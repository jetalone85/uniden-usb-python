#!/usr/bin/env python3
"""
Uniden UBC125XLT Bulk Channel Read Test

This script initializes the Uniden UBC125XLT scanner, sends the "GLG" command
to retrieve bulk channel information, and parses the response to extract useful data such as frequency,
modulation mode, and channel number.
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
    INTERFACE = 1  # using CDC Data interface (#1)
    ENDPOINT_IN = 0x81
    ENDPOINT_OUT = 0x02
    TIMEOUT = 5000  # ms

    def __init__(self) -> None:
        self.device = usb.core.find(
            idVendor=self.VENDOR_ID,
            idProduct=self.PRODUCT_ID
        )
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
                data = self.device.read(self.ENDPOINT_IN, 256, timeout=500)
                logging.debug(f"Cleared buffered data: {bytes(data)}")
        except usb.core.USBError:
            logging.info("Buffer cleared.")

    def send_command(self, cmd: str) -> str:
        full_cmd = cmd.strip() + '\r'
        logging.debug(f"Sending command: '{cmd}'")
        self.device.write(self.ENDPOINT_OUT, full_cmd.encode('ascii'), timeout=self.TIMEOUT)
        time.sleep(0.3)  # increased delay to allow full response
        response = self.device.read(self.ENDPOINT_IN, 256, timeout=self.TIMEOUT)
        response_text = bytes(response).decode('ascii', errors='replace').strip()
        # If the response ends with a comma, it might be incomplete; attempt to read additional data.
        if response_text.endswith(','):
            try:
                extra = self.device.read(self.ENDPOINT_IN, 256, timeout=1000)
                extra_text = bytes(extra).decode('ascii', errors='replace').strip()
                response_text += extra_text
                logging.debug("Appended extra response data.")
            except usb.core.USBError:
                logging.debug("No extra response data available.")
        logging.debug(f"Received response: '{response_text}'")
        return response_text

    def close(self) -> None:
        usb.util.release_interface(self.device, self.INTERFACE)
        usb.util.dispose_resources(self.device)
        logging.info("Device closed properly.")


def parse_glg_response(response: str) -> dict:
    """
    Parses the GLG response string into a dictionary.

    Expected format (when complete):
      GLG,<frequency>,<mode>,...,<channel>
    Example:
      "GLG,01705000,FM,,0,,,,0,1,,422"
    """
    fields = response.split(',')
    if fields[0] != "GLG":
        logging.warning("Response does not start with GLG.")
        return {}

    try:
        # Frequency field: '01705000' means 170.5000 MHz
        raw_freq = fields[1]
        frequency = int(raw_freq) / 10000.0 if raw_freq.isdigit() else None

        mode = fields[2] if len(fields) > 2 else None
        # Assume the channel is in the last non-empty field
        channel = next((f for f in reversed(fields) if f.strip()), "")

        return {
            "command": fields[0],
            "raw_frequency": raw_freq,
            "frequency_mhz": frequency,
            "mode": mode,
            "channel": channel,
        }
    except Exception as e:
        logging.error(f"Error parsing GLG response: {e}")
        return {}


def main() -> None:
    scanner = UnidenUBC125XLT()
    try:
        scanner.initialize()

        # Use GLG to retrieve bulk channel info.
        glg_response = scanner.send_command("GLG")
        logging.info(f"GLG response: '{glg_response}'")

        parsed = parse_glg_response(glg_response)
        if parsed:
            logging.info(f"Parsed GLG response: {parsed}")
        else:
            logging.info("Failed to parse GLG response.")

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        scanner.close()


if __name__ == "__main__":
    main()
