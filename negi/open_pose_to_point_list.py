import json

import numpy as np
from controlnet_aux import OpenposeDetector
from controlnet_aux.util import HWC3, resize_image


_names = [
    "Nose", "Neck",
    "RShoulder", "RElbow", "RWrist",
    "LShoulder", "LElbow", "LWrist",
    "RHip", "RKnee", "RAnkle",
    "LHip", "LKnee", "LAnkle",
    "REye", "LEye", "REar", "LEar"
]

_name_to_index = {name: i for i, name in enumerate(_names)}


class OpenPoseToPointList:
    def __init__(self):
        self.open_pose = OpenposeDetector.from_pretrained("lllyasviel/Annotators")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "detect_resolution": ("INT", {"default": 512, "min": 64, "max": 2048, "step": 64, "display": "slider"}),
                "method": ([
                   "face",
                   "hand",
                   "all",
                ],),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("POINT_LIST",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, image, detect_resolution, method):
        input_image = (np.fmax(0.0, np.fmin(1.0, image.to('cpu').detach().numpy()[0])) * 255.0).astype(np.uint8)
        input_image = HWC3(input_image)
        input_image = resize_image(input_image, detect_resolution)

        poses = self.open_pose.detect_poses(input_image, include_hand=False, include_face=False)

        if method == "face":
            ret = []
            for pose in poses:
                x = 0.0
                y = 0.0
                n = 0
                for name in ["Nose", "REye", "LEye", "REar", "LEar"]:
                    key_point = pose.body.keypoints[_name_to_index[name]]
                    if key_point is not None:
                        x += key_point.x
                        y += key_point.y
                        n += 1
                if n != 0:
                    ret.append({"x": x / n, "y": y / n})

        elif method == "hand":
            ret = []
            for pose in poses:
                for name in ["RWrist", "LWrist"]:
                    key_point = pose.body.keypoints[_name_to_index[name]]
                    if key_point is not None:
                        ret.append({"x": key_point.x, "y": key_point.y})

        elif method == "all":
            ret = []
            for pose in poses:
                points = {}
                for i, key_point in enumerate(pose.body.keypoints):
                    if key_point is not None:
                        points[_names[i]] = {"x": key_point.x, "y": key_point.y, "score": key_point.score}
                ret.append(points)

        else:
            raise ValueError()

        return (json.dumps(ret, indent=2),)
