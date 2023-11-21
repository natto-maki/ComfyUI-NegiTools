import random


class SeedGenerator:
    def __init__(self):
        self.__previous_seed = random.randint(0, 0xffffffffffffffff)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "generation_mode": (["random", "keep_previous"],),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("SEED",)
    FUNCTION = "doit"
    OUTPUT_NODE = True
    CATEGORY = "utils"

    def doit(self, generation_mode):
        if generation_mode == "random":
            self.__previous_seed = random.randint(0, 0xffffffffffffffff)
        return (self.__previous_seed,)
