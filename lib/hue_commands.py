from lib.hue_command_controller import HueCommand
from phue import Group
from uuid import uuid4
from curses import napms
from threading import Thread
from time import sleep

room_group_id = "Linus Room"

# Light presets
sunrise_hue = 5000
yellow_hue = 10000
green_hue = 18200
cyan_hue = 33200
blue_hue = 43500
purple_hue = 51000
pink_hue = 56500
red_hue = 65534

# Default options
default_transitiontime = 2

# Light constants
min_hue = 0
max_hue = 65534
min_sat = 0
max_sat = 254
min_bri = 0
max_bri = 254

cycle_locks = []
new_cycle_locks = []

def register_hue_commands(hue_command_controller):
    """Registers all commands to a hue command controller."""
    hcc = hue_command_controller # Shortened name for legibility

    # Ensure there are no more than 8 per category.
    # If greather than 8, all will not fit on command simulator page.

    # This function will be registered to be called when the hue command controller executes a command.
    # This will clear the cycle lock which stops all animated effects.
    def on_command_executed(command): 
        """Clears the cycle lock.
        This will make all cycle commands stop when this function is executed."""
        cycle_locks.clear()
        cycle_locks.extend(new_cycle_locks)
        new_cycle_locks.clear()

    hcc.register_callback(on_command_executed)

    hcc.register_command(HueCommand(0, 0, 260, "Set room to on.",                   hue_set_all_on))
    hcc.register_command(HueCommand(1, 0, 260, "Set room to off.",                  hue_set_all_off))
    hcc.register_command(HueCommand(2, 0, 260, "Set room to a high brightness.",    hue_set_all_high_bri))
    hcc.register_command(HueCommand(3, 0, 260, "Set room to a medium brightness.",  hue_set_all_medium_bri))
    hcc.register_command(HueCommand(4, 0, 260, "Set room to a low brightness.",     hue_set_all_low_bri))

    hcc.register_command(HueCommand(0, 0, 261, "Set room to white.",    hue_set_all_white))
    hcc.register_command(HueCommand(1, 0, 261, "Set room to yellow.",   hue_set_all_yellow))
    hcc.register_command(HueCommand(2, 0, 261, "Set room to green.",    hue_set_all_green))
    hcc.register_command(HueCommand(3, 0, 261, "Set room to cyan.",     hue_set_all_cyan))
    hcc.register_command(HueCommand(4, 0, 261, "Set room to blue.",     hue_set_all_blue))
    hcc.register_command(HueCommand(5, 0, 261, "Set room to purple.",   hue_set_all_purple))
    hcc.register_command(HueCommand(6, 0, 261, "Set room to pink.",     hue_set_all_pink))
    hcc.register_command(HueCommand(7, 0, 261, "Set room to red.",      hue_set_all_red))

    hcc.register_command(HueCommand(0, 0, 262, "Full room rainbow effect.",             hue_rainbow_cycle))
    hcc.register_command(HueCommand(1, 0, 262, "Light that 'moves' across the room.",   hue_moving_light))
    hcc.register_command(HueCommand(2, 0, 262, "Police siren.",                         hue_police_siren))

    hcc.register_command(HueCommand(0, 0, 263, "Sunrise.",                              hue_sunrise))
    hcc.register_command(HueCommand(1, 0, 263, "Flash green.",                          hue_flash_green))
    hcc.register_command(HueCommand(2, 0, 263, "Flash blue and fade out.",              hue_flash_blue_and_fade))
    hcc.register_command(HueCommand(3, 0, 263, "Flash red and fade out.",               hue_flash_red_and_fade))

# Simple on and off
def hue_set_all_off(b): Group(b, room_group_id).on = False
def hue_set_all_on(b): Group(b, room_group_id).on = True
def hue_set_all_high_bri(b): _set_group_bri(b, room_group_id, max_bri)
def hue_set_all_medium_bri(b): _set_group_bri(b, room_group_id, 120)
def hue_set_all_low_bri(b): _set_group_bri(b, room_group_id, 50)

