from elevator import Direction

class Command:
    def __init__(self) -> None:
        pass

# Command is created when a user presses a button in hall of a floor
class CallCommand(Command):
    def __init__(self, floor, direction) -> None:
        print("CallCommand")
        self.floor = floor
        self.direction = direction

# Command is created when a user presses a button inside the elevator to go to a destination floor
class GotoCommand(Command):
    def __init__(self, elevator_id, floor) -> None:
        self.elevator_id = elevator_id
        self.floor = floor