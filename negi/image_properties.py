class ImageProperties:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",)
            },
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("WIDTH", "HEIGHT",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, image):
        # print("shape = " + str(list(image.shape)))
        return (image.shape[2], image.shape[1],)


class LatentProperties:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT",)
            },
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("WIDTH", "HEIGHT",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def doit(self, latent):
        image = latent["samples"]
        # print("shape = " + str(list(image.shape)))
        return (image.shape[3] * 8, image.shape[2] * 8,)
