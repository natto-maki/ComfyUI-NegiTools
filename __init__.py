from .negi.openai_dalle3 import OpenAiDalle3
from .negi.openai_translate import OpenAiTranslate
from .negi.string_function import StringFunction
from .negi.seed_generator import SeedGenerator
from .negi.image_properties import ImageProperties, LatentProperties
from .negi.composite_images import CompositeImages
from .negi.noise_image_generator import NoiseImageGenerator

NODE_CLASS_MAPPINGS = {
    "NegiTools_OpenAiDalle3": OpenAiDalle3,
    "NegiTools_OpenAiTranslate": OpenAiTranslate,
    "NegiTools_StringFunction": StringFunction,
    "NegiTools_SeedGenerator": SeedGenerator,
    "NegiTools_ImageProperties": ImageProperties,
    "NegiTools_LatentProperties": LatentProperties,
    "NegiTools_CompositeImages": CompositeImages,
    "NegiTools_NoiseImageGenerator": NoiseImageGenerator,
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
}
