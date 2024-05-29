import logging
import logging.config
import RPi.GPIO as GPIO
from typing import Callable

from LimitSwitch.ILimitSwitch import ILimitSwitch

# To test this as an executable, run `python -m LimitSwitch.LimitSwitch`
# TODO: Test with pin 40
class LimitSwitch(ILimitSwitch):
    def __init__(self, pin: int):
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setup(pin, GPIO.IN)
        self.logger = logging.getLogger(__name__)
        GPIO.add_event_detect(pin, GPIO.RISING, bouncetime=200)

    def isActive(self) -> bool:
        value = GPIO.input(self.pin)
        # print(f'Limit Switch value: {GPIO.input(self.pin)}')
        # self.logger.info()
        return value

    def add_active_callback(self, callback: Callable):
        GPIO.add_event_callback(self.pin, callback)

if __name__ == '__main__':
    #switch = LimitSwitch(config.TURNTABLE.limit_switch.pin)
    pin = 40
    switch = LimitSwitch(pin)
    switch.add_active_callback(lambda _: print("switch press detected"))
    print(f"waiting for limit switch on pin {pin}")
    import time
    time.sleep(60)