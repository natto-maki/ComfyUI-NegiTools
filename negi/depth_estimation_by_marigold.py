import os
import sys
import subprocess

import numpy as np
import torch
import torchvision


_dependency_dir = "dependencies"

_install_script_bare = '''\
bash script/download_weights.sh
'''

_install_script_venv = '''\
source venv/marigold/bin/activate
pip install -r requirements.txt
bash script/download_weights.sh
'''

_infer_script_bare = '''\
%(interpreter)s run.py --n_infer %(infer_passes)d --denoise_steps %(denoise_steps)d --seed %(seed)d --input_rgb_dir "%(input_dir_name)s" --output_dir "%(output_dir_name)s"
'''

_infer_script_venv = '''\
source venv/marigold/bin/activate
python run.py --n_infer %(infer_passes)d --denoise_steps %(denoise_steps)d --seed %(seed)d --input_rgb_dir "%(input_dir_name)s" --output_dir "%(output_dir_name)s"
'''


class DepthEstimationByMarigold:
    def __check_environment(self, enable_venv=False):
        if not os.path.isdir(os.path.join(self.dep_dir, "Marigold")):
            r0 = subprocess.run(["git", "clone", "https://github.com/prs-eth/Marigold.git"], cwd=self.dep_dir)
            if r0.returncode != 0:
                subprocess.run(["rm", "-rf", "Marigold"], cwd=self.dep_dir)
                raise RuntimeError("Marigold repository not found or connection error")

        if not enable_venv and not os.path.isfile(os.path.join(self.rep_dir, "installed_bare")):
            with open(os.path.join(self.rep_dir, "install.sh"), "wt") as f:
                f.write(_install_script_bare)
            subprocess.run(["bash", "install.sh"], cwd=self.rep_dir)
            with open(os.path.join(self.rep_dir, "installed_bare"), "wt") as f:
                f.write("installed")

        if enable_venv and not os.path.isfile(os.path.join(self.rep_dir, "installed_venv")):
            # Make sure that venv has been created correctly.
            # Because if you ignore the error, the ComfyUI runtime environment package will be incorrectly overwritten.
            subprocess.run([sys.executable, "-m", "venv", "venv/marigold"], cwd=self.rep_dir)
            if not os.path.isfile(os.path.join(self.rep_dir, "venv", "marigold", "bin", "activate")):
                raise RuntimeError("Failed to setup venv for Marigold")

            with open(os.path.join(self.rep_dir, "install.sh"), "wt") as f:
                f.write(_install_script_venv)
            # TODO pick errors
            subprocess.run(["bash", "install.sh"], cwd=self.rep_dir)
            with open(os.path.join(self.rep_dir, "installed_venv"), "wt") as f:
                f.write("installed")


    def __init__(self):
        self.dep_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), _dependency_dir)
        os.makedirs(self.dep_dir, exist_ok=True)
        self.rep_dir = os.path.join(self.dep_dir, "Marigold")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "infer_passes": ("INT", {"default": 10, "min": 1, "max": 40, "step": 1, "display": "number"}),
                "denoise_steps": ("INT", {"default": 10, "min": 1, "max": 40, "step": 1, "display": "number"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffff}),
                "runtime": ([
                   "bare (recommended)",
                   "venv (if \"bare\" doesn't work)",
                ],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("DEPTH_IMAGE",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "Generator"

    def doit(self, image, infer_passes, denoise_steps, seed, runtime):
        use_venv = runtime.startswith("venv")
        self.__check_environment(use_venv)

        work_dir = os.path.join(self.rep_dir, "work")
        os.makedirs(work_dir, exist_ok=True)

        input_dir = os.path.join(work_dir, "input")
        output_dir = os.path.join(work_dir, "output")
        subprocess.run(["rm", "-rf", "input"], cwd=work_dir)
        os.makedirs(input_dir, exist_ok=True)

        im0 = torchvision.transforms.functional.to_pil_image(torch.permute(image[0], (2, 0, 1)))
        im0.save(os.path.join(input_dir, "image.png"))

        with open(os.path.join(work_dir, "infer.sh"), "wt") as f:
            f.write((_infer_script_venv if use_venv else _infer_script_bare) % {
                "interpreter": os.path.abspath(sys.executable),
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
