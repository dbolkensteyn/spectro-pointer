import cv2
import xmlrpclib
import time
from random import randint

from lights import *
from camera import Camera

MOTORES_IP = '192.168.0.100'
ELEVATION_STEPS = 4

camera = Camera()
azimuth_controller = xmlrpclib.ServerProxy('http://' + MOTORES_IP + ':8000')
elevation_controller = xmlrpclib.ServerProxy('http://' + MOTORES_IP + ':8001')
detector = LightDetector()

class LightState:
    def __init__(self, color):
        self.in_tracking = False
        self.tracked = False
        self.color = color

def is_in_range(light):
    return light.x > 160 and light.x < 520 and light.y > 120 and light.y < 360

def process():
    im = camera.capture_frame()
    lights = detector.detect(im)

    tracker = LightTracker()
    tracker.track(lights)

    for light in lights:
        if is_in_range(light):
            color = (randint(100, 255), randint(100, 255), randint(100, 255))
            light_state = LightState(color)

    while True:
        im = camera.capture_frame()
        lights = detector.detect(im)
        tracker.track(lights)

        light_to_follow = None

        # Find back the light we are currently tracking
        for light in lights:
            light_state = tracker.get(light)
            if light_state != None and light_state.in_tracking:
                light_to_follow = light
                break

        # If none, find a next light to track
        if light_to_follow == None:
            for light in lights:
                light_state = tracker.get(light)
                if light_state != None and not light_state.tracked:
                    light_to_follow = light
                    light.in_tracking = True
                    break

        # If still none, we are done with this part of the scan
        if light_to_follow == None:
            break

        # Are we done tracking the current light
        x = light_to_follow.x
        e = x - 320
        if (abs(e) < 3):
            light_to_follow.tracked = True
            continue

        # Get closer to the light's center
        steps = 20
        if e < -1:
            print "Light is on the left @ " + str(x) + " & error = " + str(e)
            azimuth_controller.move(True, steps)
            print "New position: " + str(azimuth_controller.position()) + ", moved by " + str(steps) + " steps"
        elif e > 1:
            print "Light is on the right @ " + str(x) + " & error = " + str(e)
            azimuth_controller.move(False, steps)
            print "New position: " + str(azimuth_controller.position()) + ", moved by " + str(steps) + " steps"

        # Show the current image
        for light in lights:
            light_state = tracker.get(light)
            if light_state != None:
                thickness = 7 if light.is_in_tracking else 3
                cv2.circle(im, (light.x, light.y), 15, light_state.color, thickness)

        cv2.imshow("live", im)
        cv2.waitKey()

def scan():
    for elevation in range(0, ELEVATION_STEPS):
        elevation_controller.move_to(elevation*(1.0 / ELEVATION_STEPS) + (1.0 / ELEVATION_STEPS) / 2.0)
        for azimuth in range(0, azimuth_controller.total_steps(), 480):
            azimuth_controller.move(True, 480)
            print "Azimuth: " + str(azimuth_controller.position()) + " Elevation: " + str(elevation_controller.position())
            process();

while True:
    scan()

quit()

while True:
    im = camera.capture_frame()
    lights = detector.detect(im)

    for light in lights:
        cv2.circle(im, (light.x, light.y), 15, (0, 0, 255))

        if len(lights) != 1:
            continue

        x = lights[0].x
        e = x - 320

        if (abs(e) < 3):
            steps = 1
        elif (abs(e) < 10):
            steps = 5
        elif (abs(e) < 15):
            steps = 10
        elif (abs(e) < 20):
            steps = 20
        elif (abs(e) < 50):
            steps = 50
        elif (abs(e) < 100):
            steps = 100
        else:
            steps = 500

        if e < -1:
            print "Light is on the left @ " + str(x) + " & error = " + str(e)
            azimuth_controller.move(True, steps)
            print "New position: " + str(azimuth_controller.position()) + ", moved by " + str(steps) + " steps"
        elif e > 1:
            print "Light is on the right @ " + str(x) + " & error = " + str(e)
            azimuth_controller.move(False, steps)
            print "New position: " + str(azimuth_controller.position()) + ", moved by " + str(steps) + " steps"
        else:
            print "Light is centered! @ " + str(x) + " & error = " + str(e)

    cv2.imshow("live", im)
    cv2.waitKey(100)
