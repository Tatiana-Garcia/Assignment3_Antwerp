import aalpy
from utils import *
from enum import Enum, auto


class State(Enum):
    OFF = auto()
    LOCKED = auto()
    UNLOCKED = auto()
    PRINTING = auto()
    BIN = auto()


class System(aalpy.SUL):
    def __init__(self):
        super().__init__()
        self.state = State.OFF

    def _is_accepting(self):
        return self.state == State.LOCKED

    @override
    def pre(self):
        self.state = State.OFF

    @override
    def post(self):
        pass

    @override
    def step(self, letter: Symbol):
        if letter is None:
            return False
        match self.state:
            case State.OFF:
                if letter == "power":
                    self.state = State.LOCKED
                else:
                    self.state = State.BIN
            case State.LOCKED:
                match letter:
                    case "power":
                        self.state = State.OFF
                    case "keycard":
                        self.state = State.UNLOCKED
                    case _:
                        self.state = State.BIN
            case State.UNLOCKED:
                match letter:
                    case "power":
                        self.state = State.OFF
                    case "keycard" | "timeout":
                        self.state = State.LOCKED
                    case "print":
                        self.state = State.PRINTING
                    case _:
                        self.state = State.BIN
            case State.PRINTING:
                match letter:
                    case "power":
                        self.state = State.OFF
                    case "keycard":
                        self.state = State.LOCKED
                    case "done":
                        self.state = State.LOCKED
                    case _:
                        self.state = State.BIN
        return self._is_accepting()


def get_sul() -> aalpy.SUL:
    return System()
