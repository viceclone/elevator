from control_center import ControlCenter
from elevator import Elevator

import asyncio

async def main():
    control_center = ControlCenter()
    elevator1 = Elevator(1, 10, 1)
    elevator2 = Elevator(2, 10, 1)
    elevator3 = Elevator(3, 10, 1)
    control_center.add_elevator(elevator1)
    control_center.add_elevator(elevator2)
    control_center.add_elevator(elevator3)
    await control_center.run()

asyncio.run(main())