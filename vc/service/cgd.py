import json
from dataclasses import asdict
from dataclasses import dataclass
from typing import Optional, List

import lpips
import torch
from PIL import Image
from injector import inject
from torchvision import transforms
from torchvision.transforms import functional as TF
from tqdm.notebook import tqdm

from CLIP import clip
from vc.service.file import FileService
from vc.service.helper.cgd import (
    SecondaryDiffusionImageNet,
    SecondaryDiffusionImageNet2, alpha_sigma_to_t, spherical_dist_loss, tv_loss,
    range_loss,
)
from vc.service.helper.clip import ClipHelper
from vc.service.helper.diagnosis import DiagnosisHelper as dh
from vc.service.helper.dimensions import DimensionsHelper
from vc.service.helper.guided_diffusion.script_util import (
    model_and_diffusion_defaults,
    create_model_and_diffusion,
)


@dataclass
class CgdOptions:
    prompts: str = None
    image_prompts: str = None
    output_filename: str = 'output.png'
    init_image: Optional[str] = 'output.png'
    max_iterations: int = 500
    size: List[int] = None
    batch_size = 1
    clip_guidance_scale = 1000  # Controls how much the image should look like the prompt.
    tv_scale = 0  # Controls the smoothness of the final output.
    range_scale = 0  # Controls how far out of range RGB values are allowed to be.
    cutn = 16
    cut_pow = 1.0
    skip_timesteps = 0  # This needs to be between approx. 200 and 500 when using an init image.
    init_scale = 0  # This enhances the effect of the init image, a good value is 1000.
    seed = 0


