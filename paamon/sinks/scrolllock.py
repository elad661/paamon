# scrolllock.py - Scroll Lock LED sink for Paamon
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
import pydbus


class ScrolllockLedSink(BaseSink):
    def __init__(self):
        super().__init__()
        self.should_be_blinking = False
        self.blinking = False
        self.leds = None

    def setup(self):
        """ Setup this sink. Return True on success """
        bus = pydbus.SystemBus()
        try:
            self.leds = bus.get("com.eladalfassa.LedProxy")
        except GLib.Error as e:
            if e.message.startswith('GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown'):
                # TODO proper logging
                print("led-proxy is not running")
                return False
            else:
                raise
        return True

    def stop(self):
        """ Stop this sink, turn off the LED """
        self.leds.TurnOff()
        self.should_be_blinking = False

    def trigger(self, notification: PaamonNotification, action: str):
        """ Trigger this sink on added or removed notifcation """
        super().trigger(notification, action)

        self.should_be_blinking = len(self.active_notifications) > 0
        if self.should_be_blinking and not self.blinking:
            self.blinking = True
            self.leds.Blink(500)
        elif not self.should_be_blinking:
            self.leds.TurnOff()
