#!/usr/bin/env python3

import shutil
import argparse

from .run import run, purge
from .audio import audio_player
from .inputs import read_input_file
from .xinput import gb_input_context, cbreak_mode

CSI = b"\033["


def main(args=None):
    parser = argparse.ArgumentParser(description="Gambatte terminal frontend")
    parser.add_argument("romfile", metavar="ROM", type=str)
    parser.add_argument("--input-file", "-i", default=None)
    parser.add_argument("--true-color", "-c", action="store_true")
    parser.add_argument("--test", "-t", action="store_true")
    parser.add_argument("--fast", "-f", action="store_true")
    args = parser.parse_args(args)

    if args.input_file is not None:
        get_input_from_file = read_input_file(args.input_file)
    else:
        get_input_from_file = None

    with audio_player() as audio_out:
        with cbreak_mode() as (stdin, stdout):
            try:
                stdout.write(CSI + b"2J")
                with gb_input_context() as get_gb_input:
                    return_code = run(
                        args.romfile,
                        get_input_from_file or get_gb_input,
                        stdin=stdin,
                        stdout=stdout,
                        get_size=shutil.get_terminal_size,
                        true_color=args.true_color,
                        audio_out=audio_out,
                        test=args.test,
                        fast=args.fast,
                    )
            except KeyboardInterrupt:
                pass
            else:
                exit(return_code)
            finally:
                purge(stdin)
                stdout.write(CSI + b"0m" + CSI + b"2J" + b"\n")


if __name__ == "__main__":
    main()
