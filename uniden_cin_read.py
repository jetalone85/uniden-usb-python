import logging
import time

import usb.core
import usb.util

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')


class UnidenUBC125XLT:
    VENDOR_ID = 0x1965
    PRODUCT_ID = 0x0018
    CONFIGURATION = 1
    INTERFACE = 1
    ENDPOINT_IN = 0x81
    ENDPOINT_OUT = 0x02
    TIMEOUT = 5000

    def __init__(self):
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.device is None:
            raise ValueError("Device not found")
        logging.info("Device found.")

    def initialize(self):
        if self.device.is_kernel_driver_active(self.INTERFACE):
            self.device.detach_kernel_driver(self.INTERFACE)
        self.device.set_configuration(self.CONFIGURATION)
        usb.util.claim_interface(self.device, self.INTERFACE)
        logging.info("Device initialized successfully.")

    def send_command(self, cmd):
        full_cmd = cmd.strip() + '\r'
        self.device.write(self.ENDPOINT_OUT, full_cmd.encode('ascii'), timeout=self.TIMEOUT)
        time.sleep(0.1)
        response = self.device.read(self.ENDPOINT_IN, 128, timeout=self.TIMEOUT)
        return bytes(response).decode('ascii').strip()

    def close(self):
        usb.util.release_interface(self.device, self.INTERFACE)
        usb.util.dispose_resources(self.device)
        logging.info("Device closed properly.")


if __name__ == "__main__":
    scanner = UnidenUBC125XLT()
    try:
        scanner.initialize()
        for cmd in ["CIN", "GLG"]:
            response = scanner.send_command(cmd)
            logging.info(f"{cmd} → {response}")
    finally:
        usb.util.release_interface(scanner.device, scanner.INTERFACE)
        usb.util.dispose_resources(scanner.device)
        logging.info("Device closed properly.")
