#!/usr/bin/env python3
"""
Uniden UBC125XLT USB Device Communication Module

This module implements a class-based approach for communicating with the Uniden UBC125XLT
frequency scanner via USB. It provides methods to initialize the device, send commands,
read responses, and close the connection. All comments and log messages are in English.
"""

import logging

import usb.core
import usb.util

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


class UnidenUBC125XLT:
    """
    Class to manage communication with the Uniden UBC125XLT frequency scanner via USB.
    """
    VENDOR_ID = 0x1965
    PRODUCT_ID = 0x0018
    CONFIGURATION = 1
    INTERFACE = 1  # using CDC Data interface (#1)
    ENDPOINT_IN = 0x81
    ENDPOINT_OUT = 0x02
    TIMEOUT = 5000

    def __init__(self):
        """
        Locate the Uniden device on the USB bus.
        Raises:
            ValueError: if the device is not found.
        """
        self.device = usb.core.find(
            idVendor=self.VENDOR_ID,
            idProduct=self.PRODUCT_ID
        )
        if self.device is None:
            raise ValueError("Uniden UBC125XLT not found.")

    def initialize(self):
        """
        Initialize the Uniden device by detaching any active kernel driver,
        setting the configuration, and claiming the USB interface.
        """
        logging.info("Initializing device...")

        if self.device.is_kernel_driver_active(self.INTERFACE):
            self.device.detach_kernel_driver(self.INTERFACE)
            logging.debug("Kernel driver detached.")

        self.device.set_configuration(self.CONFIGURATION)
        usb.util.claim_interface(self.device, self.INTERFACE)
        logging.info("Device initialized and interface claimed.")

    def send_command(self, command: str):
        """
        Send a command to the device.

        Parameters:
            command (str): The command to send. It is encoded in ASCII and appended with a carriage return.
        """
        data = command.encode('ascii') + b'\r'
        logging.info(f"Sending command: {command}")
        self.device.write(self.ENDPOINT_OUT, data, timeout=self.TIMEOUT)
        logging.debug(f"Sent {len(data)} bytes.")

    def read_response(self, length=64) -> str:
        """
        Read a response from the device.

        Parameters:
            length (int): Maximum number of bytes to read from the device.

        Returns:
            str: The response from the device decoded as ASCII.
        """
        logging.info("Reading response...")
        response = self.device.read(self.ENDPOINT_IN, length, timeout=self.TIMEOUT)
        response_text = bytes(response).decode('ascii', errors='ignore').strip()
        logging.info(f"Received response: {response_text}")
        return response_text

    def close(self):
        """
        Release the USB interface and dispose of device resources.
        """
        usb.util.release_interface(self.device, self.INTERFACE)
        usb.util.dispose_resources(self.device)
        logging.info("Device closed.")


def main():
    """
    Main function to demonstrate basic communication with the Uniden UBC125XLT device.
    It sends a test command ("MDL" for device model) and logs the response.
    """
    scanner = None
    try:
        scanner = UnidenUBC125XLT()
        scanner.initialize()

        # Test communication: send command "MDL" (device model)
        scanner.send_command("MDL")
        response = scanner.read_response()
        logging.info(f"Device responded: {response}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        if scanner:
            try:
                scanner.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
