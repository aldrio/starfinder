from dataclasses import dataclass
import math
import threading
import time
from .icm20948 import (
    ICM20948,
)
import numpy as np
from smbus2 import SMBus
import imufusion


@dataclass
class Orientation:
    pitch: float
    yaw: float
    roll: float


class ImuManager(threading.Thread):
    running = False

    previous_orientations = []

    orientation_lock = threading.Lock()
    orientation = Orientation(0, 0, 0)

    def __init__(self):
        super().__init__()
        self.daemon = True

        self.start()

    def get_orientation(self) -> tuple[float, float, float]:
        with self.orientation_lock:
            return self.orientation

    def run(self):
        sample_rate = 30

        try:
            bus = SMBus(1)
            time.sleep(1)
            imu = ICM20948(i2c_bus=bus, i2c_addr=0x69)

            imu.set_accelerometer_sample_rate(sample_rate)
            imu.set_gyro_sample_rate(sample_rate)

            imu.set_accelerometer_low_pass(enabled=False)
            imu.set_gyro_low_pass(enabled=False)

            imu.set_accelerometer_full_scale(16)
            imu.set_gyro_full_scale(2000)

            ahrs = imufusion.Ahrs()
            ahrs.settings = imufusion.Settings(
                imufusion.CONVENTION_NWU,
                0.5,
                2000,
                10,
                10,
                round(5.0 * sample_rate),
            )
            offset = imufusion.Offset(sample_rate)

            self.running = True
        except Exception as e:
            print(f"Failed to initialize IMU: {e}")
            self.running = False
            return

        last_tick = time.monotonic()
        while True:
            current_tick = time.monotonic()
            delta = current_tick - last_tick
            last_tick = current_tick

            mx, my, mz = imu.read_magnetometer_data()
            mag = np.array([mx, my, mz])

            ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()
            acc = np.array([ax, ay, az])
            gyro = offset.update(np.array([gx, gy, gz]))

            ahrs.update(
                gyro,
                acc,
                mag,
                delta,
            )

            euler = ahrs.quaternion.to_euler()
            roll = math.radians(-euler[1])
            pitch = math.radians(-euler[0]) + math.pi / 2
            yaw = math.radians(euler[2]) + math.pi/ 2 + math.radians(magnetic_declination)

            orientation = Orientation(pitch, yaw, roll)
            with self.orientation_lock:
                self.orientation = orientation

            target_step_time = 1 / sample_rate
            sleep_time = target_step_time - (time.monotonic() - current_tick)

            if sleep_time > 0:
                time.sleep(sleep_time)