class CgdService:
    USE_V1 = False

    file_service: FileService
    clip_helper: ClipHelper
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @inject
    def __init__(self, file_service: FileService):
        self.clip_helper = ClipHelper()
        self.file_service = file_service

    def handle(self, args: CgdOptions):
        dh.debug('CgdService', json.dumps(asdict(args), indent=4))

        model_config = model_and_diffusion_defaults()
        model_config.update({
            'attention_resolutions': '32, 16, 8',
            'class_cond': False,
            'diffusion_steps': 1000,
            'rescale_timesteps': True,
            'timestep_respacing': str(args.max_iterations),
            'image_size': 256,
            'learn_sigma': True,
            'noise_schedule': 'linear',
            'num_channels': 256,
            'num_head_channels': 64,
            'num_res_blocks': 2,
            'resblock_updown': True,
            'use_checkpoint': False,
            'use_fp16': True,
            'use_scale_shift_norm': True,
        })

        # Load models
        dh.debug('Using device:', self.device)

        model, diffusion = create_model_and_diffusion(**model_config)
        model.load_state_dict(torch.load(
            'checkpoints/256x256_diffusion_uncond.pt',
            map_location='cpu'
        ))
        model.requires_grad_(False).eval().to(self.device)
        if model_config['use_fp16']:
            model.convert_to_fp16()

        if CgdService.USE_V1:
            secondary_model = SecondaryDiffusionImageNet()
            secondary_model.load_state_dict(torch.load(
                'checkpoints/secondary_model_imagenet.pth',
                map_location='cpu'
            ))
        else:
            secondary_model = SecondaryDiffusionImageNet2()
            secondary_model.load_state_dict(torch.load(
                'checkpoints/secondary_model_imagenet_2.pth',
                map_location='cpu'
            ))

        secondary_model.eval().requires_grad_(False).to(self.device)

        clip_model = (
            clip.load('ViT-B/16', jit=False)[0]
                .eval()
                .requires_grad_(False)
                .to(self.device)
        )
        clip_size = clip_model.visual.input_resolution
        normalize = transforms.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711]
        )
        lpips_model = lpips.LPIPS(net='vgg').to(self.device)

        if args.seed is not None:
            torch.manual_seed(args.seed)

        make_cutouts = self.clip_helper.make_cutouts(
            [],
            clip_size,
            args.cutn,
            args.cut_pow
        )
        target_embeds, weights = [], []

        # Split text prompts using the pipe character
        if args.prompts:
            args.prompts = [
                phrase.strip()
                for phrase
                in args.prompts.split("|")
            ]

        # Split target images using the pipe character
        if args.image_prompts:
            args.image_prompts = args.image_prompts.split("|")
            args.image_prompts = [image.strip() for image in args.image_prompts]
        else:
            args.image_prompts = []

        if args.size is None:
            args.size = [
                DimensionsHelper.width_small(),
                DimensionsHelper.height_small(),
            ]

        side_x, side_y = args.size

        for prompt in args.prompts:
            txt, weight, stop = self.parse_prompt(prompt)
            target_embeds.append(
                clip_model.encode_text(
                    clip.tokenize(txt).to(self.device)
                ).float()
            )
            weights.append(weight)

        for prompt in args.image_prompts:
            path, weight, stop = self.parse_prompt(prompt)
            img = Image.open(path).convert('RGB')
            img = TF.resize(
                img,
                min(side_x, side_y, *img.size),
                transforms.InterpolationMode.LANCZOS
            )
            cutouts, offsets, sizes = make_cutouts(TF.to_tensor(img).unsqueeze(0).to(self.device))
            embed = clip_model.encode_image(normalize(cutouts)).float()
            target_embeds.append(embed)
            weights.extend([weight / args.cutn] * args.cutn)

        target_embeds = torch.cat(target_embeds)
        weights = torch.tensor(weights, device=self.device)
        if weights.sum().abs() < 1e-3:
            raise RuntimeError('The weights must not sum to 0.')
        weights /= weights.sum().abs()

        init = None
        if args.init_image is not None:
            init = Image.open(args.init_image).convert('RGB')
            init = init.resize((side_x, side_y), Image.LANCZOS)
            init = TF.to_tensor(init).to(self.device).unsqueeze(0).mul(2).sub(1)

        cur_t = None

        def cond_fn(x, t, y=None):
            with torch.enable_grad():
                x = x.detach().requires_grad_()
                n = x.shape[0]
                alpha = torch.tensor(
                    diffusion.sqrt_alphas_cumprod[cur_t],
                    device=self.device,
                    dtype=torch.float32
                )
                sigma = torch.tensor(
                    diffusion.sqrt_one_minus_alphas_cumprod[cur_t],
                    device=self.device,
                    dtype=torch.float32
                )
                cosine_t = alpha_sigma_to_t(alpha, sigma)
                pred = secondary_model(x, cosine_t[None].repeat([n])).pred
                batch, _, _ = make_cutouts(pred.add(1).div(2))
                image_embeds = clip_model.encode_image(normalize(batch)).float()
                dists = spherical_dist_loss(
                    image_embeds.unsqueeze(1),
                    target_embeds.unsqueeze(0)
                )
                dists = dists.view([args.cutn, n, -1])
                clip_losses = dists.mul(weights).sum(2).mean(0)
                tv_losses = tv_loss(pred)
                range_losses = range_loss(pred)
                loss = (
                    clip_losses.sum() * args.clip_guidance_scale
                    + tv_losses.sum() * args.tv_scale
                    + range_losses.sum() * args.range_scale
                )
                if init is not None and args.init_scale:
                    init_losses = lpips_model(pred, init)
                    loss = loss + init_losses.sum() * args.init_scale
                grad = -torch.autograd.grad(loss, x)[0]
                return grad

        if model_config['timestep_respacing'].startswith('ddim'):
            sample_fn = diffusion.ddim_sample_loop_progressive
        else:
            sample_fn = diffusion.p_sample_loop_progressive

        cur_t = diffusion.num_timesteps - args.skip_timesteps - 1

        samples = sample_fn(
            model,
            (args.batch_size, 3, side_y, side_x),
            clip_denoised=False,
            model_kwargs={},
            cond_fn=cond_fn,
            progress=True,
            skip_timesteps=args.skip_timesteps,
            init_image=init,
            randomize_class=True,
        )

        image = None
        for j, sample in enumerate(samples):
            if j % 100 == 0 or cur_t == 0:
                tqdm.write(f'Step {j}')
            image = sample['pred_xstart'][0]

        dh.debug('CgdService', 'writing image', args.output_filename)
        TF.to_pil_image(image.add(1).div(2).clamp(0, 1)).save(args.output_filename)

    def parse_prompt(self, prompt):
        vals = prompt.rsplit(':', 2)
        vals = vals + ['', '1', '-inf'][len(vals):]
        return vals[0], float(vals[1]), float(vals[2])
