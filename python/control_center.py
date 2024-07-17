import asyncio
import aioconsole
from elevator import Elevator

class ControlCenter:
    def __init__(self, elevators = []):
        self.elevators = elevators

    def add_elevator(self, elevator):
        self.elevators.append(elevator)

    def call(self, floor):
        elevator = self.get_elevator(floor)
        elevator.add_new_destination(floor)
        pass

    def goto(self, elevator_id, floor):
        self.elevators[elevator_id].add_new_destination(floor)

    def get_elevator(self, floor):
        # TODO: implement the logic to get the best elevator
        return self.elevators[0]
    
    def parse_command(self, raw_command):
        # rawcommand: <elevator_id> <floor>
        elevator_id, floor = raw_command.split()
        # cast to int
        return int(elevator_id), int(floor)

    async def run_command_board(self):
        stdin, stdout = await aioconsole.get_standard_streams()
        async for line in stdin:
            elevator_id, floor = self.parse_command(line)
            await self.elevators[elevator_id].add_new_destination(floor)
            stdout.write(line)
    
    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_command_board())
            for elevator in self.elevators:
                tg.create_task(elevator.run())