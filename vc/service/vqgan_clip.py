from datetime import datetime
import json
import math
import os
from dataclasses import dataclass, field, asdict
from typing import List
from urllib.request import urlopen
from injector import inject
from tqdm import tqdm

# @todo remove all torch imports
import torch
from torch import optim
from torch.nn import functional as F
from torchvision import transforms
from torchvision.transforms import functional as TF
from torch_optimizer import DiffGrad, AdamP, RAdam

from CLIP import clip
import numpy as np
import imageio
from PIL import ImageFile, Image, PngImagePlugin
from subprocess import Popen, PIPE
import re

from .helper.torch import TorchHelper
from .helper.vqgan import VqganHelper
from vc.service import FileService


@dataclass
class VqganClipOptions:
    prompts: str = None
    image_prompts: str = None
    max_iterations: int = 500
    display_freq: int = 50
    size: int = None
    init_image: str = None
    init_noise: str = 'pixels'
    init_weight: float = 0.
    clip_model: str = 'ViT-B/32'
    vqgan_config: str = f'checkpoints/vqgan_imagenet_f16_16384.yaml'
    vqgan_checkpoint: str = f'checkpoints/vqgan_imagenet_f16_16384.ckpt'
    noise_prompt_seeds: List[int] = field(default_factory=list)
    noise_prompt_weights: List[float] = field(default_factory=list)
    step_size: float = 0.1
    cutn: int = 32
    cut_pow: float = 1.
    seed: int = None
    optimiser: str = 'Adam'
    output: str = "output.png"
    make_video: bool = False
    cudnn_determinism: bool = False
    augments: str = None


