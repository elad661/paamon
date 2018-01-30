# blinkstick.py - BlinkStick sink for Paamon
#
# Copyright © 2018 Elad Alfassa <elad@fedoraproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" scroll-lock LED sink

This is a simplistic sink that blinks the scroll-lock LED when there are
unread notifications.

It ignores any data about the notification pushed to it, and just
keeps the active notification count.

It uses https://github.com/elad661/led-proxy to control the LED.
"""
from .base import BaseSink
from ..notification import PaamonNotification
from gi.repository import GLib
try:
    from blinkstick import blinkstick
    has_blinkstick = True
except ImportError:
    has_blinkstick = False


class BlinkStickSink(BaseSink):
    def __init__(self):
        super().__init__()
        self.blinkstick = None
        self.blink_timer_id = None
        self.is_led_on = False

    def setup(self):
        """ Setup this sink. Returns True if a BlinkStick is found """
        if not has_blinkstick:
            return False
        self.blinkstick = blinkstick.find_first()
        # TODO support more than one BlinkStick (and configuration)
        if self.blinkstick is not None:
            return True

    def stop(self):
        """ Stop this sink. called by the broker """
        self.stop_timer()

    def stop_timer(self):
        """ Stop the GLib blinking timeout """
        if self.blink_timer_id is not None:
            GLib.source_remove(self.blink_timer_id)
            self.blink_timer_id = None
        self.blinkstick.set_color()  # turn LED off

    def blink(self):
        """ Blink the BlinkStick. Called by a GLib timeout"""
        if not self.should_be_blinking:
            return False
        if not self.is_led_on:
            self.blinkstick.set_color(name="purple")
            self.is_led_on = True
        else:
            self.blinkstick.set_color()  # Turn LED off
            self.is_led_on = False
        return self.should_be_blinking

    def trigger(self, notification: PaamonNotification, action: str):
        """ Trigger this sink on added or removed notifcation """
        super().trigger(notification, action)

        self.should_be_blinking = len(self.active_notifications) > 0
        if self.should_be_blinking and self.blink_timer_id is None:
            self.blink_timer_id = GLib.timeout_add(500, self.blink)
        elif not self.should_be_blinking:
            self.stop_timer()
