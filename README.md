# ComfyUI-NegiTools

## Installation

- Install dependencies: pip install openai

- Clone the repository: git clone https://github.com/natto-maki/ComfyUI-NegiTools.git
  to your ComfyUI custom_nodes directory

  The script will then automatically install all custom scripts and nodes.
  It will attempt to use symlinks and junctions to prevent having to copy files and keep them up to date.

- To launch: Set the OPENAI_API_KEY environment variable before launching ComfyUI. 

  e.g., OPENAI_API_KEY=sk-<...your API key here...> python3 main.py ...

- For uninstallation:
  Delete the cloned repo in custom_nodes

## Update

1. Navigate to the cloned repo e.g. custom_nodes/ComfyUI-NegiTools
2. git pull

## Features

### OpenAI DALLe3

Generates an image using DALL-E3 via OpenAI API.

required: OPENAI_API_KEY.

- `prompt`: Specify a positive prompt; there is no negative prompt in DALL-E3. 
  The prompt can be written in any language.
- `resolution`: Select the output resolution from the candidates;
  the resolution combination is fixed in DALL-E3.
- `dummy_seed`: DALL-E3 does not currently provide a way to specify a seed value. 
  This `dummy_seed` value is a parameter to control caching. 
  If the prompt and resolution are the same and dummy_seed has not changed, 
  this Node will reuse the cached output (i.e., the image will not change); 
  if `dummy_seed` has changed, it will generate a new image.
  Since it does not function as an actual seed value,
  the output will not be the same even if regenerated with the same value set.

![screenshot_openai_dalle3](resources/screenshot_openai_dalle3.png)


### OpenAI Translate to English

Translates text written in any language into English using GPT-4.
This is useful when you want to write prompts in a language other than English
for input into Stable Diffusion.

It may be even more useful in combination with String Function.

required: OPENAI_API_KEY.

![screenshot_openai_translate](resources/screenshot_openai_translate.png)


### String Function

String generation using Python scripts.

Any Python script can be stored in `python_code`.
The script will be wrapped in a function and executed, and output a string that is returned by the `return` statement.

`a, b, c` are optional input strings. 
They can be accessed in the script as they are with the variable names `a, b, c`.

Available modules: random, re, numpy (as np)


`python_code` example:
```python
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
return "a girl with %s hair and %s eyes wearing %s maid costume" % (
  random.choice(colors), random.choice(colors), a 
)
# got "a girl with green hair and red eyes wearing white maid costume", etc.
```

![screenshot_string_function](resources/screenshot_string_function.png)


> [!NOTE]  
> The import statement and the eval() and exec() functions cannot be used in python_code field 
> for security reasons.

> [!CAUTION]
> This Node is capable of executing Python code and therefore has security risks. 
> Please review the python_code contents carefully before attempting to execute a workflow 
> received from a third party that cannot be fully trusted.


### Seed Generator

Generate an integer to be used as the seed value.

Although Sampler, such as KSampler, allows the user to select a random or fixed value for the seed value, 
if they are set to random, the values are updated after workflow is executed.
This behavior making it difficult to restore the seed value 
after a good picture is obtained by random generation.

The "Seed Generator" node can be set to `random` or `keep_previous`,
and the seed value is generated at the time of workflow execution.
Therefore, you can set the Seed Generator node to `random` at first,
and repeat the generation process, 
then switch to `keep_previous` when a good picture is obtained, 
and fix the seed value thereafter.

![screenshot_seed_generator](resources/screenshot_seed_generator.png)

