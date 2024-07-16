import openai
import time
import urllib.error


class OpenAiGpt:
    def __init__(self):
        self.__client = openai.OpenAI()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ([
                    "gpt-4o",
                    "gpt-4o-2024-05-13",
                    "gpt-4-turbo",
                    "gpt-4-turbo-2024-04-09",
                    "gpt-4-turbo-preview",
                    "gpt-4-0125-preview",
                    "gpt-4-1106-preview",
                    "gpt-4-vision-preview",
                    "gpt-4",
                    "gpt-4-0314",
                    "gpt-4-0613",
                    "gpt-4-32k",
                    "gpt-4-32k-0314",
                    "gpt-4-32k-0613",
                    "gpt-3.5-turbo",
                    "gpt-3.5-turbo-16k",
                    "gpt-3.5-turbo-0301",
                    "gpt-3.5-turbo-0613",
                    "gpt-3.5-turbo-1106",
                    "gpt-3.5-turbo-16k-0613",
                ], {"default": "gpt-4-0613"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "max_tokens": ("INT", {"default": 512, "min": 16, "max": 4096}),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "You are a helpful assistant."
                })
            },
            "optional": {
                "a_role": (["user", "assistant", "system"], {"default": "user"}),
                "a": ("STRING", {"multiline": False, "default": ""}),
                "b_role": (["user", "assistant", "system"], {"default": "assistant"}),
                "b": ("STRING", {"multiline": False, "default": ""}),
                "c_role": (["user", "assistant", "system"], {"default": "user"}),
                "c": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "doit"
    OUTPUT_NODE = False
    CATEGORY = "Generator"

    def doit(self, model, seed, max_tokens, system_prompt, a_role, a, b_role, b, c_role, c):
        messages = [{"role": "system", "content": system_prompt}]
        input_role = [a_role, b_role, c_role]
        input_text = [a, b, c]
        for i in range(3):
            if input_text[i] is not None and len(input_text[i]) > 0:
                messages.append({
                    "role": input_role[i] if input_role[i] is not None else "user",
                    "content": input_text[i]
                })

        try_count = 0
        r0 = None
        while True:
            try_count += 1
            try:
                r0 = self.__client.chat.completions.create(
                    model=model,
                    max_tokens=max_tokens,
                    seed=seed,
                    messages=messages
                )
                break
            except openai.AuthenticationError as ex:
                raise ex
            except (urllib.error.HTTPError, openai.OpenAIError) as ex:
                if try_count >= 3:
                    raise ex
                time.sleep(5)
                continue

        return (r0.choices[0].message.content,)
