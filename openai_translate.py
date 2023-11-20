import openai
import time
import json
import urllib.error


_prompt = '''\
Please translate it into clean English.
Output should be in JSON format as follows: {"translated": "translated text"}'''


class OpenAiTranslate:
    def __init__(self):
        self.__client = openai.OpenAI()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_any_language": ("STRING", {
                    "multiline": True,
                    "default": "return \"日本語の文章\""
                })
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "doit"
    OUTPUT_NODE = True
    CATEGORY = "utils"

    def __invoke(self, messages, model_name: str = "gpt-4-1106-preview"):
        try_count = 0
        r0 = None
        while True:
            try_count += 1
            try:
                r0 = self.__client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                break
            except openai.AuthenticationError as ex:
                raise ex
            except (urllib.error.HTTPError, openai.OpenAIError) as ex:
                if try_count >= 3:
                    raise ex
                time.sleep(5)
                continue

        finish_reason = r0.choices[0].finish_reason
        if finish_reason != "stop":
            raise RuntimeError("API finished with unexpected reason: " + finish_reason)

        return r0.choices[0].message.content

    def doit(self, text_any_language):
        r0 = self.__invoke([
            {"role": "system", "content": _prompt},
            {"role": "user", "content": text_any_language}
        ])
        j0 = json.loads(r0)
        return (j0["translated"] if "translated" in j0 and isinstance(j0["translated"], str) else "<error>",)
