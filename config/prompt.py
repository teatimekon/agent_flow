import yaml

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

if config["PROMPT_LANGUAGE"] == "cn":
    from .prompt_cn import *
else:
    from .prompt_en import *