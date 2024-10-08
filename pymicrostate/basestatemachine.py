from typing import Any, Generic, TypeVar
from abc import ABC, abstractmethod

CT = TypeVar('CT')

class _StateMachine(ABC):
    
    @abstractmethod
    def _set_state(self, origin: Any, dest: Any) -> None:
        pass