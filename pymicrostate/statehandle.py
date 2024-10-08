from typing import Callable, Generic, TypeVar

from .basestatemachine import _StateMachine

CT = TypeVar('CT')

class StateHandle(Generic[CT]):

    def __init__(self, statemachine: _StateMachine):
        self._pymicrostate_statemachine: _StateMachine = statemachine
        self._pymicrostate_method_cache: dict[str, Callable] = {}

    def __getattr__(self, name):
        if name in self._pymicrostate_method_cache:
            return self._pymicrostate_method_cache[name]
        else:
            # Create wrapper which calls the method of each state with the given args
            def _wrapper(*args, **kwargs):
                if self._pymicrostate_statemachine._state_tree is None:
                    raise RuntimeError("State machine has no current state.")
                def caller(state):
                    getattr(state, name)(*args, **kwargs)
                self._pymicrostate_statemachine._state_tree.do_leaves_first(caller)

            self._pymicrostate_method_cache[name] = _wrapper
            return _wrapper