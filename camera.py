from picamera.array import PiRGBArray
from picamera import PiCamera

class Camera:
    SIZE = (640, 480)

    def __init__(self):
        camera = PiCamera()
        camera.resolution = SIZE
        stream = PiRGBArray(camera, size = SIZE)

    def capture_frame():
        stream.seek(0)
        stream.truncate()

        camera.capture(stream, format = 'bgr', use_video_port = True)
        return stream.array
