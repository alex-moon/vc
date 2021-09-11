import os
import cv2
import numpy as np
import torch


def run_depth(img_name, output_path, model_path, Net, utils):
    """Run MonoDepthNN to compute depth maps.

    Args:
        output_path (str): path to output folder
        model_path (str): path to saved model
    """
    print("initialize")

    # select device
    device = torch.device("cpu")
    print("device: %s" % device)

    # load network
    model = Net(model_path)
    model.to(device)
    model.eval()

    # get input

    # create output folder
    os.makedirs(output_path, exist_ok=True)

    print("start processing", img_name)

    # input
    img = utils.read_image(img_name)
    w = img.shape[1]
    scale = 640. / max(img.shape[0], img.shape[1])
    target_height = int(round(img.shape[0] * scale))
    target_width = int(round(img.shape[1] * scale))

    img_input = utils.resize_image(img)

    print(img_input.shape)

    img_input = img_input.to(device)

    # compute
    with torch.no_grad():
        out = model.forward(img_input)

    depth = utils.resize_depth(out, target_width, target_height)
    cv2.resize(
        (img * 255).astype(np.uint8),
        (target_width, target_height),
        interpolation=cv2.INTER_AREA
    )

    filename = os.path.join(
        output_path,
        os.path.splitext(os.path.basename(img_name))[0]
    )
    np.save(filename + '.npy', depth)
    utils.write_depth(filename, depth, bits=2)

    print("finished")
