import io
import threading
import time
import serial
import pynmea2


class GpsManager(threading.Thread):
    running = True
    location = None

    def __init__(self):
        super().__init__()
        self.daemon = True

        self.data_lock = threading.Lock()

        self.start()

    def get_location(self, timeout=5) -> tuple[float, float]:
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            if not self.running:
                break

            with self.data_lock:
                if self.location is not None:
                    return self.location
            time.sleep(0.1)

        # fall back to dayton, ohio
        print("Failed to get GPS location, falling back to Dayton, Ohio.")
        return 39.7589, -84.1916

    def run(self):
        try:
            ser = serial.Serial("/dev/ttyS0", 9600, timeout=1)
            dev = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        except Exception as e:
            print(f"Failed to initialize GPS: {e}")
            self.running = False
            return

        while True:
            # Read a line from the serial port
            line = dev.readline()
            if line and line.startswith("$"):
                try:
                    msg = pynmea2.parse(line)

                    if hasattr(msg, "latitude") and hasattr(msg, "longitude"):
                        with self.data_lock:
                            self.location = (msg.latitude, msg.longitude)
                except pynmea2.ParseError as e:
                    print(f"Parse error: {e}")
