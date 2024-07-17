import asyncio
from enum import Enum

class Elevator:
    class State(Enum):
        IDLE = 0
        STOPPED = 1
        MOVING = 2
    
    class Direction(Enum):
        UP = 1
        DOWN = -1
    
    def __init__(self, id, floors, speed):
        self.id = id
        self.floors = floors
        self.speed = speed
        self.current_floor = 0
        self.state = Elevator.State.IDLE
        self.current_direction = Elevator.Direction.UP
        self.current_destination = 0
        self.destination_floors = set()
        self.new_destination_event = asyncio.Event()
        self.lock = asyncio.Lock()
    
    async def fetch_new_destination(self):
        while True:
            await self.new_destination_event.wait()
            async with self.lock:
                self.set_next_destination()
                self.new_destination_event.clear()
    
    def set_next_destination(self):
        if self.current_direction == Elevator.Direction.UP:
            upper_floors = [floor for floor in self.destination_floors if floor > self.current_floor]
            if upper_floors:
                self.current_destination = min(upper_floors)
            else:
                self.current_direction = Elevator.Direction.DOWN
                lower_floors = [floor for floor in self.destination_floors if floor < self.current_floor]
                if lower_floors:
                    self.current_destination = max(lower_floors)
        else:
            lower_floors = [floor for floor in self.destination_floors if floor < self.current_floor]
            if lower_floors:
                self.current_destination = max(lower_floors)
            else:
                self.current_direction = Elevator.Direction.UP
                upper_floors = [floor for floor in self.destination_floors if floor > self.current_floor]
                if upper_floors:
                    self.current_destination = min(upper_floors)
    
    async def add_new_destination(self, floor):
        async with self.lock:
            self.destination_floors.add(floor)
            self.new_destination_event.set()

    async def stop(self):
        print(f'--Elevator {self.id} has arrived at floor {self.current_floor}')
        self.state = Elevator.State.STOPPED
        self.destination_floors.remove(self.current_destination)
        if self.destination_floors:
            self.set_next_destination()
            await self.move()
        else:
            await self.idle()

    async def move(self):
        self.state = Elevator.State.MOVING
        # TODO: Implement the move method
        while self.current_floor != self.current_destination:
            async with self.lock:
                if self.current_floor < self.current_destination:
                    self.current_floor += 1
                else:
                    self.current_floor -= 1
                print(f'Elevator {self.id} is at floor {self.current_floor}')
            await asyncio.sleep(1 / self.speed)
        await self.stop()

    async def idle(self):
        print(f'Elevator {self.id} is idle')
        self.state = Elevator.State.IDLE
        await self.new_destination_event.wait()
        await self.move()

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.fetch_new_destination())
            tg.create_task(self.idle())
    
