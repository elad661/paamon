# broker.py - notification broker for Paamon
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

from queue import Queue
from .sources import all_sources
from .sinks import all_sinks
import threading


class Broker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.notification_queue = Queue()
        self.running = True
        self.sources = []
        self.sinks = []

    def register_sources(self):
        for source_cls in all_sources:
            source = source_cls(self.notification_queue)
            if source.setup():
                self.sources.append(source)
        if len(self.sources) == 0:
            raise Exception("No sources!")

    def register_sinks(self):
        for sink_cls in all_sinks:
            sink = sink_cls()
            # it is expected that sink.setup() will return True if it succeeds
            if sink.setup():
                self.sinks.append(sink)
        if len(self.sinks) == 0:
            raise Exception("No sinks!")

    def stop(self):
        # stop all sinks
        for sink in self.sinks:
            sink.stop()
        self.running = False
        # Put None in the queue to get the queue watcher loop to exit
        self.notification_queue.put((None, None))

    def run(self):
        while self.running:
            notification, action = self.notification_queue.get()
            if notification is None and action is None:
                break
            for sink in self.sinks:
                sink.trigger(notification, action)
