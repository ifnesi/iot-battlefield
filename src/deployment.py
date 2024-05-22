import argparse

from utils import deploy_units


if __name__ == "__main__":
    TARGETS = [
        "tanks",
        "troops",
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
        help="Start simulation without publishing it to Kafka",
        dest="dry_run",
        action="store_true",
    )
    args = parser.parse_args()

    deploy_units(
        args.target,
        args.dry_run,
    )
