import asyncio
from enum import Enum

class Direction(Enum):
        UP = 1
        DOWN = -1

class Elevator:
    class State(Enum):
        IDLE = 0
        STOPPED = 1
        MOVING = 2
    
    def __init__(self, id, floors, speed):
        self.id = id
        self.floors = floors
        self.speed = speed
        self.current_floor = 0
        self.state = Elevator.State.IDLE
        self.current_direction = Direction.UP
        self.current_destination = None
        self.destination_floors = set()
        self.new_destination_event = asyncio.Event()
        self.lock = asyncio.Lock()
    
    def __str__(self):
        dir = 'UP' if self.current_direction == Direction.UP else 'DOWN'
        door = 'OPEN' if self.state == Elevator.State.STOPPED else 'CLOSED'
        return f'{self.id}|floor:{self.current_floor}|dir:{dir}|door:{door}'
    
    # Function to fetch the newly added destination
    async def fetch_new_destination(self):
        while True:
            # Wait for the new destination event to be set
            await self.new_destination_event.wait()
            async with self.lock:
                self.set_next_destination()
                self.new_destination_event.clear()
    
    # Function to set the next destination
    def set_next_destination(self):
        # If the current destination is not None, add it to back the set of destination floors for later processing
        if self.current_destination != None:
            self.destination_floors.add(self.current_destination)

        # If the elevator is going up, get the next upper floor as the destination
        # If there are no upper floors, change the direction to down and get the next lower floor as the destination
        if self.current_direction == Direction.UP:
            upper_floors = [floor for floor in self.destination_floors if floor > self.current_floor]
            if upper_floors:
                self.current_destination = min(upper_floors)
            else:
                self.current_direction = Direction.DOWN
                lower_floors = [floor for floor in self.destination_floors if floor < self.current_floor]
                if lower_floors:
                    self.current_destination = max(lower_floors)
        # If the elevator is going down, get the next lower floor as the destination
        # If there are no lower floors, change the direction to up and get the next upper floor as the destination
        else:
            lower_floors = [floor for floor in self.destination_floors if floor < self.current_floor]
            if lower_floors:
                self.current_destination = max(lower_floors)
            else:
                self.current_direction = Direction.UP
                upper_floors = [floor for floor in self.destination_floors if floor > self.current_floor]
                if upper_floors:
                    self.current_destination = min(upper_floors)
        
        self.destination_floors.remove(self.current_destination)

    # Function to add a new destination to the set of destination floors and trigger the new destination event
    async def add_new_destination(self, floor):
        async with self.lock:
            self.destination_floors.add(floor)
            self.new_destination_event.set()

    # Function to set the elevator to idle state
    async def idle(self):
        print(f'Elevator {self.id} is idle')
        self.state = Elevator.State.IDLE
        await self.new_destination_event.wait()
        await self.move()

    # Function to set the elevator to moving state
    # The elevator will move to the next floor until it reaches the current destination
    async def move(self):
        self.state = Elevator.State.MOVING
        while self.current_floor != self.current_destination:
            async with self.lock:
                if self.current_floor < self.current_destination:
                    self.current_floor += 1
                else:
                    self.current_floor -= 1
                print(f'Elevator {self.id} is at floor {self.current_floor}')
            await asyncio.sleep(1 / self.speed)
        await self.stop()

    # Function to set the elevator to stop state
    # The elevator will remain stopped for 5 seconds before moving to the next destination (if any)
    async def stop(self):
        print(f'--Elevator {self.id} has arrived at floor {self.current_floor}')
        print(f'--The door of {self.id} will remain open for 5 seconds')
        self.state = Elevator.State.STOPPED
        self.current_destination = None

        await asyncio.sleep(5)
        print(f'--The door of {self.id} is closing')
        if self.destination_floors:
            self.set_next_destination()
            await self.move()
        else:
            await self.idle()

    # Function to run the elevator
    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.fetch_new_destination())
            tg.create_task(self.idle())
    
