import os
import subprocess
import importlib

import numpy as np
import torch
import torchvision
from PIL import Image


_dependency_dir = "dependencies"
_repository_name = "stable-diffusion-webui-depthmap-script"


class StereoImageGenerator:
    def __check_environment(self):
        if not os.path.isdir(os.path.join(self.dep_dir, _repository_name)):
            r0 = subprocess.run([
                "git", "clone", "https://github.com/thygate/stable-diffusion-webui-depthmap-script.git"
            ], cwd=self.dep_dir)
            if r0.returncode != 0:
                subprocess.run(["rm", "-rf", _repository_name], cwd=self.dep_dir)
                raise RuntimeError("Marigold repository not found or connection error")

    def __init__(self):
        self.dep_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), _dependency_dir)
        os.makedirs(self.dep_dir, exist_ok=True)
        self.rep_dir = os.path.join(self.dep_dir, _repository_name)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "depth_image": ("IMAGE",),
                "divergence": ("FLOAT", {
                    "default": 5.0, "min": 0.05, "max": 10.0, "step": 0.01, "round": 0.001, "display": "slider"
                }),
                "stereo_offset_exponent": ("FLOAT", {
                    "default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1, "round": 0.01, "display": "slider"
                }),
                "fill_technique": ([
                    "polylines_sharp", "polylines_soft", "naive", "naive_interpolating", "none"
                ],),
                "output_mode": ([
                    "L-R", "R-L", "L-R-L",
                ],),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("STEREO_IMAGE", "IMAGE_L", "IMAGE_R")
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "Generator"

    from .noise_image_generator import NoiseImageGenerator

    def doit(self, image, depth_image, divergence, stereo_offset_exponent, fill_technique, output_mode):
        self.__check_environment()
        m = importlib.import_module(
            "." + ".".join([_dependency_dir, _repository_name, "src", "stereoimage_generation"]),
            ".".join(__name__.split(".")[:-2]))

        xw = image.shape[2]
        yw = image.shape[1]
        image = torchvision.transforms.functional.to_pil_image(torch.permute(image[0], (2, 0, 1)))

        depth_map = depth_image.to('cpu').detach().numpy()[0, :, :, 0]
        depth_min = np.min(depth_map)
        depth_max = np.max(depth_map)
        if depth_max == depth_min:
            depth_max = depth_min + 1.0
        depth_map = (depth_map - depth_min) * (1.0 / (depth_max - depth_min))
        depth_map = 1.0 - depth_map

        modes = ["left-only", "only-right"]
        if output_mode == "L-R":
            modes.append("left-right")
        elif output_mode == "R-L":
            modes.append("right-left")
        elif output_mode == "L-R-L":
            pass
        else:
            raise ValueError()

        images = m.create_stereoimages(
            image, depth_map, divergence, modes=modes,
            stereo_offset_exponent=stereo_offset_exponent, fill_technique=fill_technique)

        if output_mode == "L-R-L":
            out_image = Image.new("RGB", (xw * 3, yw))
            out_image.paste(images[0], (0, 0))
            out_image.paste(images[1], (xw, 0))
            out_image.paste(images[0], (xw * 2, 0))
            images.append(out_image)

        return (
            torch.from_numpy(np.expand_dims(np.array(images[2]) * (1.0 / 255), axis=0)),
            torch.from_numpy(np.expand_dims(np.array(images[0]) * (1.0 / 255), axis=0)),
            torch.from_numpy(np.expand_dims(np.array(images[1]) * (1.0 / 255), axis=0)),
        )
