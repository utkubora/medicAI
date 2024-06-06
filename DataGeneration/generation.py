from abc import ABC, abstractmethod, abstractproperty
from typing import List, Tuple, Dict
from sentence_transformers import SentenceTransformer

class AbstractBehavior(ABC):
    """Abstract class to help in creation of ExpectedBehavior classes
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def check(self) -> List[Tuple[bool, Dict[str, float]]]:
        raise NotImplementedError(
            'Derived class must implement the check method.'
        )

    @abstractproperty
    def behavior_description(self):
        pass

class SimilarGeneration(AbstractBehavior):
    """
    Class to verify if the model's generations are robust to
    perturbations.
    """
    def __init__(
        self,
        similarity_model: SentenceTransformer,
        similarity_threshold: float = 0.7,
        similarity_metric_key: str = 'Similarity [Generations]'
    ) -> None:
        self.similarity_model = similarity_model
        self.similarity_threshold = similarity_threshold
        self.similarity_metric_key = similarity_metric_key
        self.descriptor = (
            f'Model\'s generations for perturbations '
            f'are greater than {self.similarity_threshold} similarity metric '
            f'compared to the reference generation.'
        )
        return

    def check(
        self,
        perturbed_generations: List[str],
        reference_generation: str,
    ) -> List[Tuple[bool, Dict[str, float]]]:
        test_results = []
        for peturbed_gen in perturbed_generations:
            try:
                score = compute_similarity(
                    sentence_model=self.similarity_model,
                    reference_sentence=reference_generation,
                    perturbed_sentence=peturbed_gen,
                )
                score = round(score, ndigits=2)
                test_results.append(score)
            except Exception as e:
                raise e
        return test_results
    
    def behavior_description(self):
        return self.descriptor