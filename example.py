from abc import abstractmethod

from pymicrostate import State, StateMachine, parentstate

class Flashlight:

    def set_intensity(self, i):
        print(f'Setting intensity to {i}')
    
    def set_color(self, color):
        print(f'Setting color to {color}')

class BaseState(State[Flashlight]):

    @abstractmethod
    def on_button(self):
        pass
    
    @abstractmethod
    def color_button(self):
        pass

class OffState(BaseState):

    def on_button(self):
        self.set_state(OnState)
    
    def color_button(self):
        pass

    def on_enter(self):
        self.context.set_intensity(0)
    
    def on_exit(self):
        pass

class OnState(BaseState):

    def on_button(self):
        pass
    
    def color_button(self):
        pass

    def on_enter(self):
        self.set_state(RedState)
        self.set_state(FullPowerState)
    
    def on_exit(self):
        pass

@parentstate(OnState)
class FullPowerState(BaseState):

    def on_button(self):
        self.set_state(HalfPowerState)
    
    def color_button(self):
        pass

    def on_enter(self):
        self.context.set_intensity(1)
    
    def on_exit(self):
        pass

@parentstate(OnState)
class HalfPowerState(BaseState):

    def on_button(self):
        self.set_state(OffState)
    
    def color_button(self):
        pass

    def on_enter(self):
        self.context.set_intensity(0.5)
    
    def on_exit(self):
        pass

@parentstate(OnState)
class RedState(BaseState):

    def on_button(self):
        pass
    
    def color_button(self):
        self.set_state(GreenState)

    def on_enter(self):
        self.context.set_color("Red")
    
    def on_exit(self):
        pass

@parentstate(OnState)
class GreenState(BaseState):

    def on_button(self):
        pass
    
    def color_button(self):
        self.set_state(RedState)

    def on_enter(self):
        self.context.set_color("Green")
    
    def on_exit(self):
        pass

@parentstate(RedState)
class SomeOtherState(BaseState):
    pass

f = Flashlight()
sm = StateMachine(BaseState, f)

sm.start(OffState)


while True:
    a = input()
    c = a[0].lower()
    if c == 'x':
        sm.handle.on_button()
    if c == 'c':
        sm.handle.color_button()
    if c == 'q':
        break
