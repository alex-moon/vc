import math
import os
import sys
from dataclasses import dataclass, field
# from email.policy import default
from urllib.request import urlopen
from injector import inject
from typing import List
from tqdm import tqdm

# pip install taming-transformers works with Gumbel, but does not work with coco etc
# appending the path works with Gumbel, but gives ModuleNotFoundError: No module named 'transformers' for coco etc
sys.path.append('taming-transformers')

from omegaconf import OmegaConf
from taming.models import cond_transformer, vqgan
#import taming.modules

import torch
from torch import nn, optim
from torch.nn import functional as F
from torchvision import transforms
from torchvision.transforms import functional as TF

torch.backends.cudnn.benchmark = False		# NR: True is a bit faster, but can lead to OOM. False is more deterministic.
#torch.use_deterministic_algorithms(True)	# NR: grid_sampler_2d_backward_cuda does not have a deterministic implementation

from torch_optimizer import DiffGrad, AdamP, RAdam

from CLIP import clip
import kornia.augmentation as K
import numpy as np
import imageio

from PIL import ImageFile, Image, PngImagePlugin
ImageFile.LOAD_TRUNCATED_IMAGES = True

from subprocess import Popen, PIPE
import re


class ReplaceGrad(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x_forward, x_backward):
        ctx.shape = x_backward.shape
        return x_forward

    @staticmethod
    def backward(ctx, grad_in):
        return None, grad_in.sum_to_size(ctx.shape)


class ClampWithGrad(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input, min, max):
        ctx.min = min
        ctx.max = max
        ctx.save_for_backward(input)
        return input.clamp(min, max)

    @staticmethod
    def backward(ctx, grad_in):
        input, = ctx.saved_tensors
        return grad_in * (grad_in * (input - input.clamp(ctx.min, ctx.max)) >= 0), None, None


class Prompt(nn.Module):
    def __init__(self, embed, weight=1., stop=float('-inf')):
        super().__init__()
        self.register_buffer('embed', embed)
        self.register_buffer('weight', torch.as_tensor(weight))
        self.register_buffer('stop', torch.as_tensor(stop))

    def forward(self, input):
        input_normed = F.normalize(input.unsqueeze(1), dim=2)
        embed_normed = F.normalize(self.embed.unsqueeze(0), dim=2)
        dists = input_normed.sub(embed_normed).norm(dim=2).div(2).arcsin().pow(2).mul(2)
        dists = dists * self.weight.sign()
        return self.weight.abs() * self.replace_grad(dists, torch.maximum(dists, self.stop)).mean()


