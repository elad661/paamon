# Base sink for Paamon
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
from ..notification import PaamonNotification


class BaseSink(object):
    """ Base classs for Paamon sink objects.
        Sinks should implement at least the basic `trigger()` method.

        It is expceted that trigger won't block the broker. Sinks can use
        threads if needed.
    """
    def __init__(self):
        self.active_notifications = set()

    def setup(self):
        """ Setup this sink. Returns True on success """
        pass

    def stop(self):
        """ Stop this sink """
        pass

    def trigger(self, notification: PaamonNotification, action: str):
        """ Trigger this sink on added or removed notifcation """
        if action == 'add':
            self.active_notifications.add(notification)
        else:
            self.active_notifications.remove(notification)
