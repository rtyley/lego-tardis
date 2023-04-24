import asyncio
import keypad


class Activity(object):
    def start(self):
        raise NotImplementedError("Please Implement this method")

    def handle_key(self, event: keypad.Event, coords, single_key_stuff):
        raise NotImplementedError("Please Implement this method")


class DeviceMode:
    def __init__(self, activity: Activity):
        self._current_activity = activity

    def set_activity(self, activity: Activity):
        self._current_activity = activity
        asyncio.create_task(activity.start())

    def get_activity(self) -> Activity:
        return self._current_activity