class MakeCutouts(nn.Module):
    def __init__(self, augments, cut_size, cutn, cut_pow=1.):
        super().__init__()
        self.cut_size = cut_size
        self.cutn = cutn
        self.cut_pow = cut_pow

        # Pick your own augments & their order
        augment_list = []
        for item in augments[0]:
            if item == 'Ji':
                augment_list.append(
                    K.ColorJitter(
                        brightness=0.1,
                        contrast=0.1,
                        saturation=0.05,
                        hue=0.05,
                        p=0.5
                    )
                )
            elif item == 'Sh':
                augment_list.append(K.RandomSharpness(sharpness=0.4, p=0.7))
            elif item == 'Gn':
                augment_list.append(
                    K.RandomGaussianNoise(mean=0.0, std=1., p=0.5))
            elif item == 'Pe':
                augment_list.append(
                    K.RandomPerspective(distortion_scale=0.7, p=0.7))
            elif item == 'Ro':
                augment_list.append(K.RandomRotation(degrees=15, p=0.7))
            elif item == 'Af':
                augment_list.append(
                    K.RandomAffine(
                        degrees=15,
                        translate=0.1,
                        p=0.7,
                        padding_mode='border'
                    )
                )
            elif item == 'Et':
                augment_list.append(K.RandomElasticTransform(p=0.7))
            elif item == 'Ts':
                augment_list.append(
                    K.RandomThinPlateSpline(scale=0.3, same_on_batch=False,
                                            p=0.7))
            elif item == 'Cr':
                augment_list.append(
                    K.RandomCrop(size=(self.cut_size, self.cut_size), p=0.5))
            elif item == 'Er':
                augment_list.append(
                    K.RandomErasing((.1, .4), (.3, 1 / .3), same_on_batch=True,
                                    p=0.7))
            elif item == 'Re':
                augment_list.append(
                    K.RandomResizedCrop(
                        size=(self.cut_size, self.cut_size),
                        scale=(0.1, 1),
                        ratio=(0.75, 1.333),
                        cropping_mode='resample',
                        p=0.5
                    )
                )

        print(augment_list)

        self.augs = nn.Sequential(*augment_list)

        '''
        self.augs = nn.Sequential(
            # Original:
            # K.RandomHorizontalFlip(p=0.5),
            # K.RandomVerticalFlip(p=0.5),
            # K.RandomSolarize(0.01, 0.01, p=0.7),
            # K.RandomSharpness(0.3,p=0.4),
            # K.RandomResizedCrop(size=(self.cut_size,self.cut_size), scale=(0.1,1),  ratio=(0.75,1.333), cropping_mode='resample', p=0.5),
            # K.RandomCrop(size=(self.cut_size,self.cut_size), p=0.5), 

            # Updated colab:
            K.RandomAffine(degrees=15, translate=0.1, p=0.7, padding_mode='border'),
            K.RandomPerspective(0.7,p=0.7),
            K.ColorJitter(hue=0.1, saturation=0.1, p=0.7),
            K.RandomErasing((.1, .4), (.3, 1/.3), same_on_batch=True, p=0.7),        
            )
        '''

        self.noise_fac = 0.1
        # self.noise_fac = False

        # Pooling
        self.av_pool = nn.AdaptiveAvgPool2d((self.cut_size, self.cut_size))
        self.max_pool = nn.AdaptiveMaxPool2d((self.cut_size, self.cut_size))

    def forward(self, input):
        # sideY, sideX = input.shape[2:4]
        # max_size = min(sideX, sideY)
        # min_size = min(sideX, sideY, self.cut_size)
        cutouts = []

        for _ in range(self.cutn):
            # size = int(torch.rand([])**self.cut_pow * (max_size - min_size) + min_size)
            # offsetx = torch.randint(0, sideX - size + 1, ())
            # offsety = torch.randint(0, sideY - size + 1, ())
            # cutout = input[:, :, offsety:offsety + size, offsetx:offsetx + size]
            # cutouts.append(resample(cutout, (self.cut_size, self.cut_size)))
            # cutout = transforms.Resize(size=(self.cut_size, self.cut_size))(input)

            # Use Pooling
            cutout = (self.av_pool(input) + self.max_pool(input)) / 2
            cutouts.append(cutout)

        batch = self.augs(torch.cat(cutouts, dim=0))

        if self.noise_fac:
            facs = batch.new_empty([self.cutn, 1, 1, 1]).uniform_(0,
                                                                  self.noise_fac)
            batch = batch + facs * torch.randn_like(batch)
        return batch


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
    @inject
    def __init__(self):
        pass

    def handle(self, args: VqganClipOptions):
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

        # Make video steps directory
        if args.make_video:
            if not os.path.exists('steps'):
                os.mkdir('steps')

        if args.size is None:
            args.size = [400, 400]

        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        model = self.load_vqgan_model(
            args.vqgan_config,
            args.vqgan_checkpoint
        ).to(device)
        jit = True if float(torch.__version__[:3]) < 1.8 else False
        perceptor = clip.load(
            args.clip_model,
            jit=jit
        )[0].eval().requires_grad_(False).to(device)

        # clock=deepcopy(perceptor.visual.positional_embedding.data)
        # perceptor.visual.positional_embedding.data = clock/clock.max()
        # perceptor.visual.positional_embedding.data=clamp_with_grad(clock,0,1)

        f = 2 ** (model.decoder.num_resolutions - 1)

        toksX, toksY = args.size[0] // f, args.size[1] // f
        sideX, sideY = toksX * f, toksY * f

        if gumbel:
            e_dim = 256
            n_toks = model.quantize.n_embed
            z_min = model.quantize.embed.weight.min(dim=0).values[None, :, None, None]
            z_max = model.quantize.embed.weight.max(dim=0).values[None, :, None, None]
        else:
            e_dim = model.quantize.e_dim
            n_toks = model.quantize.n_e
            z_min = model.quantize.embedding.weight.min(dim=0).values[None, :, None, None]
            z_max = model.quantize.embedding.weight.max(dim=0).values[None, :, None, None]

        # z_min = model.quantize.embedding.weight.min(dim=0).values[None, :, None, None]
        # z_max = model.quantize.embedding.weight.max(dim=0).values[None, :, None, None]

        # normalize_imagenet = transforms.Normalize(mean=[0.485, 0.456, 0.406],
        #                                            std=[0.229, 0.224, 0.225])

        # Image initialisation
        if args.init_image:
            if 'http' in args.init_image:
                img = Image.open(urlopen(args.init_image))
            else:
                img = Image.open(args.init_image)
            pil_image = img.convert('RGB')
            pil_image = pil_image.resize((sideX, sideY), Image.LANCZOS)
            pil_tensor = TF.to_tensor(pil_image)
            z, *_ = model.encode(pil_tensor.to(device).unsqueeze(0) * 2 - 1)
        elif args.init_noise == 'pixels':
            img = self.random_noise_image(args.size[0], args.size[1])
            pil_image = img.convert('RGB')
            pil_image = pil_image.resize((sideX, sideY), Image.LANCZOS)
            pil_tensor = TF.to_tensor(pil_image)
            z, *_ = model.encode(pil_tensor.to(device).unsqueeze(0) * 2 - 1)
        elif args.init_noise == 'gradient':
            img = self.random_gradient_image(args.size[0], args.size[1])
            pil_image = img.convert('RGB')
            pil_image = pil_image.resize((sideX, sideY), Image.LANCZOS)
            pil_tensor = TF.to_tensor(pil_image)
            z, *_ = model.encode(pil_tensor.to(device).unsqueeze(0) * 2 - 1)
        else:
            one_hot = F.one_hot(
                torch.randint(n_toks, [toksY * toksX], device=device),
                n_toks).float()
            # z = one_hot @ model.quantize.embedding.weight
            if gumbel:
                z = one_hot @ model.quantize.embed.weight
            else:
                z = one_hot @ model.quantize.embedding.weight

            z = z.view([-1, toksY, toksX, e_dim]).permute(0, 3, 1, 2)
            # z = torch.rand_like(z)*2						# NR: check

        z_orig = z.clone()
        z.requires_grad_(True)

        pms = []

        # CLIP tokenize/encode
        # NR: Add alternate method
        for prompt in args.prompts:
            txt, weight, stop = self.parse_prompt(prompt)
            embed = perceptor.encode_text(clip.tokenize(txt).to(device)).float()
            pms.append(Prompt(embed, weight, stop).to(device))

        for prompt in args.image_prompts:
            path, weight, stop = self.parse_prompt(prompt)
            img = Image.open(path)
            pil_image = img.convert('RGB')
            img = self.resize_image(pil_image, (sideX, sideY))
            batch = self.make_cutouts(args, perceptor, TF.to_tensor(img).unsqueeze(0).to(device))
            embed = perceptor.encode_image(self.normalize(batch)).float()
            pms.append(Prompt(embed, weight, stop).to(device))

        for seed, weight in zip(args.noise_prompt_seeds, args.noise_prompt_weights):
            gen = torch.Generator().manual_seed(seed)
            embed = torch.empty([1, perceptor.visual.output_dim]).normal_(
                generator=gen)
            pms.append(Prompt(embed, weight).to(device))

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
        print('Using device:', device)
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

        i = 0
        try:
            with tqdm() as pbar:
                while True:
                    self.train(
                        model,
                        perceptor,
                        args,
                        pms,
                        opt,
                        z,
                        z_min,
                        z_max,
                        z_orig,
                        i
                    )
                    if i == args.max_iterations:
                        break
                    i += 1
                    pbar.update()
        except KeyboardInterrupt:
            pass

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

    # NR: Testing with different intital images
    def random_noise_image(self, w, h):
        random_image = Image.fromarray(
            np.random.randint(0, 255, (w, h, 3), dtype=np.dtype('uint8')))
        return random_image

    # create initial gradient image
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

    # Not used?
    def resample(self, input, size, align_corners=True):
        n, c, h, w = input.shape
        dh, dw = size

        input = input.view([n * c, 1, h, w])

        if dh < h:
            kernel_h = self.lanczos(self.ramp(dh / h, 2), 2).to(input.device, input.dtype)
            pad_h = (kernel_h.shape[0] - 1) // 2
            input = F.pad(input, (0, 0, pad_h, pad_h), 'reflect')
            input = F.conv2d(input, kernel_h[None, None, :, None])

        if dw < w:
            kernel_w = self.lanczos(self.ramp(dw / w, 2), 2).to(input.device, input.dtype)
            pad_w = (kernel_w.shape[0] - 1) // 2
            input = F.pad(input, (pad_w, pad_w, 0, 0), 'reflect')
            input = F.conv2d(input, kernel_w[None, None, None, :])

        input = input.view([n, c, h, w])
        return F.interpolate(
            input,
            size,
            mode='bicubic',
            align_corners=align_corners
        )

    def replace_grad(self, *args, **kwargs):
        return ReplaceGrad.apply(*args, **kwargs)

    def clamp_with_grad(self, *args, **kwargs):
        return ClampWithGrad.apply(*args, **kwargs)

    def normalize(self, *args, **kwargs):
        return transforms.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711]
        )(*args, **kwargs)

    def make_cutouts(self, opts, perceptor, *args, **kwargs):
        return MakeCutouts(
            opts.augments,
            perceptor.visual.input_resolution,
            opts.cutn,
            cut_pow=opts.cut_pow
        )(*args, **kwargs)

    def vector_quantize(self, x, codebook):
        d = x.pow(2).sum(dim=-1, keepdim=True) + codebook.pow(2).sum(dim=1) - 2 * x @ codebook.T
        indices = d.argmin(-1)
        x_q = F.one_hot(indices, codebook.shape[0]).to(d.dtype) @ codebook
        return self.replace_grad(x_q, x)

    def parse_prompt(self, prompt):
        vals = prompt.rsplit(':', 2)
        vals = vals + ['', '1', '-inf'][len(vals):]
        return vals[0], float(vals[1]), float(vals[2])

    def load_vqgan_model(self, config_path, checkpoint_path):
        global gumbel
        gumbel = False
        config = OmegaConf.load(config_path)
        if config.model.target == 'taming.models.vqgan.VQModel':
            model = vqgan.VQModel(**config.model.params)
            model.eval().requires_grad_(False)
            model.init_from_ckpt(checkpoint_path)
        elif config.model.target == 'taming.models.vqgan.GumbelVQ':
            model = vqgan.GumbelVQ(**config.model.params)
            model.eval().requires_grad_(False)
            model.init_from_ckpt(checkpoint_path)
            gumbel = True
        elif config.model.target == 'taming.models.cond_transformer.Net2NetTransformer':
            parent_model = cond_transformer.Net2NetTransformer(**config.model.params)
            parent_model.eval().requires_grad_(False)
            parent_model.init_from_ckpt(checkpoint_path)
            model = parent_model.first_stage_model
        else:
            raise ValueError(f'unknown model type: {config.model.target}')
        del model.loss
        return model

    def resize_image(self, image, out_size):
        ratio = image.size[0] / image.size[1]
        area = min(image.size[0] * image.size[1], out_size[0] * out_size[1])
        size = round((area * ratio)**0.5), round((area / ratio)**0.5)
        return image.resize(size, Image.LANCZOS)

    def synth(self, model, z):
        if gumbel:
            z_q = self.vector_quantize(
                z.movedim(1, 3),
                model.quantize.embed.weight
            ).movedim(3, 1)
        else:
            z_q = self.vector_quantize(
                z.movedim(1, 3),
                model.quantize.embedding.weight
            ).movedim(3, 1)
        return self.clamp_with_grad(model.decode(z_q).add(1).div(2), 0, 1)

    @torch.no_grad()
    def checkin(self, model, z, prompts, output, i, losses):
        losses_str = ', '.join(f'{loss.item():g}' for loss in losses)
        tqdm.write(f'i: {i}, loss: {sum(losses).item():g}, losses: {losses_str}')
        out = self.synth(model, z)
        info = PngImagePlugin.PngInfo()
        info.add_text('comment', f'{prompts}')
        TF.to_pil_image(out[0].cpu()).save(output, pnginfo=info)

    def ascend_txt(self, model, perceptor, args, pms, z_orig, z):
        global i
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
            result.append(F.mse_loss(z, torch.zeros_like(z_orig)) * (
                    (1 / torch.tensor(i * 2 + 1)) * args.init_weight) / 2)

        for prompt in pms:
            result.append(prompt(iii))

        if args.make_video:
            img = np.array(
                out.mul(255).clamp(0, 255)[0].cpu().detach().numpy().astype(
                    np.uint8))[:, :, :]
            img = np.transpose(img, (1, 2, 0))
            imageio.imwrite('./steps/' + str(i) + '.png', np.array(img))

        return result

    def train(self, model, perceptor, args, pms, opt, z, z_min, z_max, z_orig, i):
        opt.zero_grad(set_to_none=True)
        loss_all = self.ascend_txt(model, perceptor, args, pms, z_orig, z)

        if i % args.display_freq == 0:
            self.checkin(model, z, args.prompts, args.output, i, loss_all)

        loss = sum(loss_all)
        loss.backward()
        opt.step()

        with torch.no_grad():
            z.copy_(z.maximum(z_min).minimum(z_max))
