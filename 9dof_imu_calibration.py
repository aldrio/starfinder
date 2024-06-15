import threading
import time
import numpy as np
from smbus2 import SMBus
from icm20948 import ICM20948

SAMPLE_SIZE = 500


class KeyListener:
    """Object for listening for input in a separate thread"""

    def __init__(self):
        self._input_key = None
        self._listener_thread = None

    def _key_listener(self):
        while True:
            self._input_key = input()

    def start(self):
        """Start Listening"""
        if self._listener_thread is None:
            self._listener_thread = threading.Thread(
                target=self._key_listener, daemon=True
            )
        if not self._listener_thread.is_alive():
            self._listener_thread.start()

    def stop(self):
        """Stop Listening"""
        if self._listener_thread is not None and self._listener_thread.is_alive():
            self._listener_thread.join()

    @property
    def pressed(self):
        """Return whether enter was pressed since last checked"""
        result = False
        if self._input_key is not None:
            self._input_key = None
            result = True
        return result


def ellipsoid_fit(data):
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]
    D = np.array(
        [
            x * x + y * y - 2 * z * z,
            x * x + z * z - 2 * y * y,
            2 * x * y,
            2 * x * z,
            2 * y * z,
            2 * x,
            2 * y,
            2 * z,
            1 - 0 * x,
        ]
    )
    d2 = np.array(x * x + y * y + z * z).T  # rhs for LLSQ
    u = np.linalg.solve(D.dot(D.T), D.dot(d2))
    a = np.array([u[0] + 1 * u[1] - 1])
    b = np.array([u[0] - 2 * u[1] - 1])
    c = np.array([u[1] - 2 * u[0] - 1])
    v = np.concatenate([a, b, c, u[2:]], axis=0).flatten()
    A = np.array(
        [
            [v[0], v[3], v[4], v[6]],
            [v[3], v[1], v[5], v[7]],
            [v[4], v[5], v[2], v[8]],
            [v[6], v[7], v[8], v[9]],
        ]
    )

    center = np.linalg.solve(-A[:3, :3], v[6:9])

    translation_matrix = np.eye(4)
    translation_matrix[3, :3] = center.T

    R = translation_matrix.dot(A).dot(translation_matrix.T)

    evals, evecs = np.linalg.eig(R[:3, :3] / -R[3, 3])
    evecs = evecs.T

    radii = np.sqrt(1.0 / np.abs(evals))
    radii *= np.sign(evals)

    return center, evecs, radii


def main():
    bus = SMBus(1)
    imu = ICM20948(i2c_bus=bus, i2c_addr=0x69)

    key_listener = KeyListener()
    key_listener.start()

    # Magnetometer calibration
    print("Magnetometer Calibration")
    print("Start moving the board in all directions")
    print(
        "When the magnetic Hard Offset values stop changing, press ENTER to go to the next step"
    )
    print("Press ENTER to continue...")
    while not key_listener.pressed:
        pass

    mag_data = []
    while not key_listener.pressed:
        mag_x, mag_y, mag_z = imu.read_magnetometer_data()
        mag_data.append([mag_x, mag_y, mag_z])

        if len(mag_data) > SAMPLE_SIZE:
            center, evecs, radii = ellipsoid_fit(np.array(mag_data))
            hard_iron_offset = center
            print(
                "Current Hard Iron Offset: X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
                    *hard_iron_offset
                )
            )

        time.sleep(0.01)

    mag_data = np.array(mag_data)
    center, evecs, radii = ellipsoid_fit(mag_data)
    soft_iron_matrix = evecs @ np.diag(radii) @ evecs.T
    hard_iron_offset = center

    print("")
    print("------------------------------------------------------------------------")
    print("Magnetometer Calibration Values:")
    print("\tHard Iron Offset:", hard_iron_offset)
    print("\tSoft Iron Matrix:\n", soft_iron_matrix)


if __name__ == "__main__":
    main()
