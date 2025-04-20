import io
import os
from groq import Groq
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import logging

from llmservice.instructions import first_instruction, second_instruction

# from services.llmservice.instructions import first_instruction, second_instruction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Retrieve the API key
groq_key = os.environ.get("GROQ_KEY")


class LLMBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def generate_response(self, document: str) -> str | None:
        ...


class LLMClient(LLMBase):
    def __init__(self):
        self._client = None
        self._config = {'instruction': '', 'model': None}

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, new_client):
        self._client = new_client

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, new_config):
        self._config = new_config

    def generate_response(self, document: str):
        try:
            chat_completion = self._client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.config.get('instruction')} {document}"
                    }
                ],
                model=self._config.get('model')
            )
            # Log the response for debugging
            result = chat_completion.choices[0].message.content
            logger.info("Response from model (%s): %s", self._config.get('model'), result)
            return result
        except Exception as e:
            logger.error("An error occurred while generating the response: %s", str(e))
            return None

    @staticmethod
    def write_to_memory(data: str) -> io.StringIO:
        text_obj = io.StringIO(data)
        text_obj.seek(0)
        return text_obj


def llm(instruction: str, initial_query: str)->io.StringIO|None:
    try:
        # Initialize Groq client
        client = Groq(api_key=groq_key)
        model = 'llama-3.3-70b-versatile'
        llmservice = LLMClient()
        llmservice.client = client
        llmservice.config = {"model": model, "instruction": instruction}

        response = llmservice.generate_response(initial_query)

        if not response:
            logger.error("No response from model.")
            return None

        logger.info("response: %s", response)

        # Write final response to memory
        data: io.StringIO = llmservice.write_to_memory(response)
        print(data,'weck')

        return data

    except Exception as e:
        logger.error("An error occurred in the main execution: %s", str(e))
        return None
#
# a= llm(initial_query='the list of albums you have are adele,eminem',instruction=second_instruction)
# a.seek(0)
# print(a.read())
# #
# scanned_text = 'what is 2 ^ 5? \n it is 64'
# llm_tumbler_response = generate_modified_response(first_instruction=first_instruction,second_instruction=second_instruction,initial_query=scanned_text)
# a = llm_tumbler_response.read()
# print(a)