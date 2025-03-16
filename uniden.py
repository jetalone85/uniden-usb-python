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
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")


class UnidenUBC125XLT:
    VENDOR_ID = 0x1965
    PRODUCT_ID = 0x0018
    CONFIGURATION = 1
    INTERFACE = 1
    ENDPOINT_IN = 0x81
    ENDPOINT_OUT = 0x02
    TIMEOUT = 5000

    def __init__(self):
        """
        Locate the Uniden UBC125XLT device on the USB bus.
        Raises:
            ValueError: if the device is not found.
        """
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.device is None:
            raise ValueError("Uniden UBC125XLT not found.")

    def initialize(self):
        """
        Initialize the device by detaching any active kernel driver, setting the configuration,
        and claiming the USB interface.
        """
        if self.device.is_kernel_driver_active(self.INTERFACE):
            self.device.detach_kernel_driver(self.INTERFACE)
            logging.debug("Detached kernel driver.")
        self.device.set_configuration(self.CONFIGURATION)
        usb.util.claim_interface(self.device, self.INTERFACE)
        logging.info("Device initialized successfully.")

    def send_command(self, cmd: str) -> str:
        """
        Send a command to the device and return the response.

        Parameters:
            cmd (str): Command string to send.

        Returns:
            str: The device response.
        """
        full_cmd = cmd.strip() + '\r'
        self.device.write(self.ENDPOINT_OUT, full_cmd.encode('ascii'), timeout=self.TIMEOUT)
        logging.debug(f"Sent: {cmd}")
        response = self.device.read(self.ENDPOINT_IN, 64, timeout=self.TIMEOUT)
        response_text = bytes(response).decode('ascii').strip()
        logging.debug(f"Response: {response_text}")
        return response_text

    def get_model(self) -> str:
        """
        Get the device model by sending the "MDL" command.

        Returns:
            str: The device model.
        """
        return self.send_command("MDL")

    def get_channel_frequency(self, channel: int) -> str:
        """
        Get the frequency for a specified channel.

        Parameters:
            channel (int): The channel number.

        Returns:
            str: The frequency as a string.
        """
        return self.send_command(f"RF {channel}")

    def close(self):
        """
        Release the USB interface and dispose of device resources.
        """
        usb.util.release_interface(self.device, self.INTERFACE)
        usb.util.dispose_resources(self.device)
        logging.info("Device closed properly.")

    def get_channel_info(self, channel: int) -> str:
        """
        Get detailed information about a specified channel.

        Parameters:
            channel (int): The channel number.

        Returns:
            str: Channel details.
        """
        return self.send_command(f"PM {channel}")


if __name__ == "__main__":
    scanner = UnidenUBC125XLT()
    try:
        scanner.initialize()

        model = scanner.get_model()
        logging.info(f"Model: {model}")

        # Try first 10 channels to find a programmed one
        for channel_number in range(1, 11):
            channel_info = scanner.get_channel_info(channel_number)
            logging.info(f"Channel {channel_number} info: {channel_info}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        scanner.close()
