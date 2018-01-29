Pa'amon - notification bridge (WIP)
===================================
Pa'amon (פעמון) is a notification bridge. It reads notifications from a number of sources,
and can process/show them in different wayss.

The main idea is to have some sort of physical indication of pending notifications,
either by blinking a LED on your keyboard, controlling the color of a BlinkStick,
making sounds, or sending it to a Pebble watch.

**At the moment, it's in early stages and most of the functionality doesn't exist
yet.**

Planned features
----------------
* Configuration - make notifications from different sources show in your preferred way,
for example - blink for terminal command completion, but not for email.
* Simple interface for extending with custom sources/sinks
* Various sources:
  * Desktop notifications **ready**
  * GitHub notifications
  * twitter notifications
  * possibly others?
* Various sinks:
  * Blinking the scroll-lock LED **ready** (using [led-proxy](https://github.com/elad661/led-proxy))
  * BlinkStick (with configurable colors, or use a color average of the notification icon) **works** (no configuration yet)
  * Pebble watches (regular notifications)
  * Pebble watches (custom app that displays the notification icon)
  * Sound (possibly using libcanberra)
  * Mobile phone push notifications (need to figure out how to do that)
  * possibly others?

Design - sinks and sources
--------------------------
A broker object spawns `Source` objects, which can watch for notifications
either by listening on dbus, adding sources to the GLib mainloop (like idle callbacks or IO watches),
or starting their own thread to poll some web resource.

The source object sends notifications into the broker's queue,
and for each incoming notification the broker triggers all the `Sink`s.
The sink's trigger method can decide what it wants to do with the notification,
but it's expected that it won't block the broker's thread or the GLib mainloop.

The source also sends an event to the queue when a notification is removed.
