from typing import Callable, Generic, Self, TypeVar
from .state import State

CT = TypeVar('CT')

class StateTreeNode(Generic[CT]):

    def __init__(self, state: State[CT]) -> None:
        self._state: State[CT] = state
        self._substates: list[Self] = []

    def do_only_leafs(self, f: Callable[[State[CT]], None]) -> None:
        if len(self._substates) == 0:
            f(self._state)
        else:
            for x in self._substates:
                x.do_only_leafs(f)

    def get_queue_leaves_first(self, queue = None):
        if queue is None:
            queue = []
        for x in self._substates:
            x.get_queue_leaves_first(queue = queue)
        queue.append(self._state)
        return queue

    def do_leaves_first(self, f: Callable[[State[CT]], None]) -> None:
        queue = self.get_queue_leaves_first()
        for x in queue:
            f(x)

    def get_node(self, t: type[State[CT]]) -> Self | None:
        if type(self._state) == t:
            return self, None
        else:
            for x in self._substates:
                s, p = x.get_node(t)
                if not s is None:
                    return s, self if p is None else p
        return None, None
    
    def remove(self, state: type[State[CT]]) -> None:
        for i, x in enumerate(self._substates):
            if type(x._state) == state:
                del self._substates[i]
                return
        raise RuntimeError(f'Subnode of type {state} not found')

    def add(self, node):
        self._substates.append(node)