import os
import argparse

from utils import deploy


if __name__ == "__main__":
    TARGETS = [
        "tanks",
        "troops",
    ]
    parser = argparse.ArgumentParser(description="Python emulator - IoT Battlefield")
    parser.add_argument(
        "--target",
        help=f"Select target unit to be deployed. Valid options are: {', '.join(TARGETS)}",
        dest="target",
        type=str,
        choices=TARGETS,
        required=True,
    )

    args = parser.parse_args()

    deploy(args.target)
