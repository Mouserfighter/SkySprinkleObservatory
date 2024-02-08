from threading import Event

import RPi.GPIO as GPIO
import time
import asyncio

import config
from MotorConfig import MotorConfig
import logging
import logging.config
BACKWARD = False
FORWARD = not BACKWARD


class Motor:
    def __init__(self, motor: MotorConfig):
        self.motor = motor
        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setup(self.motor.step_pin, GPIO.OUT)
        GPIO.setup(self.motor.direction_pin, GPIO.OUT)
        if self.motor.enable_pin:
            GPIO.setup(self.motor.enable_pin, GPIO.OUT)
            GPIO.output(self.motor.enable_pin, GPIO.LOW)  # Enable the motor
        # Initialize ENABLE pin
        self.current_pos = 0
        self.logger = logging.getLogger(__name__)

        self.stop_event = Event()  # Use an event for signaling
        """
        if motor.limit_switch:
                motor.limit_switch.add_active_callback(self.stop_callback)
                motor.limit_switch.add_deactive_callback(self.start_callback)
    
    def stop_callback(self):
        self.stop_event.set()

    def start_callback(self):
        self.stop_event.clear()
        """

    def step_motor(self, steps: int, direction: bool, seconds_per_step: float = 1, check_limit=True):
        print(f"stepping {steps} steps in {direction} dir at {seconds_per_step} sps")
        #if check_limit:
        #    steps = self._limit_in_range(steps, direction)
        # Set direction
        GPIO.output(self.motor.direction_pin, GPIO.HIGH if direction else GPIO.LOW)
        # Perform steps
        for _ in range(steps):
            GPIO.output(self.motor.step_pin, GPIO.HIGH)
            GPIO.output(self.motor.step_pin, GPIO.LOW)
            self.current_pos += 1
            #print("*", end="")
            time.sleep(seconds_per_step)  # Adjust this delay for speed control

    def _limit_in_range(self, steps: int, direction: bool) -> int:
        max_steps = int(self.motor.max_angle * self.motor.degrees_per_step)

        if direction == FORWARD:
            potential_pos = self.current_pos + steps
            if potential_pos <= max_steps:
                return steps
            else:
                return max_steps - self.current_pos
        else:
            potential_pos = self.current_pos - steps
            if potential_pos >= 0:
                return steps
            else:
                return self.current_pos

    def go_to(self, angle: float, degrees_per_second=1, check_limit=True):
        seconds_per_step = self._calculate_seconds_per_step(degrees_per_second)
        step_dir = angle > 0
        if not self.motor.forward_direction:
            step_dir = not step_dir
        # TODO: rounding errors?
        self.step_motor(steps=int(abs(angle) / self.motor.degrees_per_step),
                        direction=step_dir, seconds_per_step=seconds_per_step, check_limit=check_limit)

    def zero(self):
        self.logger.debug(f'zeroing using {self.motor.limit_switch.__class__.__name__}')
        if not self.motor.limit_switch:
            pass
        while not self.motor.limit_switch.isActive():
            self.step_motor(10, not self.motor.forward_direction, seconds_per_step=self._calculate_seconds_per_step(config.zero_degrees_per_sec),
                            check_limit=False)
        self.current_pos = 0

    def _calculate_seconds_per_step(self, degrees_per_second: float):
        return self.motor.degrees_per_step / degrees_per_second

    def __del__(self):
        # Clean up 
        #GPIO.cleanup()
        # TODO: Use pull up resisters so the enable pin defaults to On
        pass


async def main():
    # Example usage
    turntable = Motor(config.TURNTABLE)
    turret = Motor(config.TURRET)
    spin = Motor(config.SPIN)
    motor = spin

    #asyncio.run(turntable.zero())
    #asyncio.run(motor.zero())
    #asyncio.run(spin.zero())
    turntable.zero()
    print("moving 10 degrees forward")
    #await motor.go_to(10, 10)
    while True:
        print("moving 90 degrees backward")
        await asyncio.gather(
            #turntable.go_to(90, 10),
            asyncio.to_thread(turntable.go_to, 90, 30),
            asyncio.to_thread(turret.go_to, -90, 30),
            asyncio.to_thread(spin.go_to, -180, 60) 
        )
        print("moving 90 degrees forward")
        await asyncio.gather(
            #turntable.go_to(90, 10),
            asyncio.to_thread(turntable.go_to, 90, 30),
            asyncio.to_thread(turret.go_to, 90, 30),
            asyncio.to_thread(spin.go_to, 180, 60) 
        )
        print("sleeping")
        time.sleep(2)

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    asyncio.run(main())