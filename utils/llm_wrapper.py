import json
import os
import sys
import boto3


module_path = ".."
sys.path.append(os.path.abspath(module_path))
from utils.aws_services import get_bedrock_client

from langchain.llms.bedrock import Bedrock
from typing import Optional, List, Any
from langchain.callbacks.manager import CallbackManagerForLLMRun

boto3_bedrock = get_bedrock_client()

class BedrockModelWrapper(Bedrock):
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        prompt = "\n\nHuman: " + prompt + "\n\nAssistant:"   ## Satisfy Bedrock-Claude prompt requirements
        return super()._call(prompt, stop, run_manager, **kwargs)
    

model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}
llm = BedrockModelWrapper(model_id="anthropic.claude-v2", client=boto3_bedrock, model_kwargs=model_parameter, streaming=True, verbose=True)

def get_llm():
    return llm