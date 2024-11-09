# Pico-bridge


This is a minimal pygame implementation to forward keyboard and mouse events to a [PicoHID Bridge](https://docs.pikvm.org/pico_hid_bridge/).

## What is this?

The Pico is assembled and flashed with the PiKVM image, and connected to the host computer with a USB cable. 

The PiKVM PicoHID Bridge is configured same as for PiKVM, and it will be recognized by the host computer as an USB serial port, and translates that to PS/2 keyboard and mouse events with very low latency.

This script will open a pygame window to capture keyboard and mouse events, and forward them to the PicoHID Bridge, with on-screen indicators for Num lock, Caps lock and Scroll lock.

This setup is very convenient when paired with a capture card, since it allows you to use another computer without plugging a separate keyboard, mouse and screen to the other computer.

When I'm done with it, I can use it with my PiKVM, since it's the same protocol.

## How to run this:

1. Plug in the pico to your host computer with a USB cable.
2. Run `python pico-bridge.py /dev/ttyUSB0` where `/dev/ttyUSB0` is the device name of your Pico.
3. Any keyboard events in the window will be forwarded, and the mouse will be grabbed and forwarded.
4. Press scroll-lock on the keyboard to exit.


## Thanks

Thanks to Maxim Devaev and PiKVM contributors for doing all the hard work.

License: GPL v3.0 (the same as PiKVM [kvmd](https://github.com/pikvm/kvmd) where most of the code for this came from)
