import time
from dataclasses import dataclass

from Programs.program import Program
from time import sleep

from starTracker import StarTracker


@dataclass
class DirectionCommand:
    # TODO: limit dir_x and dir_y to [-100, 100]
    dir_x: int = 0
    dir_y: int = 0


class Manual(Program):
    """
    @param: star_tracker - The star tracker object to operate on
    @param: velocity - The speed to move the star tracker in, in degrees per second
    """

    def __init__(self, star_tracker: StarTracker, velocity: float = 1):
        self.star_tracker = star_tracker
        self._velocity = velocity
        self._target_dir = DirectionCommand
        # self._last_move_time = time.time()
        super().__init__()

    def handle_command(self, command: DirectionCommand):
        self._target_dir = command

    def execute(self):
        # TODO: calculate speed based on time since last execution?
        rel_x, rel_y = self._target_dir.dir_x * self._velocity, self._target_dir.dir_y * self._velocity
        self.star_tracker.go_relative(rel_x, rel_y, self.cancellation_event)

    def _time_since_last_move(self) -> float:
        diff = time.time() - self._last_move_time
        self._last_move_time = time.time()
        return diff
