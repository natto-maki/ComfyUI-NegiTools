import json

import numpy as np


class PointListToMask:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "point_list": ("STRING", {"multiline": False, "default": ""}),
                "width": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 64, "display": "number"}),
                "height": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 64, "display": "number"}),
                "radius": ("INT", {"default": 50, "min": 1, "max": 2048, "step": 1, "display": "number"}),
            }
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, point_list, width, height, radius):
        point_list = json.loads(point_list)

        ret = []
        px = (np.reshape(np.arange(width, dtype=np.float32), (1, -1))
              * np.ones((height, 1), dtype=np.float32))
        py = (np.reshape(np.arange(height, dtype=np.float32), (-1, 1))
              * np.ones((1, width), dtype=np.float32))
        for point in point_list:
            d2 = np.power(px - point["x"] * width, 2.0) + np.power(py - point["y"] * height, 2.0)
            ret.append(np.reshape(d2 <= radius * radius, (height, width)).astype(np.float32))

        if len(ret) == 0:
            return (np.zeros((1, height, width), dtype=np.float32),)

        return (np.fmin(1.0, np.sum(np.stack(ret), axis=0, keepdims=True)),)
