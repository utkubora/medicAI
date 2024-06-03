from typing import List, Optional, Literal, Dict

from langchain.llms.base import BaseLLM

from generation import (
    SimilarGeneration,
)

from perturbations import Paraphrase
from perturbations import TransformBase


class LLMEval:
    def __init__(
        self,
        llm: BaseLLM,
        expected_behavior: SimilarGeneration,
        transformation: Optional[TransformBase] = None,
    ) -> None:
        self.llm = llm
        self.expected_behavior = expected_behavior
        if transformation is None:
            self.transformation = Paraphrase()
        else:
            self.transformation = transformation
        return

    def _get_generation(
        self,
        prompt: str,
        pre_context: Optional[str],
        post_context: Optional[str],
    ) -> str:
        """Get generation from the model"""
        try:
            llm_input = self.construct_llm_input(prompt, pre_context, post_context)
            response = str(self.llm(llm_input))
        except Exception as err:
            raise err
        return response

    def construct_llm_input(
        self,
        prompt: str,
        pre_context: Optional[str],
        post_context: Optional[str],
        delimiter: str = " ",
    ) -> str:
        if pre_context is not None:
            full_prompt = pre_context + delimiter + prompt
        else:
            full_prompt = prompt
        if post_context is not None:
            full_prompt += delimiter + post_context
        return full_prompt

    def generate_alternative_prompts(
        self,
        prompt: str,
    ) -> List[str]:
        return self.transformation.transform(prompt)