class VqganClipService:
    file_service: FileService
    vqgan_helper: VqganHelper
    torch_helper: TorchHelper
    device = torch.device(
        'cuda' if torch.cuda.is_available() else 'cpu'
    )

    @inject
    def __init__(self, file_service: FileService):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        torch.backends.cudnn.benchmark = False
        self.vqgan_helper = VqganHelper()
        self.torch_helper = TorchHelper()
        self.file_service = file_service

    def handle(self, args: VqganClipOptions):
        print("VQGAN/CLIP starting with spec:")
        print(json.dumps(asdict(args), indent=4))

        if args.cudnn_determinism:
            torch.backends.cudnn.deterministic = True

        if not args.augments:
            args.augments = [['Af', 'Pe', 'Ji', 'Er']]

        # Split text prompts using the pipe character
        if args.prompts:
            args.prompts = [phrase.strip() for phrase in
                            args.prompts.split("|")]

        # Split target images using the pipe character
        if args.image_prompts:
            args.image_prompts = args.image_prompts.split("|")
            args.image_prompts = [image.strip() for image in args.image_prompts]
        else:
            args.image_prompts = []

        # Make video steps directory
        if args.make_video:
            if not os.path.exists('steps'):
                os.mkdir('steps')

        if args.size is None:
            args.size = [400, 400]

        # VQGAN
        model = self.vqgan_helper.load_vqgan_model(
            args.vqgan_config,
            args.vqgan_checkpoint
        ).to(self.device)

        # CLIP
        jit = True if float(torch.__version__[:3]) < 1.8 else False
        perceptor = clip.load(
            args.clip_model,
            jit=jit
        )[0].eval().requires_grad_(False).to(self.device)

        f = 2 ** (model.decoder.num_resolutions - 1)

        toksX, toksY = args.size[0] // f, args.size[1] // f
        sideX, sideY = toksX * f, toksY * f

        if self.vqgan_helper.gumbel:
            e_dim = 256
            n_toks = model.quantize.n_embed
            z_min = model.quantize.embed.weight.min(dim=0).values[None, :, None, None]
            z_max = model.quantize.embed.weight.max(dim=0).values[None, :, None, None]
        else:
            e_dim = model.quantize.e_dim
            n_toks = model.quantize.n_e
            z_min = model.quantize.embedding.weight.min(dim=0).values[None, :, None, None]
            z_max = model.quantize.embedding.weight.max(dim=0).values[None, :, None, None]

        # Image initialisation
        if args.init_image:
            if 'http' in args.init_image:
                img = Image.open(urlopen(args.init_image))
            else:
                img = Image.open(args.init_image)
            pil_image = img.convert('RGB')
            pil_image = pil_image.resize((sideX, sideY), Image.LANCZOS)
            pil_tensor = TF.to_tensor(pil_image)
            z, *_ = model.encode(pil_tensor.to(self.device).unsqueeze(0) * 2 - 1)
        elif args.init_noise == 'pixels':
            img = self.random_noise_image(args.size[0], args.size[1])
            pil_image = img.convert('RGB')
            pil_image = pil_image.resize((sideX, sideY), Image.LANCZOS)
            pil_tensor = TF.to_tensor(pil_image)
            z, *_ = model.encode(pil_tensor.to(self.device).unsqueeze(0) * 2 - 1)
        elif args.init_noise == 'gradient':
            img = self.random_gradient_image(args.size[0], args.size[1])
            pil_image = img.convert('RGB')
            pil_image = pil_image.resize((sideX, sideY), Image.LANCZOS)
            pil_tensor = TF.to_tensor(pil_image)
            z, *_ = model.encode(pil_tensor.to(self.device).unsqueeze(0) * 2 - 1)
        else:
            one_hot = F.one_hot(
                torch.randint(n_toks, [toksY * toksX], device=self.device),
                n_toks).float()
            if self.vqgan_helper.gumbel:
                z = one_hot @ model.quantize.embed.weight
            else:
                z = one_hot @ model.quantize.embedding.weight

            z = z.view([-1, toksY, toksX, e_dim]).permute(0, 3, 1, 2)

        z_orig = z.clone()
        z.requires_grad_(True)

        prompts = []

        # CLIP tokenize/encode
        for prompt in args.prompts:
            txt, weight, stop = self.parse_prompt(prompt)
            embed = perceptor.encode_text(clip.tokenize(txt).to(self.device)).float()
            prompts.append(
                self.torch_helper.prompt(embed, weight, stop).to(self.device)
            )

        for prompt in args.image_prompts:
            path, weight, stop = self.parse_prompt(prompt)
            img = Image.open(path)
            pil_image = img.convert('RGB')
            img = self.resize_image(pil_image, (sideX, sideY))
            batch = self.make_cutouts(args, perceptor, TF.to_tensor(img).unsqueeze(0).to(self.device))
            embed = perceptor.encode_image(self.normalize(batch)).float()
            prompts.append(
                self.torch_helper.prompt(embed, weight, stop).to(self.device)
            )

        for seed, weight in zip(args.noise_prompt_seeds, args.noise_prompt_weights):
            gen = torch.Generator().manual_seed(seed)
            embed = torch.empty(
                [1, perceptor.visual.output_dim]
            ).normal_(generator=gen)
            prompts.append(
                self.torch_helper.prompt(embed, weight).to(self.device)
            )

        # Set the optimiser
        if args.optimiser == "Adam":
            opt = optim.Adam([z], lr=args.step_size)  # LR=0.1 (Default)
        elif args.optimiser == "AdamW":
            opt = optim.AdamW([z], lr=args.step_size)  # LR=0.2
        elif args.optimiser == "Adagrad":
            opt = optim.Adagrad([z], lr=args.step_size)  # LR=0.5+
        elif args.optimiser == "Adamax":
            opt = optim.Adamax([z], lr=args.step_size)  # LR=0.5+?
        elif args.optimiser == "DiffGrad":
            opt = DiffGrad([z], lr=args.step_size)  # LR=2+?
        elif args.optimiser == "AdamP":
            opt = AdamP([z], lr=args.step_size)  # LR=2+?
        elif args.optimiser == "RAdam":
            opt = RAdam([z], lr=args.step_size)  # LR=2+?
        else:
            raise RuntimeError("Unknown optimiser. Are choices broken?")

        # Output for the user
        print('Using device:', self.device)
        print('Optimising using:', args.optimiser)

        if args.prompts:
            print('Using text prompts:', args.prompts)
        if args.image_prompts:
            print('Using image prompts:', args.image_prompts)
        if args.init_image:
            print('Using initial image:', args.init_image)
        if args.noise_prompt_weights:
            print('Noise prompt weights:', args.noise_prompt_weights)

        if args.seed is None:
            seed = torch.seed()
        else:
            seed = args.seed
        torch.manual_seed(seed)
        print('Using seed:', seed)

        # DO IT @todo put training in a separate Trainer class
        i = 0
        try:
            with tqdm() as pbar:
                while i < args.max_iterations:
                    self.train(
                        model,
                        perceptor,
                        args,
                        prompts,
                        opt,
                        z,
                        z_min,
                        z_max,
                        z_orig,
                        i
                    )
                    i += 1
                    pbar.update()
        except KeyboardInterrupt:
            pass

        now = datetime.now()
        self.file_service.put(args.output, '%s-%s' % (
            now.strftime('%Y-%m-%d-%H-%M-%S'),
            args.output
        ))

        # Video generation
        if args.make_video:
            init_frame = 1  # This is the frame where the video will start
            last_frame = i  # You can change i to the number of the last frame you want to generate. It will raise an error if that number of frames does not exist.

            min_fps = 10
            max_fps = 60

            total_frames = last_frame - init_frame

            length = 15  # Desired time of the video in seconds

            frames = []
            tqdm.write('Generating video...')
            for i in range(init_frame, last_frame):  #
                frames.append(Image.open("./steps/" + str(i) + '.png'))

            # fps = last_frame/10
            fps = np.clip(total_frames / length, min_fps, max_fps)
            output_file = re.compile('\.png$').sub('.mp4', args.output)
            p = Popen([
                'ffmpeg',
                '-y',
                '-f', 'image2pipe',
                '-vcodec', 'png',
                '-r', str(fps),
                '-i',
                '-',
                '-vcodec', 'libx264',
                '-r', str(fps),
                '-pix_fmt', 'yuv420p',
                '-crf', '17',
                '-preset', 'veryslow',
                '-metadata', f'comment={args.prompts}',
                output_file
            ], stdin=PIPE)
            for im in tqdm(frames):
                im.save(p.stdin, 'PNG')
            p.stdin.close()
            p.wait()
            self.file_service.put(output_file, '%s-%s' % (
                now.strftime('%Y-%m-%d-%H-%M-%S'),
                output_file
            ))

    def sinc(self, x):
        return torch.where(
            x != 0,
            torch.sin(math.pi * x) / (math.pi * x),
            x.new_ones([])
        )

    def lanczos(self, x, a):
        cond = torch.logical_and(-a < x, x < a)
        out = torch.where(cond, self.sinc(x) * self.sinc(x / a), x.new_zeros([]))
        return out / out.sum()

    def ramp(self, ratio, width):
        n = math.ceil(width / ratio + 1)
        out = torch.empty([n])
        cur = 0
        for i in range(out.shape[0]):
            out[i] = cur
            cur += ratio
        return torch.cat([-out[1:].flip([0]), out])[1:-1]

    def random_noise_image(self, w, h):
        random_image = Image.fromarray(
            np.random.randint(0, 255, (w, h, 3), dtype=np.dtype('uint8'))
        )
        return random_image

    def gradient_2d(self, start, stop, width, height, is_horizontal):
        if is_horizontal:
            return np.tile(np.linspace(start, stop, width), (height, 1))
        else:
            return np.tile(np.linspace(start, stop, height), (width, 1)).T

    def gradient_3d(self, width, height, start_list, stop_list, is_horizontal_list):
        result = np.zeros((height, width, len(start_list)), dtype=float)

        for i, (start, stop, is_horizontal) in enumerate(
            zip(start_list, stop_list, is_horizontal_list)):
            result[:, :, i] = self.gradient_2d(start, stop, width, height, is_horizontal)

        return result

    def random_gradient_image(self, w, h):
        array = self.gradient_3d(w, h, (0, 0, np.random.randint(0, 255)), (
        np.random.randint(1, 255), np.random.randint(2, 255),
        np.random.randint(3, 128)), (True, False, False))
        random_image = Image.fromarray(np.uint8(array))
        return random_image

    def normalize(self, batch):
        return transforms.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711]
        )(batch)

    def make_cutouts(self, args, perceptor, batch):
        return self.torch_helper.make_cutouts(
            args.augments,
            perceptor.visual.input_resolution,
            args.cutn,
            cut_pow=args.cut_pow
        )(batch)

    def vector_quantize(self, x, codebook):
        d = x.pow(2).sum(dim=-1, keepdim=True) + codebook.pow(2).sum(dim=1) - 2 * x @ codebook.T
        indices = d.argmin(-1)
        x_q = F.one_hot(indices, codebook.shape[0]).to(d.dtype) @ codebook
        return self.torch_helper.replace_grad(x_q, x)

    def parse_prompt(self, prompt):
        vals = prompt.rsplit(':', 2)
        vals = vals + ['', '1', '-inf'][len(vals):]
        return vals[0], float(vals[1]), float(vals[2])

    def resize_image(self, image, out_size):
        ratio = image.size[0] / image.size[1]
        area = min(image.size[0] * image.size[1], out_size[0] * out_size[1])
        size = round((area * ratio)**0.5), round((area / ratio)**0.5)
        return image.resize(size, Image.LANCZOS)

    def synth(self, model, z):
        if self.vqgan_helper.gumbel:
            z_q = self.vector_quantize(
                z.movedim(1, 3),
                model.quantize.embed.weight
            ).movedim(3, 1)
        else:
            z_q = self.vector_quantize(
                z.movedim(1, 3),
                model.quantize.embedding.weight
            ).movedim(3, 1)
        return self.torch_helper.clamp_with_grad(
            model.decode(z_q).add(1).div(2),
            0,
            1
        )

    @torch.no_grad()
    def checkin(self, model, z, prompts, output, i, losses):
        losses_str = ', '.join(f'{loss.item():g}' for loss in losses)
        tqdm.write(f'i: {i}, loss: {sum(losses).item():g}, losses: {losses_str}')
        out = self.synth(model, z)
        info = PngImagePlugin.PngInfo()
        info.add_text('comment', f'{prompts}')
        TF.to_pil_image(out[0].cpu()).save(output, pnginfo=info)

    def ascend_txt(self, model, perceptor, args, prompts, z_orig, z, i):
        out = self.synth(model, z)
        iii = perceptor.encode_image(
            self.normalize(
                self.make_cutouts(
                    args,
                    perceptor,
                    out
                )
            )
        ).float()

        result = []

        if args.init_weight:
            # result.append(F.mse_loss(z, z_orig) * args.init_weight / 2)
            result.append(F.mse_loss(
                z,
                torch.zeros_like(z_orig)
            ) * (
                (1 / torch.tensor(i * 2 + 1)) * args.init_weight
            ) / 2)

        for prompt in prompts:
            result.append(prompt(iii))

        if args.make_video:
            img = np.array(
                out.mul(255).clamp(0, 255)[0].cpu().detach().numpy().astype(
                    np.uint8))[:, :, :]
            img = np.transpose(img, (1, 2, 0))
            imageio.imwrite('./steps/' + str(i) + '.png', np.array(img))

        return result

    def train(self, model, perceptor, args, prompts, opt, z, z_min, z_max, z_orig, i):
        opt.zero_grad(set_to_none=True)
        loss_all = self.ascend_txt(model, perceptor, args, prompts, z_orig, z, i)

        if i % args.display_freq == 0:
            self.checkin(model, z, args.prompts, args.output, i, loss_all)

        loss = sum(loss_all)
        loss.backward()
        opt.step()

        with torch.no_grad():
            z.copy_(z.maximum(z_min).minimum(z_max))
