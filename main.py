from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ReferenceListProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from functools import partial
from kivy.config import Config

import datetime

class DigitDisplay(Button):
    pass

class TimeDisplay(BoxLayout):
    pass

class Controller(BoxLayout):
    alarm_btn = ObjectProperty(None)
    shutdown_btn = ObjectProperty(None)

class Container(BoxLayout):
    pass

class ClockTicker(App):
    day_value = NumericProperty(0) 
    hour_value = NumericProperty(1) 
    min_value = NumericProperty(0) 
    sec_value = NumericProperty(0) 
    alarm_date = StringProperty(datetime.datetime.now().strftime("%c"))
    total_secs_left = NumericProperty(3600)

    # Alarm mode alarms upon time's up.
    # Shutdown simply shuts down (windows only for now?)
    alarm_selected = BooleanProperty(False)
    shutdown_selected = BooleanProperty(False)

    # countdown is true iff at least an action is selected.
    countdown = BooleanProperty(False)

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

    def update_counter(self):
        """ Returns total number of seconds left """
        self.total_secs_left -= 1
        self.day_value, remainder = divmod(self.total_secs_left, 86400)
        self.hour_value, remainder = divmod(remainder, 3600)
        self.min_value, self.sec_value = divmod(remainder, 60)

        return self.total_secs_left

    def check_countdown_status(self):
        self.countdown = (self.shutdown_selected or self.alarm_selected)
        print "countdown is now ", self.countdown

    def update_alarm_date(self):
        delta = datetime.timedelta(self.day_value, seconds=self.sec_value,\
                               minutes=self.min_value,hours=self.hour_value)
        self.alarm_date = (datetime.datetime.now() + delta).strftime("%c").replace(" ", "\n")
        print "alarm_date is now ", self.alarm_date

    def update(self):
        """ Runs every second """
        controller = self.root.ids.ctr
        if (not self.countdown):
            self.update_alarm_date()
        else:
            if (self.update_counter() == 0):
                print "Time's up!"
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
    ClockTicker().run()
