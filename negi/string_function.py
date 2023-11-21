_sandbox_template0 = '''\
import random
import re
import numpy as np

def _string_function(a, b, c):
'''

_sandbox_template1 = '''\
_result.append(_string_function(_a, _b, _c))
'''


class StringFunction:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "python_code": ("STRING", {
                    "multiline": True,
                    "default": "return \"a text\""
                })
            },
            "optional": {
                "a": ("STRING", {"multiline": False, "default": ""}),
                "b": ("STRING", {"multiline": False, "default": ""}),
                "c": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "doit"
    OUTPUT_NODE = True
    CATEGORY = "utils"

    def doit(self, python_code, a, b, c):
        if python_code.find("import") != -1:
            raise ValueError("\"import\" cannot be included in python_code for security reasons")

        code = (_sandbox_template0 +
                "    " + "\n    ".join((python_code + "\n").split("\n")) + "\n" +
                _sandbox_template1)

        sandbox_builtins = {k: v for k, v in __builtins__.items() if k != "eval" and k != "exec"}
        result = []
        exec(code, {"__builtins__": sandbox_builtins, "_result": result, "_a": a, "_b": b, "_c": c})
        return (result[0] if len(result) == 1 and isinstance(result[0], str) else "",)
