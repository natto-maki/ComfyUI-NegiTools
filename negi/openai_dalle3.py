import openai
import base64
import io
import os
import json

import torch
from PIL import Image
from torchvision.transforms import functional as TF

from . import utils


class OpenAiDalle3:
    def __init__(self):
        self.__client = openai.OpenAI()
        self.__previous_resolution = ""
        self.__previous_seed = -1
        self.__previous_prompt = ""
        self.__cache_image = None
        self.__cache_revised_prompt = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": (["1024x1024", "1024x1792", "1792x1024"],),
                "dummy_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "great picture"
                }),
                "quality": (["HD", "Standard"],),
                "style": (["vivid", "natural"],),
                "retry": ("INT", {"default": 0, "min": 0, "max": 5}),
                "auto_save": ("BOOLEAN", {"default": False}),
                "auto_save_dir": ("STRING", {"multiline": False, "default": "./output_dalle3"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("IMAGE", "WIDTH", "HEIGHT", "REVISED_PROMPT")
    FUNCTION = "doit"
    OUTPUT_NODE = True
    CATEGORY = "Generator"

    def doit(self, resolution, dummy_seed, prompt, quality, style, retry, auto_save, auto_save_dir):
        if (self.__cache_image is None or
                self.__previous_resolution != resolution or self.__previous_seed != dummy_seed or
                self.__previous_prompt != prompt):
            r0 = None
            for retry_count in range(retry + 1):
                try:
                    r0 = self.__client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size=resolution,
                        quality="hd" if quality == "HD" else "standard",
                        style="vivid" if style == "vivid" else "natural",
                        n=1,
                        response_format="b64_json"
                    )
                    break
                except openai.BadRequestError as ex:
                    if retry_count >= retry:
                        raise ex
                    print("OpenAiDalle3: received BadRequestError, retrying... #%d : %s" % (
                        retry_count + 1, json.dumps(ex.response.json())))

            im0 = Image.open(io.BytesIO(base64.b64decode(r0.data[0].b64_json)))

            if auto_save:
                directory = utils.get_directory(auto_save_dir)
                next_index = utils.find_next_index(directory)
                image_file_name = os.path.join(directory, "out.%06d.png" % next_index)
                state_file_name = os.path.join(directory, "out.%06d.json" % next_index)
                im0.save(image_file_name)
                with open(state_file_name, "wt") as f:
                    f.write(json.dumps({
                        "resolution": resolution,
                        "prompt": prompt,
                        "quality": quality,
                        "style": style
                    }, indent=2, ensure_ascii=False))

            im1 = TF.to_tensor(im0.convert("RGBA"))
            im1[:3, im1[3, :, :] == 0] = 0
            revised_prompt = r0.data[0].revised_prompt
            self.__previous_resolution = resolution
            self.__previous_seed = dummy_seed
            self.__previous_prompt = prompt
            self.__cache_image = im1
            self.__cache_revised_prompt = revised_prompt
        else:
            im1 = self.__cache_image
            revised_prompt = self.__cache_revised_prompt

        images = torch.stack([im1])
        images = images.permute(0, 2, 3, 1)
        images = images[:, :, :, :3]
        widths = resolution.split("x")
        return images, int(widths[0]), int(widths[1]), revised_prompt
