#!/usr/bin/env python3
"""
Uniden UBC125XLT USB Device Descriptor Utility

This module locates a connected Uniden UBC125XLT USB device and prints its descriptors.
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
    Class representing the Uniden UBC125XLT USB device.
    """
    VENDOR_ID = 0x1965
    PRODUCT_ID = 0x0018

    def __init__(self) -> None:
        """
        Locate the Uniden device on the USB bus.
        Exits the program if the device is not found.
        """
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.device is None:
            logging.error("Uniden UBC125XLT device not found. Check USB connection and device IDs.")
            sys.exit(1)
        logging.info("Uniden UBC125XLT device found successfully.")

    def print_descriptors(self) -> None:
        """
        Retrieve and print the USB device descriptors.
        """
        logging.info("Retrieving USB device descriptors...")
        logging.info(f"Vendor ID: {hex(self.device.idVendor)}")
        logging.info(f"Product ID: {hex(self.device.idProduct)}")
        logging.info(f"Device Class: {hex(self.device.bDeviceClass)}")
        logging.info(f"Device Subclass: {hex(self.device.bDeviceSubClass)}")
        logging.info(f"Device Protocol: {hex(self.device.bDeviceProtocol)}")

        try:
            manufacturer = usb.util.get_string(self.device, self.device.iManufacturer)
            product = usb.util.get_string(self.device, self.device.iProduct)
            serial_number = usb.util.get_string(self.device, self.device.iSerialNumber)
            logging.info(f"Manufacturer: {manufacturer}")
            logging.info(f"Product: {product}")
            logging.info(f"Serial Number: {serial_number}")
        except usb.core.USBError as e:
            logging.error(f"Failed to retrieve string descriptors: {e}")

        # Iterate through all configurations, interfaces, and endpoints
        for cfg in self.device:
            logging.info(f"Configuration: {cfg.bConfigurationValue}")
            for intf in cfg:
                logging.info(
                    f" Interface: Number={intf.bInterfaceNumber}, Class={hex(intf.bInterfaceClass)}, "
                    f"SubClass={hex(intf.bInterfaceSubClass)}, Protocol={hex(intf.bInterfaceProtocol)}"
                )
                for ep in intf:
                    logging.info(
                        f"  Endpoint: Address={hex(ep.bEndpointAddress)}, Attributes={hex(ep.bmAttributes)}, "
                        f"Max Packet Size={ep.wMaxPacketSize}"
                    )


def main() -> None:
    """
    Main function to detect the device and print its descriptors.
    """
    device = UnidenDevice()
    device.print_descriptors()
    logging.info("Completed retrieving device descriptors.")


if __name__ == "__main__":
    main()
