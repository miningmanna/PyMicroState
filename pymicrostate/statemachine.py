from typing import Any, Generic, TypeVar, get_args

from .basestatemachine import _StateMachine
from .state import State
from .statetree import StateTreeNode
from .statehandle import StateHandle

def get_common_states(a, b):
    return [x for x, y in zip(a, b) if x == y]

CT = TypeVar('CT')

def _print_state_tree(t, i = 0):
    print("".join(["    "] * i) + type(t._state).__name__)
    for x in t._substates:
        _print_state_tree(x, i = i+1)

class StateMachine(Generic[CT], _StateMachine):
    
    def __init__(self, basestate: Any, context: CT):
        if basestate is None:
            raise RuntimeError("Base state must not be None.")
        if not issubclass(basestate, State):
            raise RuntimeError("Base state must be a sub-class of pymicrostate.State")
        self._base_state: type[State[CT]] = basestate
        self._state_tree: StateTreeNode[CT] | None = None
        self._state_handle: StateHandle[CT] = StateHandle(self)
        self._context: CT = context

    def start(self, state: type[State[CT]]) -> None:
        if not self._state_tree is None:
            raise RuntimeError("StateMachine is already started.")
        if state is None:
            raise RuntimeError("State must not be None.")
        if not hasattr(state, '__bases__') or not self._base_state in state.__bases__:
            raise RuntimeError(f"State must be a direct sub-class of the base state {self._base_state}")
        
        state_instance: State[CT] = state(self)
        self._state_tree = StateTreeNode(state_instance)
        state_instance.on_enter()

    # Only called from within a state
    def _exit(self, state: type[State[CT]]) -> None:
        if self._state_tree is None:
            raise RuntimeError("StateMachine has not been started.")
        if state is None:
            raise RuntimeError("State must not be None.")
        if not hasattr(state, '__bases__') or not self._base_state in state.__bases__:
            raise RuntimeError(f"State must be a direct sub-class of the base state {self._base_state}")
        
        # Find out if we actually are in this state
        node, parent_node = self._state_tree.get_node(state)
        if node is None:
            raise RuntimeError("State is not active.")
        
        # Exit all states up to node leafs first
        node.do_leaves_first(lambda s: s.on_exit())
        
        # Remove node tree
        if parent_node is None:
            # Finish statemachine
            self._state_tree = None
        else:
            # Simply remove branch
            parent_node.remove(state)

    # Only called from within a state
    def _set_state(self, from_state: type[State[CT]], to_state: type[State[CT]]) -> None:
        from_hierarchy = from_state._get_state_hierarchy()
        to_hierarchy = to_state._get_state_hierarchy()
        
        common_states = get_common_states(from_hierarchy, to_hierarchy)

        if len(to_hierarchy) - len(common_states) > 1:
            raise RuntimeError("States must on the same level or one below")
        
        if len(common_states) == 0:
            # Exit all states
            self._exit(type(self._state_tree._state))
            # Enter new state
            self.start(to_state)
        else:
            # Switch from some points
            # Exit to first common state
            if len(from_hierarchy) > len(common_states):
                self._exit(from_hierarchy[len(common_states)])
            # Add new state/substate
            node, parent = self._state_tree.get_node(common_states[-1])
            state = to_state(self) 
            subtree = StateTreeNode(state)
            node.add(subtree)
            state.on_enter()


    @property
    def handle(self) -> Any:
        return self._state_handle