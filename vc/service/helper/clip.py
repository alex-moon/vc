import math

import kornia.augmentation as K
import torch
from torch import nn
from torch.nn import functional as F

from vc.service.helper.diagnosis import DiagnosisHelper as dh


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
        return grad_in * (
            grad_in * (
                input - input.clamp(ctx.min, ctx.max)
            ) >= 0
        ), None, None


# based on https://github.com/sportsracer48/pytti
class MaskingPrompt(nn.Module):
    text: str = None

    def __init__(
        self,
        clip_helper,
        embed,
        weight=1.,
        stop=float('-inf'),
        ground=False,
        text=None
    ):
        super().__init__()
        self.register_buffer('embed',  embed)
        self.register_buffer('weight', torch.as_tensor(weight))
        self.register_buffer('stop',   torch.as_tensor(stop))
        self.clip_helper = clip_helper
        self.ground = ground
        self.text = text

    def forward(self, input, position, size):
        input_normed = F.normalize(input, dim=-1)
        embed_normed = F.normalize(self.embed, dim=-1)
        dists = (
            input_normed
                .sub(embed_normed)
                .norm(dim=-1)
                .div(2)
                .arcsin()
                .pow(2)
                .mul(2)
        )
        dists = dists * self.weight.sign()
        mask = self.mask(
            position,
            size,
            self.ground
        )
        dists = self.clip_helper.replace_grad(
            dists,
            torch.maximum(dists, self.stop)
        )
        weight = mask.mul(self.weight.abs())
        # dh.debug('ClipHelper', {
        #     'text': self.text,
        #     'position': position,
        #     'size': size,
        #     'mask': mask,
        #     'weight': weight,
        #     'dists': dists,
        # })
        return weight.mul(dists).mean()

    def mask(self, pos, size, ground=False):
        max = torch.as_tensor(0.707107)  # == hypot(0.5, 0.5)
        x = (pos[..., 0] + size[..., 0] * 0.5) - 0.5
        y = (pos[..., 1] + size[..., 1] * 0.5) - 0.5
        distance = torch.hypot(x, y)
        # dh.debug('ClipHelper', {
        #     'text': self.text,
        #     'distance': distance,
        #     'x': x,
        #     'y': y,
        # })
        if ground:
            return distance.div(max)
        return torch.as_tensor(1.).sub(distance.div(max)).clamp(min=0)


class Prompt(nn.Module):
    def __init__(self, clip_helper, embed, weight=1., stop=float('-inf')):
        super().__init__()
        self.clip_helper = clip_helper
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
        return self.weight.abs() * self.clip_helper.replace_grad(
            dists,
            torch.maximum(dists, self.stop)
        ).mean()


class MakeCutouts(nn.Module):
    def __init__(self, clip_helper, augments, cut_size, cutn, cut_pow=1.):
        super().__init__()
        self.cut_size = cut_size
        self.cutn = cutn
        self.cut_pow = cut_pow
        self.clip_helper = clip_helper
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

        # print(augment_list)

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
        # based on https://github.com/sportsracer48/pytti
        cutouts = []
        offsets = []
        sizes = []
        _, _, side_y, side_x = input.shape
        max_size = min(side_x, side_y)
        paddingx = min(round(side_x * self.clip_helper.padding), side_x)
        paddingy = min(round(side_y * self.clip_helper.padding), side_y)
        input = F.pad(
            input,
            (paddingx, paddingx, paddingy, paddingy),
            mode='constant'  # 'reflect', 'replicate', 'circular', 'constant'
        )

        master_offsetx_max = side_x - max_size + 1
        master_offsety_max = side_y - max_size + 1
        master_offsetx = int(0.5 * (master_offsetx_max + 2 * paddingx) - paddingx)
        master_offsety = int(0.5 * (master_offsety_max + 2 * paddingy) - paddingy)

        i = 0
        while i < self.cutn:
            if i % 2 == 0:
                size = max_size
                offsetx = master_offsetx
                offsety = master_offsety
            else:
                while True:
                    xrandc = torch.rand([])
                    yrandc = torch.rand([])
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

                    offsetx = int(xrandc * (offsetx_max + 2 * paddingx) - paddingx)
                    offsety = int(yrandc * (offsety_max + 2 * paddingy) - paddingy)
                    centerx = offsetx + size * 0.5
                    centery = offsety + size * 0.5
                    if (
                        centerx <= master_offsetx
                        or centerx >= master_offsetx + max_size
                        or centery <= master_offsety
                        or centery >= master_offsety + max_size
                    ):
                        # if center outside master cutout, let's use it
                        break

            xfrom, xto = paddingx + offsetx, paddingx + offsetx + size
            yfrom, yto = paddingy + offsety, paddingy + offsety + size

            if False and i == 0:
                dh.debug('ClipHelper', 'master cutout', {
                    'side_x': side_x,
                    'side_y': side_y,
                    'max_size': max_size,
                    'paddingx': paddingx,
                    'paddingy': paddingy,
                    'input.shape': input.shape,
                    'master_offsetx_max': master_offsetx_max,
                    'master_offsety_max': master_offsety_max,
                    'xfrom': xfrom,
                    'xto': xto,
                    'yfrom': yfrom,
                    'yto': yto,
                })

            cutout = input[:, :, yfrom:yto, xfrom:xto]

            cutouts.append(self.av_pool(cutout))
            offsets.append(torch.as_tensor(
                [[offsetx / side_x, offsety / side_y]]
            ).to(self.device))
            sizes.append(torch.as_tensor(
                [[size / side_x, size / side_y]]
            ).to(self.device))

            i += 1

        cutouts = self.augs(torch.cat(cutouts, dim=0))
        offsets = torch.cat(offsets)
        sizes = torch.cat(sizes)

        if self.noise_fac:
            facs = cutouts.new_empty(
                [len(cutouts), 1, 1, 1]
            ).uniform_(0,self.noise_fac)
            cutouts = cutouts + facs * torch.randn_like(cutouts)

        return cutouts, offsets, sizes

    # not used (get a random number with a normal distribution)
    def randc(self, min=0., max=1., mean=0.5, sd=0.5):
        return float(np.clip(np.random.normal(mean, sd), min, max))


class ClipHelper:
    padding = 0.25

    def replace_grad(self, *args, **kwargs):
        return ReplaceGrad.apply(*args, **kwargs)

    def clamp_with_grad(self, *args, **kwargs):
        return ClampWithGrad.apply(*args, **kwargs)

    def prompt(self, embed, weight=1., stop=float('-inf'), ground=False, text=None):
        return MaskingPrompt(self, embed, weight, stop, ground, text)

    def make_cutouts(self, augments, cut_size, cutn, cut_pow=1.):
        return MakeCutouts(self, augments, cut_size, cutn, cut_pow)
