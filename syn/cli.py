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
    start_parser.add_argument("--key", type=str)
    start_parser.add_argument("--seed", type=int)
    start_parser.add_argument("--session", type=str)

    args = parser.parse_args()

    if args.command != "start":
        parser.error("Only 'start' command is supported")

    session = Session(mode=args.mode, key=args.key, seed=args.seed, session_name=args.session)
    session.start()

if __name__ == "__main__":
    main()