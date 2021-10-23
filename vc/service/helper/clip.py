import kornia.augmentation as K
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


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
        return grad_in * (grad_in * (
            input - input.clamp(ctx.min, ctx.max)) >= 0), None, None


class Prompt(nn.Module):
    def __init__(self, torch_helper, embed, weight=1., stop=float('-inf')):
        super().__init__()
        self.torch_helper = torch_helper
        self.register_buffer('embed', embed)
        self.register_buffer('weight', torch.as_tensor(weight))
        self.register_buffer('stop', torch.as_tensor(stop))

    def forward(self, input):
        input_normed = F.normalize(input.unsqueeze(1), dim=2)
        embed_normed = F.normalize(self.embed.unsqueeze(0), dim=2)
        dists = (
            input_normed
                .sub(embed_normed)
                .norm(dim=2)
                .div(2)
                .arcsin()
                .pow(2)
                .mul(2)
        )
        dists = dists * self.weight.sign()
        return self.weight.abs() * self.torch_helper.replace_grad(
            dists,
            torch.maximum(dists, self.stop)
        ).mean()


class MakeCutouts(nn.Module):
    def __init__(self, augments, cut_size, cutn, cut_pow=1.):
        super().__init__()
        self.cut_size = cut_size
        self.cutn = cutn
        self.cut_pow = cut_pow
        self.padding = 0.5

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
                    K.RandomGaussianNoise(mean=0.0, std=1., p=0.5)
                )
            elif item == 'Pe':
                augment_list.append(
                    K.RandomPerspective(distortion_scale=0.7, p=0.7)
                )
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
                    K.RandomThinPlateSpline(
                        scale=0.3, same_on_batch=False,
                        p=0.7
                    )
                )
            elif item == 'Cr':
                augment_list.append(
                    K.RandomCrop(size=(self.cut_size, self.cut_size), p=0.5)
                )
            elif item == 'Er':
                augment_list.append(
                    K.RandomErasing(
                        (.1, .4), (.3, 1 / .3), same_on_batch=True,
                        p=0.7
                    )
                )
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
        # yoinked from https://github.com/sportsracer48/pytti
        cutouts = []
        _, _, side_x, side_y = input.shape
        max_size = min(side_x, side_y)

        paddingx = min(round(side_x * self.padding), side_x)
        paddingy = min(round(side_y * self.padding), side_y)
        input = F.pad(
            input,
            (paddingx, paddingx, paddingy, paddingy),
            mode='constant'  # 'reflect', 'replicate', 'circular', 'constant'
        )
        i = 0
        while i < self.cutn:
            size = int(
                max_size * (
                    torch
                    .zeros(1, )
                    .normal_(mean=.8, std=.3)
                    .clip(self.cut_size / max_size, 1.)
                    ** self.cut_pow
                )
            )
            offsetx_max = side_x - size + 1
            offsety_max = side_y - size + 1

            px = min(size, paddingx)
            py = min(size, paddingy)
            offsetx = (self.randc() * (offsetx_max + 2 * px) - px).floor().int()
            offsety = (self.randc() * (offsety_max + 2 * py) - py).floor().int()
            cutout = input[
                :,
                :,
                paddingx + offsetx:paddingx + offsetx + size,
                paddingy + offsety:paddingy + offsety + size,
            ]
            try:
                cutouts.append(self.av_pool(cutout))
            except:
                pass  # @todo figure out why we get this exception
            else:
                i += 1

        batch = self.augs(torch.cat(cutouts, dim=0))

        if self.noise_fac:
            facs = batch.new_empty([len(cutouts), 1, 1, 1]).uniform_(
                0,
                self.noise_fac
            )
            batch = batch + facs * torch.randn_like(batch)
        return batch

    def randc(self, min=0., max=1., mean=0.5, sd=0.5):
        return np.clip(np.random.normal(mean, sd), min, max)


class ClipHelper:
    def replace_grad(self, *args, **kwargs):
        return ReplaceGrad.apply(*args, **kwargs)

    def clamp_with_grad(self, *args, **kwargs):
        return ClampWithGrad.apply(*args, **kwargs)

    def prompt(self, embed, weight=1., stop=float('-inf')):
        return Prompt(self, embed, weight, stop)

    def make_cutouts(self, augments, cut_size, cutn, cut_pow=1.):
        return MakeCutouts(augments, cut_size, cutn, cut_pow)
