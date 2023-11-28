import numpy as np


class CompositeImages:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_B": ("IMAGE",),
                "image_F": ("IMAGE",),
                "method": ([
                    "default",
                    "thru_B",
                    "thru_F",
                    "multiply",
                    "divide",
                    "screen",
                    "overlay",
                    "dodge",
                    "burn",
                    "hard_light",
                    "soft_light",
                    "difference",
                    "add",
                    "subtract",
                    "lighten",
                    "darken"
                ],),
                "alpha": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "round": 0.001,
                    "display": "slider"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    @staticmethod
    def round(image):
        return np.fmax(0.0, np.fmin(1.0, image))

    @staticmethod
    def round_eps(image):
        return np.fmax(1.0 / 256, np.fmin(1.0, image))

    def doit(self, image_B, image_F, method, alpha):
        image_r = None
        if method == "default":
            image_r = image_F
        elif method == "thru_B":
            return (image_B,)
        elif method == "thru_F":
            return (image_F,)
        elif method == "multiply":
            image_r = image_B * image_F
        elif method == "divide":
            image_r = image_B / self.round_eps(image_F)
        elif method == "screen":
            image_r = 1.0 - (1.0 - image_F) * (1.0 - image_B)
        elif method == "overlay":
            image_r = image_B * (image_B + 2.0 * image_F * (1.0 - image_B))
        elif method == "dodge":
            image_r = image_B / self.round_eps(1.0 - image_F)
        elif method == "burn":
            image_r = 1.0 - (1.0 - image_B) / self.round_eps(image_F)
        elif method == "hard_light":
            image_r = np.where(
                image_F <= 0.5,
                2.0 * image_F * image_B,
                1.0 - (1.0 - 2.0 * (image_F - 0.5)) * (1.0 - image_B))
        elif method == "soft_light":
            image_r = ((1.0 - image_B) * image_F + (1.0 - (1.0 - image_F) * (1.0 - image_B))) * image_B
        elif method == "difference":
            image_r = np.abs(image_B - image_F)
        elif method == "add":
            image_r = image_B + image_F
        elif method == "subtract":
            image_r = image_B - image_F
        elif method == "lighten":
            image_r = np.fmax(image_B, image_F)
        elif method == "darken":
            image_r = np.fmin(image_B, image_F)
        # TODO support "hue", "saturation", "color", "value"

        if image_r is None:
            raise ValueError()

        return ((1 - alpha) * image_B + alpha * self.round(image_r),)