# Set full room colour
def hue_set_all_white(b):   _set_group_bri_hue_sat(b, room_group_id, max_bri, 0, 0)
def hue_set_all_yellow(b):  _set_group_bri_hue_sat(b, room_group_id, max_bri, yellow_hue, max_sat)
def hue_set_all_green(b):   _set_group_bri_hue_sat(b, room_group_id, max_bri, green_hue, max_sat)
def hue_set_all_cyan(b):    _set_group_bri_hue_sat(b, room_group_id, max_bri, cyan_hue, max_sat)
def hue_set_all_blue(b):    _set_group_bri_hue_sat(b, room_group_id, max_bri, blue_hue, max_sat)
def hue_set_all_purple(b):  _set_group_bri_hue_sat(b, room_group_id, max_bri, purple_hue, max_sat)
def hue_set_all_pink(b):    _set_group_bri_hue_sat(b, room_group_id, max_bri, pink_hue, max_sat)
def hue_set_all_red(b):     _set_group_bri_hue_sat(b, room_group_id, max_bri, red_hue, max_sat)

# Effects
def hue_rainbow_cycle(b):
    lock = uuid4()
    new_cycle_locks.extend([lock])

    def cycle():
        hue = 0

        while lock_is_valid(lock):
            hue += 13000
            if (hue > max_hue): hue -= max_hue
            _set_group_bri_hue_sat_trans(b, room_group_id, max_bri, hue, max_sat, 30)
            sleep(3)
         
    t = Thread(target=cycle)
    t.daemon = True
    t.start()

def hue_moving_light(b):
    lock = uuid4()
    new_cycle_locks.extend([lock])

    def cycle():
        g = Group(b, room_group_id)
        i = 0
        lights = g.lights

        while lock_is_valid(lock):
            i += 1
            if (i >= len(lights)): i = 0

            g.transitiontime = default_transitiontime

            for j, light in enumerate(lights):
                light.on = i == j
            
            sleep(1)
         
    t = Thread(target=cycle)
    t.daemon = True
    t.start()

def hue_police_siren(b):
    lock = uuid4()
    new_cycle_locks.extend([lock])

    def cycle():
        g = Group(b, room_group_id)
        i = 0
        lights = g.lights

        while lock_is_valid(lock):
            i += 1
            if (i > 1): i = 0

            g.transitiontime = default_transitiontime

            for j, light in enumerate(lights):
                light.on = True
                light.transitiontime = 0
                light.brightness = max_bri
                light.saturation = max_sat

                if j % 2 == i:
                    light.hue = red_hue
                else:
                    light.hue = blue_hue
                
            sleep(0.8)
         
    t = Thread(target=cycle)
    t.daemon = True
    t.start()

def hue_sunrise(b):
    _set_group_bri_hue_sat_trans(b, room_group_id, min_bri, sunrise_hue, max_sat, 0)
    _set_group_bri_hue_sat_trans(b, room_group_id, max_bri, sunrise_hue, max_sat, 70)

def hue_flash_green(b):
    _set_group_bri_hue_sat_trans(b, room_group_id, max_bri, green_hue, max_sat, 0)
    _set_group_bri_hue_sat_trans(b, room_group_id, min_bri, green_hue, max_sat, 30)

def hue_flash_blue_and_fade(b):
    _set_group_bri_hue_sat_trans(b, room_group_id, max_bri, blue_hue, max_sat, 0)
    _set_group_bri_hue_sat_trans(b, room_group_id, min_bri, blue_hue, max_sat, 35)

def hue_flash_red_and_fade(b):
    _set_group_bri_hue_sat_trans(b, room_group_id, max_bri, red_hue, max_sat, 0)
    _set_group_bri_hue_sat_trans(b, room_group_id, min_bri, red_hue, max_sat, 50)

# Internal util methods
def lock_is_valid(lock):
    return lock in cycle_locks or lock in new_cycle_locks

def _set_group_bri_hue_sat_trans(bridge, group_id, bri, hue, sat, trans):
    g = Group(bridge, group_id)
    g.transitiontime = trans
    g.on = True
    g.brightness = bri
    g.hue = hue
    g.saturation = sat

def _set_group_bri_hue_sat(bridge, group_id, bri, hue, sat):
    _set_group_bri_hue_sat_trans(bridge, group_id, bri, hue, sat, default_transitiontime)

def _set_group_bri(bridge, group_id, bri):
    g = Group(bridge, group_id)
    g.transitiontime = default_transitiontime
    g.on = True
    g.brightness = bri