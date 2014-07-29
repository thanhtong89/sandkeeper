from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ReferenceListProperty, ObjectProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from functools import partial
from kivy.config import Config
from kivy.core.audio import SoundLoader

import datetime
import subprocess
import time

SHUTDOWN_MODE = 0
HIBERNATE_MODE = 1
class DigitDisplay(Button):
    pass

class TimeDisplay(BoxLayout):
    pass

class Controller(BoxLayout):
    alarm_btn = ObjectProperty(None)
    shutdown_btn = ObjectProperty(None)

class Container(StackLayout):
    pass

class SandKeeper(App):
    day_value = NumericProperty(0)
    hour_value = NumericProperty(1)
    min_value = NumericProperty(0)
    sec_value = NumericProperty(0)
    alarm_date = StringProperty(datetime.datetime.now().strftime("%c"))
    total_secs_left = NumericProperty(3600)

    alarm_sound = SoundLoader.load('analog-alarm-clock.wav')

    # Alarm mode alarms upon time's up.
    # Shutdown simply shuts down (windows only for now?)
    alarm_selected = BooleanProperty(False)
    shutdown_selected = BooleanProperty(False)
    shutdown_modes = DictProperty({ SHUTDOWN_MODE : 'power.png',
                                    HIBERNATE_MODE : 'hibernate.png' })
    shutdown_current_mode = NumericProperty(0)
    # countdown is true iff at least an action is selected.
    countdown = BooleanProperty(False)

    def on_shutdown_touch_down(self, btn, touch):
        if (btn.collide_point(*touch.pos)):
            if (touch.button in ['scrolldown', 'scrollup']):
                self.shutdown_current_mode = (self.shutdown_current_mode + 1) % \
                                                        len(self.shutdown_modes)

    def on_display_touch_down(self, display, touch):
        if (self.countdown):
            return
        if (display.collide_point(*touch.pos)):
            delta = -1
            if (touch.button in ['scrolldown', 'left']):
                delta = 1
            newval = (int(display.value) + delta) % display.modulo
            if (display._id == 'daylabel'):
                self.day_value = newval
            elif (display._id == 'hourlabel'):
                self.hour_value = newval
            elif (display._id == 'minlabel'):
                self.min_value = newval
            else:
                self.sec_value = newval
            self.total_secs_left = self.day_value * 86400 + \
                                self.hour_value * 3600 + \
                                self.min_value * 60 + self.sec_value
            self.update_alarm_date()

    def update_counter(self):
        """ Returns total number of seconds left """
        self.total_secs_left -= 1
        self.day_value, remainder = divmod(self.total_secs_left, 86400)
        self.hour_value, remainder = divmod(remainder, 3600)
        self.min_value, self.sec_value = divmod(remainder, 60)

        return self.total_secs_left

    def check_countdown_status(self):
        self.countdown = (self.shutdown_selected or self.alarm_selected)

    def update_alarm_date(self):
        delta = datetime.timedelta(self.day_value, seconds=self.sec_value,\
                               minutes=self.min_value,hours=self.hour_value)
        self.alarm_date = (datetime.datetime.now() + delta).strftime("%c")

    def shutdown_windows(self, options):
        return subprocess.call(["shutdown.exe"] + options)

    def take_actions(self):
        if (self.alarm_selected):
            self.alarm_sound.play()
        if (self.shutdown_selected):
            if (self.shutdown_current_mode == SHUTDOWN_MODE):
               self.shutdown_windows(['/s'])
            elif (self.shutdown_current_mode == HIBERNATE_MODE):
               self.shutdown_windows(['/h'])

    def update(self):
        """ Runs every second """
        controller = self.root.ids.ctr
        if (not self.countdown):
            self.update_alarm_date()
        else:
            if (self.update_counter() == 0):
                self.take_actions()
                self.countdown = False
                controller.alarm_btn.state = 'normal'
                controller.shutdown_btn.state = 'normal'

    def build(self):
        self.container = Container()
        Clock.schedule_interval(lambda dt: self.update(), 1)
        return self.container

if __name__ == '__main__':
    Config.set('graphics', 'width', '323')
    Config.set('graphics', 'height', '200')
    Config.set("input", "mouse", "mouse,disable_multitouch")
    SandKeeper().run()
