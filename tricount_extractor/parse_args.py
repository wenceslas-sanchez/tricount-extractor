import argparse

from tricount_extractor.client.client import DEFAULT_TIMEOUT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract and save Tricount registries to Excel files"
    )
    parser.add_argument(
        "-id",
        "--registry-id",
        nargs="+",
        required=True,
        help="One or more Tricount registry IDs to extract",
    )
    parser.add_argument(
        "-f",
        "--folder",
        action="store",
        type=str,
        required=True,
        help="Output folder path where registry Excel files will be saved",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        action="store",
        type=float_or_none,
        default=DEFAULT_TIMEOUT,
        help=(
            f"HTTP request timeout in seconds (default: {DEFAULT_TIMEOUT}). "
            "Use None for no timeout."
        ),
    )
    return parser.parse_args()


def float_or_none(value):
    if value is None or value.lower() == "none":
        return None
    try:
        return float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid float or 'None'")
