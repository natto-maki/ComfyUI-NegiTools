import random


class SeedGenerator:
    __generation = 0

    def __init__(self):
        self.__previous_seed = random.randint(0, 0xffffffffffffffff)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "generation_mode": (["random", "keep_previous"],),
            }
        }

    @classmethod
    def IS_CHANGED(cls, generation_mode):
        if generation_mode == "random":
            cls.__generation += 1
        return cls.__generation

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("SEED",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, generation_mode):
        if generation_mode == "random":
            self.__previous_seed = random.randint(0, 0xffffffffffffffff)
        print("NegiTools_SeedGenerator: provided seed value = %d" % self.__previous_seed)
        return (self.__previous_seed,)
