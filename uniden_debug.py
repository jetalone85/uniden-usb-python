#!/usr/bin/env python3
"""
Uniden UBC125XLT Debug Tool (with USB buffer clearing)

This script sends multiple commands to the scanner and ensures
responses match sent commands by clearing buffers before use.
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
        logging.info("Uniden UBC125XLT device located.")

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
                logging.debug(f"Cleared buffered data: {bytes(data).decode('ascii', errors='replace')}")
        except usb.core.USBError as e:
            if e.errno == 110 or "timeout" in str(e).lower():
                logging.info("Device buffer cleared (no more data).")
            else:
                logging.error(f"USB error clearing buffer: {e}")

    def send_command(self, cmd: str) -> str:
        full_cmd = cmd.strip() + '\r'
        logging.debug(f"Sending command: '{cmd}'")
        self.device.write(self.ENDPOINT_OUT, full_cmd.encode('ascii'), timeout=self.TIMEOUT)
        time.sleep(0.1)
        response = self.device.read(self.ENDPOINT_IN, 128, timeout=self.TIMEOUT)
        response_text = bytes(response).decode('ascii', errors='replace').strip()
        logging.debug(f"Received response: '{response_text}'")
        return response_text

    def close(self) -> None:
        usb.util.release_interface(self.device, self.INTERFACE)
        usb.util.dispose_resources(self.device)
        logging.info("Device closed properly.")


def rediscover_commands(scanner: UnidenUBC125XLT) -> dict:
    test_commands = ["MDL", "VER", "VOL", "BAT", "STS",
                     "GLG", "KEY,PSE", "KEY,SCN", "RF 1",
                     "PM 1", "SQ", "BLT"]
    responses = {}
    for cmd in test_commands:
        try:
            response = scanner.send_command(cmd)
            responses[cmd] = response
            logging.info(f"Command '{cmd}' response: '{response}'")
            time.sleep(0.2)
        except usb.core.USBError as e:
            logging.error(f"USB Error on command '{cmd}': {e}")
            responses[cmd] = f"USB Error: {e}"
    return responses


def main() -> None:
    scanner = UnidenUBC125XLT()
    try:
        scanner.initialize()
        results = rediscover_commands(scanner)
        print("\n--- Corrected Summary of Responses ---")
        for command, response in results.items():
            print(f"{command:<10} → {response}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        scanner.close()


if __name__ == "__main__":
    main()
