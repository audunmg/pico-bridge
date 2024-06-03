# Pico-bridge


This is a minimal pygame implementation to forward keyboard and mouse events to a [PicoHID Bridge](https://docs.pikvm.org/pico_hid_bridge/).

The purpose (for me) is to emulate a PS/2 keyboard and a mouse with a Pico and another computer.

The Pico is assembled and flashed with the PiKVM image, and connected to the host computer.

When I'm done with it, I can use it with my PiKVM, since it's the same protocol.

Thanks to Maxim Devaev and PiKVM contributors for doing all the hard work.

License: GPL v3.0 (the same as PiKVM [kvmd](https://github.com/pikvm/kvmd) where most of the code for this came from)