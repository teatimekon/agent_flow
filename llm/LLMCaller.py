from langchain_openai import ChatOpenAI
import yaml
from logs import logger
from .OpenAI import OpenAI 
from .Ollama import Ollama
from .BaseLLM import BaseLLM
class LLMCaller(BaseLLM):
    def __init__(self, tool_call:bool=False):
        # self.llm_supporter : str
        # self.llm_api_key : str
        # self.llm_base_url : str
        # self.llm_model_name : str
        # self.llm_temperature : float
        super().__init__()
        self.tool_call = tool_call
        self.__default_config = {   # 设置成私有成员变量
            "MODEL_NAME": "gpt-4o-mini",
            "MODEL_TEMPERATURE": 0,
            "MODEL_BASE_URL": "https://api2.aigcbest.top/v1",
            "MODEL_API_KEY": "sk-WbEpTniVLtZbePrk3e4fE2B1AbCd43B6B0FcCaC5A0478934",
            "MODEL_SUPPORTER": "openai"
        }   
        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error("Error reading config file: %s", e)
                logger.info("Using default config")
                config = self.__default_config 
        self.llm_supporter = config["MODEL_SUPPORTER"]
        self.llm_api_key = config["MODEL_API_KEY"]
        self.llm_base_url = config["MODEL_BASE_URL"]
        self.llm_model_name = config["MODEL_NAME"]
        self.llm_temperature = config["MODEL_TEMPERATURE"]
        self.llm = self.my_llm()

    def my_llm(self):
        if self.llm_supporter == "openai":
            self.llm_wrapper = OpenAI(
                api_key=self.llm_api_key,
                base_url=self.llm_base_url,
                model_name=self.llm_model_name,
                tool_call=self.tool_call
            )
        elif self.llm_supporter == "ollama":
            self.llm_wrapper = Ollama(
                model_name=self.llm_model_name,
                tool_call=self.tool_call
            )
        else:
            raise ValueError("Unsupported LLM supporter")
        return self.llm_wrapper.get_llm()


    def invoke(self, messages, **kwargs):
        from time import time
        start = time()
        res = self.llm.invoke(messages, **kwargs)
        end = time()
        logger.info(f"Time taken: {end - start} seconds")
        return res