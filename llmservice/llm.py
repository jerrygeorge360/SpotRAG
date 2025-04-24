import io
import os
from groq import Groq
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import logging

from llmservice.instructions import first_instruction, second_instruction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Retrieve the API key
groq_key = os.environ.get("GROQ_KEY")


class LLMBase(ABC):
    """
    Abstract base class for implementing Language Model behaviors.

    This class provides a blueprint for creating language model components
    with essential methods to initialize and generate responses. Concrete
    implementations must inherit from this class and implement the abstract
    methods to function properly.

    Methods:
        generate_response: Abstract method for generating responses based
        on input documents.
    """
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def generate_response(self, document: str) -> str | None:
        ...


class LLMClient(LLMBase):
    """
    Manages interactions with a Language Learning Model (LLM).

    This class allows the user to configure and utilize a Language Learning Model
    (LLM) for generating responses based on provided input. It provides methods
    for setting up the client, configuring the model, and generating responses.
    Additionally, it includes utility for writing string data into an in-memory
    file-like object.
    """
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
    """
    Generates a response for a given instruction and initial query using the LLM service and writes it to memory.

    Generates a response based on the specified instruction and initial query by leveraging the LLM service
    configured with the 'llama-3.3-70b-versatile' model. The response, if any, is logged, written to an in-memory
    string buffer, and returned. If no response is generated or an error occurs, the function logs the issue
    and handles it gracefully.

    Parameters:
        instruction (str): The instruction to guide the model behavior.
        initial_query (str): The initial query input for which a response is expected.

    Returns:
        io.StringIO | None: The in-memory string buffer containing the response if successful, otherwise None.

    Raises:
        Exception: Logs any exception that occurs during execution without raising it further.
    """
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