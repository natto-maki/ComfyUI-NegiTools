import glob
import os
import re

import torch
from PIL import Image
import torchvision
from torchvision.transforms import functional as TF


def _get_directory(directory):
    base_path = os.path.abspath(__file__)
    for _ in range(4):
        base_path = os.path.dirname(base_path)
    return os.path.abspath(os.path.join(base_path, directory))


class RandomImageLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"multiline": False, "default": "./input"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, directory, seed):
        directory = _get_directory(directory)
        print("RandomImageLoader: directory = %s" % directory)

        files = (glob.glob(os.path.join(directory, "*.png")) +
                 glob.glob(os.path.join(directory, "*.jpg")) +
                 glob.glob(os.path.join(directory, "*.jpeg")))

        if len(files) == 0:
            raise ValueError("Specified directory does not contain any image files")

        file = files[seed % len(files)]
        print("RandomImageLoader: load %s; in %d files" % (file, len(files)))

        im0 = Image.open(file)
        im1 = TF.to_tensor(im0.convert("RGBA"))
        im1[:3, im1[3, :, :] == 0] = 0

        images = torch.stack([im1])
        images = images.permute(0, 2, 3, 1)
        images = images[:, :, :, :3]
        return (images,)


class SaveImageToDirectory:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"multiline": False, "default": "./output"}),
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "doit"
    OUTPUT_NODE = True
    CATEGORY = "utils"

    def doit(self, directory, image):
        directory = _get_directory(directory)
        os.makedirs(directory, exist_ok=True)
        print("SaveImageToDirectory: directory = %s" % directory)

        next_index = 0
        files = glob.glob(os.path.join(directory, "out.??????.png"))
        for file in files:
            r = re.match(r"out\.(\d{6})\.png", os.path.basename(file))
            if r is None:
                continue
            next_index = max(next_index, int(r.group(1)) + 1)

        file_name = os.path.join(directory, "out.%06d.png" % next_index)
        print("SaveImageToDirectory: save to %s" % file_name)

        im0 = torchvision.transforms.functional.to_pil_image(torch.permute(image[0], (2, 0, 1)))
        im0.save(file_name)

        return (image,)
