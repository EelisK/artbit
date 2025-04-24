import logging
import sys

from app import cli
from app.sound import presets
from app.sound.player import LoopPlayer

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s\t%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

if __name__ != "__main__":
    raise RuntimeError("This module should be run as a script")


args = cli.parse_args()
input_plugin = cli.get_plugin(args)

if input_plugin is None:
    logging.error("No input plugin selected. Use --stdin or --uds.")
    sys.exit(1)


player = LoopPlayer()
player.start()

bpm = cli.get_bpm(args)
if bpm is not None:
    if args.verbose:
        logging.info(f"Initial BPM: {bpm}")
    player.set_sound(presets.RealisticHeartbeatSound(bpm=bpm))

try:
    input_plugin.start()
    for bpm in input_plugin.values():
        bpm = round(bpm)
        if args.verbose:
            logging.info(f"Received BPM: {bpm}")
        player.set_sound(presets.RealisticHeartbeatSound(bpm=bpm))
        cli.set_bpm(args, round(bpm))
except Exception:
    logging.exception("Stopping the application")
finally:
    player.stop()
    input_plugin.stop()
    logging.info("Application stopped")
