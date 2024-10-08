from typing import Any, Callable, Generic, Optional, Self, TypeVar
from abc import ABC, abstractmethod

from .basestatemachine import _StateMachine

CT = TypeVar('CT', covariant = True)

class _State():
    _parent_state: type[Self] | None = None

    @classmethod
    def _get_state_hierarchy(c_self: type[Self]) -> list[type[Self]]:
        hierarchy: list[type[Self]] = []
        cc: type[Self] = c_self
        while True:
            hierarchy.insert(0, cc)
            if not hasattr(cc, '_parent_state') or cc._parent_state is None:
                return hierarchy
            cc = cc._parent_state
        return hierarchy

class State(ABC, Generic[CT], _State):

    def __init__(self, _state_machine : _StateMachine):
        self._state_machine : _StateMachine = _state_machine
    
    @property
    def context(self) -> CT:
        # Needed because otherwise, there would be circular imports
        return self._state_machine._context # type: ignore

    @abstractmethod
    def on_enter(self) -> None:
        pass

    @abstractmethod
    def on_exit(self) -> None:
        pass

    def set_state(self, state : Self) -> None:
        self._state_machine._set_state(type(self), state)
    
    def exit(self) -> None:
        self._state_machine.exit(type(self))

def parentstate(parent: type[_State]) -> Callable[[type[_State]], type[_State]]:
    def _parentstate(c: type[_State]):
        c._parent_state = parent
        return c
    return _parentstate
