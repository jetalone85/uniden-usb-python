#!/usr/bin/env python3
"""
Uniden Frequency Scanner USB Device Detection Module

This module provides a class-based implementation for detecting a connected Uniden
frequency scanner USB device. Update the vendor and product IDs as necessary.
All comments and log messages are in English.
"""

import logging
import sys

import usb.core
import usb.util

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


class UnidenDevice:
    """
    Class to manage the Uniden frequency scanner USB device.
    """
    # Device identifiers (update these values based on your device)
    VENDOR_ID = 0x1965
    PRODUCT_ID = 0x0018

    def __init__(self) -> None:
        """
        Initialize the Uniden device by searching for it on the USB bus.
        Exits the program if the device is not found.
        """
        logging.info("Searching for Uniden frequency scanner USB device...")
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.device is None:
            logging.error("Uniden device not found. Check USB connection and device IDs.")
            sys.exit(1)
        logging.info(f"Found Uniden USB device: Vendor ID={hex(self.VENDOR_ID)}, Product ID={hex(self.PRODUCT_ID)}")

    def initialize(self) -> None:
        """
        Perform any additional initialization steps if needed.
        Currently, it simply logs that the device detection was successful.
        """
        logging.info("Device detection successful.")

    def close(self) -> None:
        """
        Release device resources.
        """
        usb.util.dispose_resources(self.device)
        logging.info("Device resources released.")


def main() -> None:
    """
    Main function to detect and initialize the Uniden device.
    """
    uniden = UnidenDevice()
    uniden.initialize()
    # Further operations with uniden.device can be added here.
    uniden.close()


if __name__ == "__main__":
    main()
