import openai
import base64
import io

import torch
from PIL import Image
from torchvision.transforms import functional as TF


class OpenAiDalle3:
    def __init__(self):
        self.__client = openai.OpenAI()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": (["1024x1024", "1024x1792", "1792x1024"],),
                "dummy_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "great picture"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "WIDTH", "HEIGHT")
    FUNCTION = "doit"
    OUTPUT_NODE = True
    CATEGORY = "Generator"

    def doit(self, resolution, dummy_seed, prompt):
        _ = dummy_seed
        r0 = self.__client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=resolution,
            quality="hd",  # "standard"
            n=1,
            response_format="b64_json"
        )
        im0 = Image.open(io.BytesIO(base64.b64decode(r0.data[0].b64_json)))
        im1 = TF.to_tensor(im0.convert("RGBA"))
        im1[:3, im1[3, :, :] == 0] = 0

        images = torch.stack([im1])
        images = images.permute(0, 2, 3, 1)
        images = images[:, :, :, :3]
        widths = resolution.split("x")
        return images, int(widths[0]), int(widths[1])
