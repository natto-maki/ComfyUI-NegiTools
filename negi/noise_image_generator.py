import numpy as np
import torch


# Perlin Noise implementation was based on this post:
# https://pvigier.github.io/2018/06/13/perlin-noise-numpy.html

def _interpolate_function(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def _generate_perlin_noise_2d(rand_generator, shape, res):
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1

    # Gradients
    angles = 2 * np.pi * rand_generator.random((res[0] + 1, res[1] + 1))
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    gradients = gradients.repeat(d[0], 0).repeat(d[1], 1)
    g00 = gradients[:-d[0], :-d[1]]
    g10 = gradients[d[0]:, :-d[1]]
    g01 = gradients[:-d[0], d[1]:]
    g11 = gradients[d[0]:, d[1]:]

    # Ramps
    n00 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1])) * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)

    # Interpolation
    t = _interpolate_function(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)


def _generate_fractal_noise_2d(rand_generator, shape, res, octaves=1, persistence=0.5, lacunarity=2):
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * _generate_perlin_noise_2d(
            rand_generator, shape, (frequency * res[0], frequency * res[1]))
        frequency *= lacunarity
        amplitude *= persistence
    return noise


def _find_shape(width, height):
    w = 2 ** int(np.ceil(np.log2(max(width, height))))
    return w, w


class NoiseImageGenerator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 64, "display": "number"}),
                "height": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 64, "display": "number"}),
                "method": ([
                    "uniform_gray",
                    "uniform_color",
                    "gaussian_gray",
                    "gaussian_color",
                    "perlin_gray",
                    "perlin_color",
                    "perlin_fractal_gray",
                    "perlin_fractal_color",
                ],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "scale": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, "display": "slider"
                }),
                "center": ("FLOAT", {
                    "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, "display": "slider"
                }),
                "perlin_freq_log2": ("INT", {"default": 4, "min": 1, "max": 11, "step": 1, "display": "slider"}),
                "perlin_octaves": ("INT", {"default": 4, "min": 1, "max": 11, "step": 1, "display": "slider"}),
                "perlin_persistence": ("FLOAT", {
                    "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, "display": "slider"
                }),
            },
            "optional": {
                "image_opt": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "Generator"

    @staticmethod
    def round(image):
        return np.fmax(0.0, np.fmin(1.0, image))

    def doit(
            self, width, height, method, seed, scale, center,
            perlin_freq_log2, perlin_octaves, perlin_persistence, image_opt=None):

        if image_opt is not None:
            width = image_opt.shape[2]
            height = image_opt.shape[1]

        rand_generator = np.random.default_rng(seed)
        image_r = None
        if method == "uniform_gray":
            image_r = center + scale * (rand_generator.random((1, height, width, 1)) - 0.5)
        elif method == "uniform_color":
            image_r = center + scale * (rand_generator.random((1, height, width, 3)) - 0.5)
        elif method == "gaussian_gray":
            image_r = center + scale * rand_generator.normal(0.0, 0.5, (1, height, width, 1))
        elif method == "gaussian_color":
            image_r = center + scale * rand_generator.normal(0.0, 0.5, (1, height, width, 3))
        elif method.startswith("perlin_"):
            shape = _find_shape(width, height)
            shape_log2 = int(np.log2(shape[0]))
            res = shape[0] // (2 ** max(1, shape_log2 - perlin_freq_log2 + 1))
            if method == "perlin_gray":
                image_r = _generate_perlin_noise_2d(rand_generator, shape, (res, res))
            elif method == "perlin_color":
                image_r = np.stack([
                    _generate_perlin_noise_2d(rand_generator, shape, (res, res)) for _ in range(3)], axis=-1)
            elif method == "perlin_fractal_gray":
                image_r = _generate_fractal_noise_2d(
                    rand_generator, shape, (res, res), perlin_octaves, perlin_persistence)
            elif method == "perlin_fractal_color":
                image_r = np.stack([
                    _generate_fractal_noise_2d(
                        rand_generator, shape, (res, res), perlin_octaves, perlin_persistence)
                    for _ in range(3)], axis=-1)
            image_r = image_r.reshape((1, shape[0], shape[1], -1))[:, :height, :width, :]
            image_r = center + (scale * 0.5) * image_r

        if image_r is None:
            raise ValueError()

        image_b = image_opt if image_opt is not None else (
            torch.full((1, height, width, 3), 0.0, dtype=torch.float32, device="cpu"))
        return (self.round(image_b + image_r),)
