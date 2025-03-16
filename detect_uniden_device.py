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

# Update these after identification
UNIDEN_VENDOR_ID = 0x1965
UNIDEN_PRODUCT_ID = 0x0018  # sprawdź dokładnie na swoim urządzeniu!


def find_uniden_device():
    logging.info("Searching for Uniden frequency scanner USB device...")

    # find device
    device = usb.core.find(idVendor=UNIDEN_VENDOR_ID, idProduct=UNIDEN_PRODUCT_ID)

    if device is None:
        logging.error("Uniden device not found. Check USB connection and device IDs.")
        return None

    logging.info(f"Found Uniden USB device: Vendor ID={hex(UNIDEN_VENDOR_ID)}, Product ID={hex(UNIDEN_PRODUCT_ID)}")

    return device


def main():
    device = find_uniden_device()
    if device:
        logging.info("Device detection successful.")
    else:
        logging.error("Device detection failed.")


if __name__ == "__main__":
    # Update these IDs once you've identified them
    UNIDEN_VENDOR_ID = 0x1965
    UNIDEN_PRODUCT_ID = 0x0018
    main_device = find_uniden_device()
