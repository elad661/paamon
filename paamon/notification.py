# notification.py
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

from typing import Optional


class PaamonNotification(object):
    def __init__(self, source: str, title: str, identifier: Optional[str]=None):
        self.source: str = source
        self.title: str = title
        self.identifier: str = identifier
        """ Any useful identifier to differentiate this notification from others """

    def __hash__(self):
        return hash((self.source, self.title, self.identifier))

    def __repr__(self):
        return f"<PaamonNotification from {self.source}, '{self.title}' ({self.identifier}) at {hex(id(self))}>"
