import json

import numpy as np
import torch


class DetectFaceRotationForInpainting:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "parts": ("STRING", {"multiline": False, "default": ""}),
                "image": ("IMAGE",),
                "radius_scale": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.01,
                    "round": 0.001,
                    "display": "number"
                }),
                "overwrite_rotation": (["None", "0", "90", "180", "270"],),
            }
        }

    RETURN_TYPES = ("INT", "MASK", "INT")
    RETURN_NAMES = ("ROTATION_INV", "MASK", "ROTATION")
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    @staticmethod
    def get_face(xw, yw, radius_scale, parts):
        x = 0.0
        y = 0.0
        n = 0
        radius = 0
        rot = 0

        for name in ["Nose", "REye", "LEye", "REar", "LEar"]:
            if name in parts:
                x += parts[name]["x"]
                y += parts[name]["y"]
                n += 1

        if n != 0:
            x = x / n
            y = y / n
            for name in ["Nose", "REye", "LEye", "REar", "LEar"]:
                if name in parts:
                    x0 = x * xw
                    y0 = y * yw
                    x1 = parts[name]["x"] * xw
                    y1 = parts[name]["y"] * yw
                    radius = max(radius, int(np.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0)) * radius_scale))

        if n != 0 and "Neck" in parts:
            x0 = x * xw
            y0 = y * yw
            x1 = parts["Neck"]["x"] * xw
            y1 = parts["Neck"]["y"] * yw
            if abs(x1 - x0) < abs(y1 - y0):
                rot = 0 if y0 < y1 else 180
            else:
                rot = 90 if x0 < x1 else 270

        return x, y, radius, rot

    @staticmethod
    def rotate(rot, x, y):
        if rot == 0:
            return x, y
        if rot == 90:
            return y, 1 - x
        if rot == 180:
            return 1 - x, 1 - y
        if rot == 270:
            return 1 - y, x

    def doit(self, parts, image, radius_scale, overwrite_rotation):
        parts_list = json.loads(parts)
        xw = image.shape[2]
        yw = image.shape[1]

        x = 0.0
        y = 0.0
        radius = 0
        rot = 0
        for parts in parts_list:
            t_x, t_y, t_radius, t_rot = self.get_face(xw, yw, radius_scale, parts)
            if t_radius > radius:
                x = t_x
                y = t_y
                radius = t_radius
                rot = t_rot

        if overwrite_rotation != "None":
            rot = int(overwrite_rotation)

        rot_inv = (0 if rot == 0 else 360 - rot)
        x_r, y_r = self.rotate(rot_inv, x, y)

        xw_r = (xw if rot == 0 or rot == 180 else yw)
        yw_r = (yw if rot == 0 or rot == 180 else xw)

        if radius == 0:
            return rot_inv, torch.from_numpy(np.zeros((1, yw_r, xw_r), dtype=np.float32)), rot

        px = (np.reshape(np.arange(xw_r, dtype=np.float32), (1, -1))
              * np.ones((yw_r, 1), dtype=np.float32))
        py = (np.reshape(np.arange(yw_r, dtype=np.float32), (-1, 1))
              * np.ones((1, xw_r), dtype=np.float32))
        d2 = np.power(px - x_r * xw_r, 2.0) + np.power(py - y_r * yw_r, 2.0)
        mask = torch.from_numpy(np.reshape(d2 <= radius * radius, (1, yw_r, xw_r)).astype(np.float32))
        return rot_inv, mask, rot
