import argparse
import sys
from syn.session import Session

def main():
    parser = argparse.ArgumentParser(
        prog="syn",
        description="syn - synesthesia engine"
    )

    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument(
        "mode",
        choices=["research", "live"],
        help="Session mode (research or live)"
    )

    args = parser.parse_args()

    if args.command != "start":
        parser.error("Only 'start' command is supported")

    session = Session(mode=args.mode)
    session.start()

if __name__ == "__main__":
    main()