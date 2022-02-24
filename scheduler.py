from datetime import datetime, timedelta
from typing import Callable, Optional
from threading import Thread, Lock
from time import sleep
import logging
from loggy import setup_logger

from plyer import notification as notif # type: ignore


logger: logging.Logger = logging.getLogger()

# ScheduledEvent(call, time):
# call: Callable[[], None] is the function to be called
# time: datetime represents when the function should be called
class ScheduledEvent:
    def __init__(self: 'ScheduledEvent', call: Callable[[], None], time: datetime) -> None:
        self.call: Callable[[], None] = call
        self.time: datetime = time
        self.done: bool = False

    # ScheduledEvent()(): calls the event's call method
    def __call__(self: 'ScheduledEvent') -> None:
        logger.info(f"Calling scheduled event: {self}")
        self.done = True
        self.call()


class Scheduler:
    def __init__(self: 'Scheduler', interval: int = 15):
        self.interval = interval
        self.event_queue: list[ScheduledEvent] = []
        self.lock_queue: Lock = Lock()
        self.running: bool = True
    
    # Scheduler().schedule_event(call, time): Schedule an event to occur at a certain time. Does not block.
    # call: Callable[[], None] is the function to run at the time
    # time: datetime is the datetime object representing when to call the object
    def schedule_event(self: 'Scheduler', call: Callable[[], None], time: datetime) -> ScheduledEvent:
        new_event: ScheduledEvent = ScheduledEvent(call, time)
        with self.lock_queue:
            # Insert event at the proper position in the event queue
            inserted: bool = False
            for i, event in enumerate(self.event_queue):
                if new_event.time > event.time:
                    self.event_queue.insert(i, new_event)
                    inserted = True
                    break
            if not inserted:
                self.event_queue.append(new_event)
        return new_event

    # Scheduler().schedule_in_future(call, time): Schedule an event to occur an amount of time in the future. Does not block.
    # call: Callable[[], None] is the function to run at the time
    # time: timedelta is the amount of time that should pass before the function is run.
    def schedule_in_future(self: 'Scheduler', call: Callable[[], None], time: timedelta) -> ScheduledEvent:
        return self.schedule_event(call, datetime.now() + time)

    # Scheduler().run(): Every <interval> seconds, call all scheduled events that are ready to be called. Blocks.
    def run(self: 'Scheduler') -> None:
        logger.info(f'Scheduler started with interval {self.interval} seconds')
        self.running = True
        while True:
            sleep(self.interval)
            if not self.running:
                logger.info('Scheduler fully done')
                break
            Thread(target=self._call_scheduled_events).start()

    # Scheduler().start(): Every <interval> seconds, call all scheduled events that are ready to be called. Does not block.
    def start(self: 'Scheduler') -> None:
        logger.info('Starting scheduler daemon')
        Thread(target=self.run, daemon=True).start()

    # Scheduler().stop(): Stops the loop used in run or start(). Does not block.
    def stop(self: 'Scheduler') -> None:
        self.running = False
        logger.info('Scheduler set to shut down in a few seconds')
        
    # Scheduler()._call_scheduled_events(): Calls all events that were scheduled at some point in the past. Does not block.
    def _call_scheduled_events(self: 'Scheduler') -> None:
        logger.info('Checking for events')
        now = datetime.now()
        with self.lock_queue:
            logger.debug(self.event_queue)
            while self.event_queue and self.event_queue[-1].time < now:
                event: ScheduledEvent = self.event_queue.pop()
                Thread(target=event, daemon=True).start()
        

if __name__ == '__main__':
    setup_logger(True)
    def make_notify(msg: str) -> Callable[[], None]:
        def inner() -> None:
            notif.notify(msg)
        return inner
    sched: Scheduler = Scheduler(1)
    sched.start()
    ev: ScheduledEvent = sched.schedule_in_future(make_notify("hello"), timedelta(seconds=10))
    sleep(2)
    ev2: ScheduledEvent = sched.schedule_in_future(make_notify("hello 2"), timedelta(seconds=5))
    ev3: ScheduledEvent = sched.schedule_in_future(make_notify("hello 3"), timedelta(seconds=10))
    ev4: ScheduledEvent = sched.schedule_in_future(make_notify("hello 4"), timedelta(seconds=8))
    sleep(20)
