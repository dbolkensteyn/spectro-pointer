import rpyc
import numpy as np
from lights import *
from random import randint

controller = rpyc.connect("127.0.0.1", 8003, config = {"allow_public_attrs": True, "allow_pickle": True})

state = {}

while True:
    tracked_lights, im = controller.root.get()
    im = np.fromstring(im, dtype = np.uint8).reshape((480, 640, 3))

    # Purge old lights state
    guids = [tracked_light["guid"] for tracked_light in tracked_lights]
    new_state = {}
    for guid in state:
        if guid in guids:
            new_state[guid] = state[guid]
    state = new_state

    # Assign a random color to new lights
    new_lights = 0
    for tracked_light in tracked_lights:
        light_state = state.get(tracked_light["guid"])
        if light_state == None:
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            state[tracked_light["guid"]] = color
            new_lights += 1

    # Show all detected lights
    for tracked_light in tracked_lights:
        light = tracked_light["light"]
        color = state.get(tracked_light["guid"])
        cv2.circle(im, (light.x, light.y), 15, color, 3)

    print "Showing " + str(len(state)) + " lights, " + str(new_lights) + " of which are new"

    cv2.imshow("foo", im)
    cv2.waitKey(100)
