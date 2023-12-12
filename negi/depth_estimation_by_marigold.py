import os
import sys
import subprocess

import numpy as np
import torch
import torchvision


_dependency_dir = "dependencies"

_install_script = '''\
source venv/marigold/bin/activate
pip install -r requirements.txt
bash script/download_weights.sh
'''

_infer_script = '''\
source venv/marigold/bin/activate
python run.py --n_infer %(infer_passes)d --denoise_steps %(denoise_steps)d --seed %(seed)d --input_rgb_dir "%(input_dir_name)s" --output_dir "%(output_dir_name)s"
'''


class DepthEstimationByMarigold:
    def __init__(self):
        dep_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), _dependency_dir)
        os.makedirs(dep_dir, exist_ok=True)

        self.rep_dir = os.path.join(dep_dir, "Marigold")

        if (not os.path.isdir(os.path.join(dep_dir, "Marigold")) or
                not os.path.isfile(os.path.join(self.rep_dir, "installed"))):

            r0 = subprocess.run(["git", "clone", "https://github.com/prs-eth/Marigold.git"], cwd=dep_dir)
            if r0.returncode != 0:
                subprocess.run(["rm", "-rf", "Marigold"], cwd=dep_dir)
                raise RuntimeError("Marigold repository not found or connection error")

            # Make sure that venv has been created correctly.
            # Because if you ignore the error, the ComfyUI runtime environment package will be incorrectly overwritten.
            subprocess.run([sys.executable, "-m", "venv", "venv/marigold"], cwd=self.rep_dir)
            if not os.path.isfile(os.path.join(self.rep_dir, "venv", "marigold", "bin", "activate")):
                raise RuntimeError("Failed to setup venv for Marigold")

            with open(os.path.join(self.rep_dir, "install.sh"), "wt") as f:
                f.write(_install_script)
            # TODO pick errors
            subprocess.run(["bash", "install.sh"], cwd=self.rep_dir)
            with open(os.path.join(self.rep_dir, "installed"), "wt") as f:
                f.write("installed")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "infer_passes": ("INT", {"default": 10, "min": 1, "max": 40, "step": 1, "display": "number"}),
                "denoise_steps": ("INT", {"default": 10, "min": 1, "max": 40, "step": 1, "display": "number"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffff}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("DEPTH_IMAGE",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, image, infer_passes, denoise_steps, seed):
        work_dir = os.path.join(self.rep_dir, "work")
        os.makedirs(work_dir, exist_ok=True)

        input_dir = os.path.join(work_dir, "input")
        output_dir = os.path.join(work_dir, "output")
        subprocess.run(["rm", "-rf", "input"], cwd=work_dir)
        os.makedirs(input_dir, exist_ok=True)

        im0 = torchvision.transforms.functional.to_pil_image(torch.permute(image[0], (2, 0, 1)))
        im0.save(os.path.join(input_dir, "image.png"))

        with open(os.path.join(work_dir, "infer.sh"), "wt") as f:
            f.write(_infer_script % {
                "infer_passes": infer_passes,
                "denoise_steps": denoise_steps,
                "seed": seed,
                "input_dir_name": os.path.abspath(input_dir),
                "output_dir_name": os.path.abspath(output_dir)
            })

        subprocess.run(["bash", os.path.join("work", "infer.sh")], cwd=self.rep_dir)

        im1 = np.load(os.path.join(output_dir, "depth_npy", "image_pred.npy")).astype(np.float32)
        im1_min = np.min(im1)
        im1_max = np.max(im1)
        if im1_min == im1_max:
            im1_max = im1_min + 1.0
        im1 = (im1 - im1_min) * (1.0 / (im1_max - im1_min))

        return (torch.from_numpy(np.expand_dims(np.stack([im1, im1, im1], axis=-1), axis=0)),)
