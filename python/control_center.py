from elevator import Elevator, Direction
from commands import CallCommand, GotoCommand

import asyncio
import aioconsole

class ControlCenter:
    def __init__(self, elevators = []):
        self.elevators = elevators

    def add_elevator(self, elevator):
        self.elevators.append(elevator)

    async def call(self, floor, direction):
        elevator = self.get_elevator(floor, direction)
        print(elevator.id)
        await elevator.add_new_destination(floor)

    async def goto(self, elevator_id, floor):
        await self.elevators[elevator_id].add_new_destination(floor)

    def get_elevator(self, floor, direction):
        # First, prioritize elevators that are idle
        distance = {i:abs(elevator.current_floor - floor) for i, elevator in enumerate(self.elevators) if elevator.state == Elevator.State.IDLE}
        if distance:
            return self.elevators[min(distance, key = distance.get)]
        
        # If all elevators are busy, prioritize elevators that are moving in the same direction
        distance = {i:abs(elevator.current_floor - floor) for i, elevator in enumerate(self.elevators) if elevator.current_direction == direction}
        if distance:
            return self.elevators[min(distance, key = distance.get)]
        
        # If all elevators are moving in the opposite direction, prioritize the closest elevator
        distance = {i:abs(elevator.current_floor - floor) for i, elevator in enumerate(self.elevators)}
        return self.elevators[min(distance, key = distance.get)]
    
    def parse_command(self, raw_command):
        command_args = raw_command.decode('UTF-8').split()
        print(command_args)
        if command_args[0] == 'call':
            if command_args[2] == 'up':
                return CallCommand(int(command_args[1]), Direction.UP)
            elif command_args[2] == 'down':
                return CallCommand(int(command_args[1]), Direction.DOWN)
        elif command_args[0] == 'goto':
            return GotoCommand(int(command_args[1]), int(command_args[2]))
        else:
            return None
    
    async def process_command(self, command):
        if isinstance(command, CallCommand):
            print("call")
            await self.call(command.floor, command.direction)
        elif isinstance(command, GotoCommand):
            print("goto")
            await self.goto(command.elevator_id, command.floor)
        else:
            print("Invalid command")

    async def run_command_board(self):
        stdin, stdout = await aioconsole.get_standard_streams()
        async for line in stdin:
            command = self.parse_command(line)
            await self.process_command(command)
            stdout.write(line)
    
    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_command_board())
            for elevator in self.elevators:
                tg.create_task(elevator.run())