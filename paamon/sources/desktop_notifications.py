# desktop_notifications.py - Desktop notifications source for Paamon
#
# Copyright © 2018 Elad Alfaassa <elad@fedoraproject.org>
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

""" desktop notifications source

This source listens for freedestkop/gtk notifications and sends them over to Paamon
It supports both org.freedesktop.Notifications and org.gtk.Notifications.

It uses the DBus org.freedesktop.DBus.BecomeMonitor interface to monitor
the session bus for notifications.
"""
from gi.repository import Gio
from ..notification import PaamonNotification
import pydbus
import pydbus.bus


class DesktopNotificationsSource(object):
    def __init__(self, queue):
        self.queue = queue
        """ The broker's queue, to push new notifications into """
        self.active_notifications_gio = {}
        """ A dictionary tracking active GNotification notifications """
        self.active_notifications_freedesktop = []
        """ List of freedesktop notifications seen. less accurate tracking. """
        self.bus: pydbus.bus.Bus = None

    def setup(self):
        self.bus = pydbus.SessionBus()
        self.bus.get('org.freedesktop.DBus')
        match_rules = ["interface='org.freedesktop.Notifications', member='Notify'",
                       "interface='org.freedesktop.Notifications', member='NotificationClosed'",
                       "interface='org.gtk.Notifications', member='AddNotification'",
                       "interface='org.gtk.Notifications', member='RemoveNotification'"]
        self.bus.get('org.freedesktop.DBus').BecomeMonitor(match_rules, 0)
        self.bus.con.add_filter(self.handle_notification)
        return True

    def handle_gio_notification(self, member: str, method_args: list):
        """ Handle Gio notifications """
        # GNotification. For details:
        # https://developer.gnome.org/gio/stable/GNotification.html
        # https://wiki.gnome.org/HowDoI/GNotification
        # https://wiki.gnome.org/Projects/GLib/GApplication/DBusAPI#org.gtk.Notification
        uuid = method_args[1]
        if member == 'AddNotification':
            title = method_args[2]['title']
            notification = PaamonNotification("desktop_notifications",
                                              title,
                                              uuid)
            self.active_notifications_gio[uuid] = notification
            self.queue.put((notification, "add"))
        elif member == 'RemoveNotification':
            # removing a notification
            if uuid in self.active_notifications_gio:
                notification = self.active_notifications_gio[uuid]
                self.queue.put((notification, "remove"))
                del self.active_notifications_gio[uuid]

    def handle_freedesktop_notification(self, member: str, method_args: list):
        """ Handle freedesktop notification """
        # Freedesktop notifications. For details:
        # https://developer.gnome.org/notification-spec/
        if member == 'Notify':
            # adding a notification
            notification = PaamonNotification("desktop_notifications",
                                              method_args[3])
            self.active_notifications_freedesktop.append(notification)
            self.queue.put((notification, "add"))
        elif member == 'NotificationClosed':
            # removing notification.
            # TODO freedesktop notification removal is tricky.
            # the ID returned here is the ID that would've been returned
            # from the Notify method call. However, dbus doesn't show
            # method return values when using the monitoring interface.
            # Solving this might involve guessing the notification ID,
            # fixing DBus, or writing a gnome-shell extensionn - and
            # non of these options seem to be a good idea
            for notification in self.active_notifications_freedesktop:
                # hack: once one freedesktop notfication was seen,
                # assume all were seen and remove them
                self.queue.put((notification, "remove"))
                self.active_notifications_freedesktop.remove(notification)

    def handle_notification(self, connection, message: Gio.DBusMessage, incoming):
        """ Handle notifications, callback for dbus """
        args = message.get_body().unpack()
        member = message.get_member()

        if message.get_interface() == 'org.gtk.Notifications':
            self.handle_gio_notification(member, args)
        elif message.get_interface() == 'org.freedesktop.Notifications':
            self.handle_freedesktop_notification(member, args)
