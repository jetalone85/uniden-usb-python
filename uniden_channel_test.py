#!/usr/bin/env python3
"""
Test specific channel information on Uniden UBC125XLT scanner.
"""

import logging
import time

import usb.core
import usb.util

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class UnidenUBC125XLT:
    VENDOR_ID = 0x1965
    PRODUCT_ID = 0x0018
    CONFIGURATION = 1
    INTERFACE = 1
    ENDPOINT_IN = 0x81
    ENDPOINT_OUT = 0x02
    TIMEOUT = 5000

    def __init__(self) -> None:
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.device is None:
            raise ValueError("Device not found")
        logging.info("Device found.")

    def initialize(self) -> None:
        if self.device.is_kernel_driver_active(self.INTERFACE):
            self.device.detach_kernel_driver(self.INTERFACE)
            logging.debug("Detached kernel driver.")
        self.device.set_configuration(self.CONFIGURATION)
        usb.util.claim_interface(self.device, self.INTERFACE)
        logging.info("Device initialized successfully.")
        self.clear_buffer()

    def clear_buffer(self) -> None:
        logging.info("Clearing device buffer...")
        try:
            while True:
                data = self.device.read(self.ENDPOINT_IN, 128, timeout=500)
                logging.debug(f"Cleared buffered data: {bytes(data)}")
        except usb.core.USBError:
            logging.info("Buffer cleared.")

    def send_command(self, cmd: str) -> str:
        self.device.write(self.ENDPOINT_OUT, (cmd + '\r').encode('ascii'), timeout=self.TIMEOUT)
        time.sleep(0.1)
        response = self.device.read(self.ENDPOINT_IN, 128, timeout=self.TIMEOUT)
        return bytes(response).decode('ascii', errors='replace').strip()

    def close(self) -> None:
        usb.util.release_interface(self.device, self.INTERFACE)
        usb.util.dispose_resources(self.device)
        logging.info("Device closed properly.")


def main():
    scanner = UnidenUBC125XLT()
    try:
        scanner.initialize()

        # Explicitly query channel 422 details:
        channel_number = 422
        channel_info = scanner.send_command(f"PM {channel_number}")
        logging.info(f"Channel {channel_number} details: '{channel_info}'")

        frequency_info = scanner.send_command(f"RF {channel_number}")
        logging.info(f"Frequency of channel {channel_number}: '{frequency_info}'")

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        scanner.close()


if __name__ == "__main__":
    main()
