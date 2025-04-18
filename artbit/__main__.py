import argparse
import logging
import sys
from typing import Union

from artbit.plugins.base import Plugin
from artbit.sound import presets
from artbit.sound.player import LoopPlayer

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s\t%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

if __name__ != "__main__":
    raise RuntimeError("This module should be run as a script")


args_parser = argparse.ArgumentParser(
    description="Artbit - A simple heartbeat sound generator",
)
args_parser.add_argument(
    "--verbose",
    action="store_true",
    help="Enable verbose logging",
)
stdin_group = args_parser.add_mutually_exclusive_group(required=False)
stdin_group.add_argument(
    "--stdin",
    help="Use stdin as input",
    action="store_true",
)

uds_group = args_parser.add_mutually_exclusive_group(required=False)
uds_group.add_argument(
    "--uds",
    help="Use UDS as input",
    action="store_true",
)
uds_group.add_argument(
    "--uds-path",
    help="Path to the UDS socket",
    default="/tmp/artbit.sock",
)
uds_group.add_argument(
    "--uds-timeout",
    help="Timeout for UDS socket",
    type=float,
    default=0.1,
)

args = args_parser.parse_args()


input_plugin: Union[Plugin, None] = None

if args.stdin:
    from artbit.plugins.stdin import StdInPlugin

    input_plugin = StdInPlugin(prompt="Enter BPM: ")
elif args.uds:
    from artbit.plugins.uds import UDSPlugin

    input_plugin = UDSPlugin(
        path=args.uds_path,
        timeout=args.uds_timeout,
    )

if input_plugin is None:
    logging.error("No input plugin selected. Use --stdin or --uds.")
    sys.exit(1)

player = LoopPlayer()
player.start()


try:
    input_plugin.start()
    for bpm in input_plugin.values():
        bpm = round(bpm)
        if args.verbose:
            logging.info(f"Received BPM: {bpm}")
        player.set_sound(presets.RealisticHeartbeatSound(bpm=bpm))
except Exception:
    logging.exception("Stopping the application")
finally:
    player.stop()
    input_plugin.stop()
    logging.info("Application stopped")
