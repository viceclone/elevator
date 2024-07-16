import aioconsole
import asyncio

class Elevator:
    def __init__(self, id, floors, speed):
        self.id = id
        self.floors = floors
        self.speed = speed
        self.current_floor = 0
        self.target_floor = 0
        self.target_floors_set = set()
        self.moving = False
        self.move_trigger = asyncio.Event()
        self.stop_trigger = asyncio.Event()
        self.lock = asyncio.Lock()
    
    def should_stop(self):
        return self.target_floor == self.current_floor

    async def move(self):
        while self.current_floor != self.target_floor:
            if self.current_floor < self.target_floor:
                self.current_floor += 1
            else:
                self.current_floor -= 1
            print(f'Elevator {self.id} is at floor {self.current_floor}')
            await asyncio.sleep(1 / self.speed)

        async with self.lock:
            self.target_floors_set.remove(self.target_floor)
            self.target_floor = min(self.target_floors_set) if self.target_floors_set else self.current_floor

        print(f'--Elevator {self.id} has arrived at floor {self.current_floor}')

        if not self.target_floors_set:
            self.move_trigger.clear()

    def update_target_floor(self, new_target_floor):
        self.target_floors_set.add(new_target_floor)
        if self.current_floor < new_target_floor and new_target_floor < self.target_floor:
            self.target_floor = new_target_floor
        elif self.current_floor > new_target_floor and new_target_floor > self.target_floor:
            self.target_floor = new_target_floor
        elif self.current_floor == self.target_floor:
            self.target_floor = new_target_floor

    async def add_new_target_floor(self, floor):
        async with self.lock:
            self.update_target_floor(floor)
            if not self.move_trigger.is_set():
                self.move_trigger.set()

    async def run(self):
        while True:
            await self.move_trigger.wait()
            # self.target_floor = self.target_floors_set.pop(0)
            await self.move()

class ControlCenter:
    def __init__(self, elevators):
        self.elevators = elevators
        self.elevator_tasks = []

    async def add_new_target_floor(self, elevator_id, floor):
        await self.elevators[elevator_id].add_new_target_floor(floor)
    
    async def call_elevator(self, floor):
        closest_distance = float('inf')
        # get the closest elevator
        for i, elevator in enumerate(self.elevators):
            distance = abs(elevator.current_floor - floor)
            if distance < closest_distance:
                closest_distance = distance
                closest_elevator = i
        self.elevators[closest_elevator].add_new_target_floor(floor)
        # add the target floor to the elevator
        pass

    def parse_command(self, raw_command):
        # rawcommand: <elevator_id> <floor>
        elevator_id, floor = raw_command.split()
        # cast to int
        return int(elevator_id), int(floor)

    async def run_command_board(self):
        stdin, stdout = await aioconsole.get_standard_streams()
        async for line in stdin:
            elevator_id, floor = self.parse_command(line)
            await self.add_new_target_floor(elevator_id, floor)
            stdout.write(line)

    async def run(self):
        async with asyncio.TaskGroup() as group:
            task = group.create_task(self.run_command_board())
            for elevator in self.elevators:
                task = group.create_task(elevator.run())
                self.elevator_tasks.append(task)


async def main():
    elevator0 = Elevator(0, 10, 0.5)
    elevator1 = Elevator(1, 10, 0.5)
    control_center = ControlCenter([elevator0, elevator1])
    await control_center.run()

if __name__ == '__main__':
    asyncio.run(main())
