import os
import argparse

from utils import deploy


if __name__ == "__main__":
    TARGETS = [
        "tanks",
        "troops",
    ]
    parser = argparse.ArgumentParser(
        description="Python emulator - IoT Battlefield"
    )
    parser.add_argument(
        "--target",
        help=f"Select target unit to be deployed. Valid options are: {', '.join(TARGETS)}",
        dest="target",
        type=str,
        choices=TARGETS,
        required=True,
    )

    args = parser.parse_args()

    FILE_APP = os.path.splitext(os.path.split(__file__)[-1])[0]
    deploy(FILE_APP, args.target)
