#!/usr/bin/env python

import pygame
import serial
import proto

from mappings import KEYMAP
from keymap import pico_to_pygame

def get_keymap():
    pygame_to_pico = dict()
    for key in KEYMAP.keys():
        if key in pico_to_pygame:
            pygame_to_pico[ pico_to_pygame[key] ] = key
    return pygame_to_pico

def check_state(r):
    if r[0] != 0x34:
        print("Wrong magic, out of sync.")
    if not proto.check_response(r):
        print("Failed CRC")
        raise ValueError("failed crc")
    
    code = r[1]
    if len(r) > 4:
        status = r[1:4]
    else:
        status = r[1] << 16
    reset_required = r[1] & 0b01000000
    if reset_required:
        print("Reset required?")
    online = True
    return status

def read_resp(r):
    # 34829b02000095f2
    state = r[1:4]
    pong = r[1]
    outputs1 = r[2]
    outputs2 = r[3]
    online = True
    
    keyboard_outputs: dict = {"available": [], "active": ""}
    mouse_outputs: dict = {"available": [], "active": ""}

    # get_active_mouse(outputs1)
    active_keyboard_codes = ["disabled", "usb", None, "ps2"]
    active_mouse_codes = {0: "disabled",
                          0b00001000: "usb",
                          0b00010000: "usb_rel",
                          0b00011000: "ps2",
                          0b00100000: "usb_win98"
                          }
    active_mouse = active_mouse_codes[outputs1 & 0b00111000]
    absolute = not active_mouse in ["usb_rel", "ps2"]


    if outputs1 & 0b10000000:  # Dynamic
        if outputs2 & 0b00000001:  # USB
            keyboard_outputs["available"].append("usb")
            mouse_outputs["available"].extend(["usb", "usb_rel"])

        if outputs2 & 0b00000100:  # USB WIN98
            mouse_outputs["available"].append("usb_win98")

        if outputs2 & 0b00000010:  # PS/2
            keyboard_outputs["available"].append("ps2")
            mouse_outputs["available"].append("ps2")

        if keyboard_outputs["available"]:
            keyboard_outputs["available"].append("disabled")

        if mouse_outputs["available"]:
            mouse_outputs["available"].append("disabled")

        active_keyboard = active_keyboard_codes[outputs1 & 0b00000011]
        if active_keyboard in keyboard_outputs["available"]:
            keyboard_outputs["active"] = active_keyboard

        if active_mouse in mouse_outputs["available"]:
            mouse_outputs["active"] = active_mouse
    return {
            "online": online,
            "connected": (bool(outputs2 & 0b01000000) if outputs2 & 0b10000000 else None),
            "keyboard": {
                "online": (online and not (pong & 0b00001000)),
                "leds": {
                    "caps":   bool(pong & 0b00000001),
                    "scroll": bool(pong & 0b00000010),
                    "num":    bool(pong & 0b00000100),
                },
                "outputs": keyboard_outputs,
            },
            "mouse": {
                "online": (online and not (pong & 0b00010000)),
                "absolute": absolute,
                "outputs": mouse_outputs,
            },
        }


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))


s = serial.Serial('/dev/serial/by-id/usb-PiKVM_PiKVM_HID_Bridge_E66180101745C339-if00')

s.timeout = 1
s.write(proto.REQUEST_PING)

resp = s.read(8)
check_state(resp)
resp = s.read()

key_map = get_keymap()


pygame.init()

clock = pygame.time.Clock()

font = pygame.font.Font(None, 30)

black = (0,0,0)
white = (255,255,255)
def draw():
    screen.fill( black )
    if state["online"]:
        text = font.render("Num", True, white)
        screen.blit(text, (116,25))
        text = font.render("Caps", True, white)
        screen.blit(text, (172,25))
        text = font.render("Scroll", True, white)
        screen.blit(text, (245,25))
        if state["keyboard"]["leds"]["num"]:
            pygame.draw.rect(screen, (0,255,0), ((119,6), (31,13)))
        if state["keyboard"]["leds"]["caps"]:
            pygame.draw.rect(screen, (0,255,0), ((183,6), (31,13)))
        if state["keyboard"]["leds"]["scroll"]:
            pygame.draw.rect(screen, (0,255,0), ((259,6), (31,13)))

    pygame.display.update()


run = True
pygame.display.set_caption = "Pico-HID Bridge"

pygame.mouse.set_visible(False)
mousebuttons = [ "", "left", "middle", "right", "up", "down"]

last_status = -1000
state = {"online": False}
while run:
    clock.tick(30)
    # Check status with a ping:
    if pygame.time.get_ticks() > last_status + 200:
        s.write(proto.REQUEST_PING)
        s.flush()
        resp = s.read(8)
        check_state(resp)
        state = read_resp(resp)
        last_status = pygame.time.get_ticks()
        if state["mouse"]["absolute"]:
            pygame.event.set_grab(True)
            pygame.event.set_keyboard_grab(True)


    # In case we forget to read the response:
    if s.in_waiting > 0:
        resp = s.read(s.in_waiting)
        print("Got leftover data: {%i}" % len(resp))

    # Get mouse and keyboard events
    for event in pygame.event.get():
        if (event.type == pygame.MOUSEMOTION):
            if state["mouse"]["absolute"]:
                pygame.mouse.set_pos((WIDTH/2, HEIGHT/2  ))
            s.write(proto.MouseRelativeEvent( event.rel[0], event.rel[1] ).make_request())
            s.flush()
            resp = s.read(8)
            check_state(resp)

        if (event.type == pygame.KEYDOWN  or event.type == pygame.KEYUP):
            if event.key == pygame.K_SCROLLLOCK:
                run = False
            elif event.key in key_map:
                s.write(proto.KeyEvent( key_map[event.key], event.type == pygame.KEYDOWN ).make_request() )
                s.flush()
                resp = s.read(8)
                check_state(resp)
            else:
                run = False
        if (event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN):
            if event.button < len(mousebuttons):
                s.write( proto.MouseButtonEvent( mousebuttons[event.button], (event.type == pygame.MOUSEBUTTONDOWN)).make_request())
                s.flush()
                resp = s.read(8)
                check_state(resp)
        if event.type == pygame.QUIT:
            run = False
    draw()
