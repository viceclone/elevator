import asyncio

class Elevator:
    def __init__(self, floors):
        self.floors = floors
        self.current_floor = 0
        self.target_floor = 0
        self.moving = False

    async def move(self):
        self.moving = True
        while self.current_floor != self.target_floor:
            if self.current_floor < self.target_floor:
                self.current_floor += 1
            else:
                self.current_floor -= 1
            print(f'Elevator is at floor {self.current_floor}')
            await asyncio.sleep(1)
        self.moving = False

class ControlPanel:
    def __init__(self, elevators):
        self.elevators = elevators

    def add_elevator(self, elevator):
        self.elevators.append(elevator)

    async def request_floor(self, floor):
        self.elevator.target_floor = floor
        if not self.elevator.moving:
            asyncio.create_task(self.elevator.move())