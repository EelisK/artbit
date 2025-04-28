import argparse

from app.plugins.base import Plugin
from app.plugins.stdin import StdInPlugin
from app.plugins.uds import UDSPlugin


class Args(argparse.Namespace):
    # Logging
    verbose: bool

    # Setup and teardown of sound
    bpm_file: str
    bpm_default: int | None

    # Input plugins
    stdin: bool
    uds: bool
    uds_path: str
    uds_timeout: float


def get_plugin(cfg: Args) -> Plugin | None:
    if cfg.stdin:
        return StdInPlugin(prompt="Enter BPM: ")
    if cfg.uds:
        return UDSPlugin(
            path=cfg.uds_path,
            timeout=cfg.uds_timeout,
        )
    return None


def get_bpm(cfg: Args) -> int | None:
    try:
        with open(cfg.bpm_file, "r") as f:
            bpm = int(f.read())
    except (FileNotFoundError, ValueError):
        bpm = cfg.bpm_default
    return bpm


def set_bpm(cfg: Args, bpm: int) -> None:
    with open(cfg.bpm_file, "w") as f:
        f.write(str(bpm))


def parse_args() -> Args:
    args_parser = argparse.ArgumentParser(
        description="Artbit - A simple heartbeat sound generator",
    )
    args_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args_parser.add_argument(
        "--bpm-file",
        help="Path to the file where the last BPM is stored",
        default="last_bpm.txt",
    )
    args_parser.add_argument(
        "--bpm-default",
        help="Default BPM value",
        type=int,
    )

    args_parser.add_argument(
        "--stdin",
        help="Use stdin as input",
        action="store_true",
    )

    args_parser.add_argument(
        "--uds",
        help="Use UDS as input",
        action="store_true",
    )
    args_parser.add_argument(
        "--uds-path",
        help="Path to the UDS socket",
        default="/tmp/artbit.sock",
    )
    args_parser.add_argument(
        "--uds-timeout",
        help="Timeout for UDS socket",
        type=float,
        default=0.1,
    )

    nsp = Args()
    return args_parser.parse_args(namespace=nsp)
