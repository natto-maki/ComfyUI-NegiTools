from .negi.openai_dalle3 import OpenAiDalle3
from .negi.openai_translate import OpenAiTranslate
from .negi.string_function import StringFunction
from .negi.seed_generator import SeedGenerator
from .negi.image_properties import ImageProperties, LatentProperties
from .negi.composite_images import CompositeImages
from .negi.noise_image_generator import NoiseImageGenerator
from .negi.open_pose_to_point_list import OpenPoseToPointList
from .negi.point_list_to_mask import PointListToMask
from .negi.depth_estimation_by_marigold import DepthEstimationByMarigold
from .negi.stereo_image_generator import StereoImageGenerator
from .negi.image_reader_writer import RandomImageLoader, SaveImageToDirectory
from .negi.detect_face_rotation_for_inpainting import DetectFaceRotationForInpainting

NODE_CLASS_MAPPINGS = {
    "NegiTools_OpenAiDalle3": OpenAiDalle3,
    "NegiTools_OpenAiTranslate": OpenAiTranslate,
    "NegiTools_StringFunction": StringFunction,
    "NegiTools_SeedGenerator": SeedGenerator,
    "NegiTools_ImageProperties": ImageProperties,
    "NegiTools_LatentProperties": LatentProperties,
    "NegiTools_CompositeImages": CompositeImages,
    "NegiTools_NoiseImageGenerator": NoiseImageGenerator,
    "NegiTools_OpenPoseToPointList": OpenPoseToPointList,
    "NegiTools_PointListToMask": PointListToMask,
    "NegiTools_DepthEstimationByMarigold": DepthEstimationByMarigold,
    "NegiTools_StereoImageGenerator": StereoImageGenerator,
    "NegiTools_RandomImageLoader": RandomImageLoader,
    "NegiTools_SaveImageToDirectory": SaveImageToDirectory,
    "NegiTools_DetectFaceRotationForInpainting": DetectFaceRotationForInpainting,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NegiTools_OpenAiDalle3": "OpenAI DALLe3 🧅",
    "NegiTools_OpenAiTranslate": "OpenAI Translate to English 🧅",
    "NegiTools_StringFunction": "String Function 🧅",
    "NegiTools_SeedGenerator": "Seed Generator 🧅",
    "NegiTools_ImageProperties": "Image Properties 🧅",
    "NegiTools_LatentProperties": "Latent Properties 🧅",
    "NegiTools_CompositeImages": "Composite Images 🧅",
    "NegiTools_NoiseImageGenerator": "Noise Image Generator 🧅",
    "NegiTools_OpenPoseToPointList": "OpenPose to Point List 🧅",
    "NegiTools_PointListToMask": "Point List to Mask 🧅",
    "NegiTools_DepthEstimationByMarigold": "Depth Estimation by Marigold (experimental) 🧅",
    "NegiTools_StereoImageGenerator": "Stereo Image Generator 🧅",
    "NegiTools_RandomImageLoader": "Random Image Loader 🧅",
    "NegiTools_SaveImageToDirectory": "Save Image to Directory 🧅",
    "NegiTools_DetectFaceRotationForInpainting": "Detect Face Rotation for Inpainting 🧅",
}
