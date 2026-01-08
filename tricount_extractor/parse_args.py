import argparse


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
    return parser.parse_args()
