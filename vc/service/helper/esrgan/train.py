# flake8: noqa
import os.path as osp
from basicsr.train import train_pipeline

import vc.service.helper.esrgan.archs
import vc.service.helper.esrgan.data
import vc.service.helper.esrgan.models

if __name__ == '__main__':
    root_path = osp.abspath(osp.join(__file__, osp.pardir, osp.pardir))
    train_pipeline(root_path)
