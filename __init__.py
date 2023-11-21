from .negi.openai_dalle3 import OpenAiDalle3
from .negi.openai_translate import OpenAiTranslate
from .negi.string_function import StringFunction
from .negi.seed_generator import SeedGenerator

NODE_CLASS_MAPPINGS = {
    "NegiTools_OpenAiDalle3": OpenAiDalle3,
    "NegiTools_OpenAiTranslate": OpenAiTranslate,
    "NegiTools_StringFunction": StringFunction,
    "NegiTools_SeedGenerator": SeedGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NegiTools_OpenAiDalle3": "OpenAI DALLe3 🧅",
    "NegiTools_OpenAiTranslate": "OpenAI Translate to English 🧅",
    "NegiTools_StringFunction": "String Function 🧅",
    "NegiTools_SeedGenerator": "Seed Generator 🧅",
}
