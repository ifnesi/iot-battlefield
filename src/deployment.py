"""
IoT Battlefield Emulator - Deployment Script

This script deploys battlefield units (troops, tanks, or FLC) and emulates their
real-time behavior by publishing events to Kafka topics.

Usage:
    python deployment.py --target troops
    python deployment.py --target tanks
    python deployment.py --target flc
    python deployment.py --target troops --dry-run
"""
import argparse

from utils import deploy_units


if __name__ == "__main__":
    TARGETS = [
        "tanks",
        "troops",
        "flc",
    ]
    parser = argparse.ArgumentParser(description="Python emulator - IoT Battlefield")
    parser.add_argument(
        "--target",
        help=f"Select the target unit to be deployed. Valid options are: {', '.join(TARGETS)}",
        dest="target",
        type=str,
        choices=TARGETS,
        required=True,
    )
    parser.add_argument(
        "--dry-run",
        help="Start emulator without publishing to Kafka",
        dest="dry_run",
        action="store_true",
    )
    args = parser.parse_args()

    deploy_units(
        args.target,
        args.dry_run,
    )
