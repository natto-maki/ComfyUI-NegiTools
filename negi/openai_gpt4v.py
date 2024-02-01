import os
import base64

import openai
import requests

import torch
import torchvision


_api_key = os.environ.get("OPENAI_API_KEY")
_tmp_file = "gpt4v_tmp.jpg"


class OpenAiGpt4v:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "detail": (["auto", "low", "high"],),
                "max_tokens": ("INT", {"default": 512, "min": 16, "max": 8192}),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "What’s in this image?"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "Generator"

    def doit(self, image, seed, detail, max_tokens, prompt):
        _ = seed

        im0 = torchvision.transforms.functional.to_pil_image(torch.permute(image[0], (2, 0, 1)))
        im0.save(_tmp_file)
        with open(_tmp_file, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }

        r0 = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if r0.status_code != 200:
            raise openai.BadRequestError("Server returned an error", body=None, response=r0)

        r1 = r0.json()
        if "choices" not in r1 or len(r1["choices"]) < 1:
            raise openai.BadRequestError("Empty results returned", body=None, response=r0)
        r2 = r1["choices"][0]
        if "finish_reason" not in r2 or r2["finish_reason"] != "stop":
            raise openai.BadRequestError("Request was not completed correctly", body=None, response=r0)
        return (r2["message"]["content"],)
