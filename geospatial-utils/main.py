import argparse
import os
import sys

import fileutils
from loguru import logger

version = os.environ.get("GEOSPATIAL_UTILS_VERSION", "unknown")


def main():
    logger.info(f"Geospatial utils - {version}")

    parser = argparse.ArgumentParser(description="ED-269 to ED-318 converter")

    commands = parser.add_subparsers(
        title="commands", dest="command", help="command", required=True
    )

    convert_cmd = commands.add_parser("convert", help="Convert ED-269 to ED-318")
    convert_cmd.add_argument(
        "input_url",
        help="URL of the ED-269 source file, example: https://data.geo.admin.ch/ch.bazl.einschraenkungen-drohnen/einschraenkungen-drohnen/einschraenkungen-drohnen_4326.json",
    )
    convert_cmd.add_argument("output_file", help="Path to ED-318 output file")
    convert_cmd.add_argument(
        "-t",
        "--ttl",
        help="Time to live of the cached files after download in seconds (default: 0)",
        default="0",
    )

    args = parser.parse_args()

    if args.command == "convert":
        logger.debug(f"Converting {args.input_url} to {args.output_file}")
        source = fileutils.get(args.input_url, int(args.ttl))
        logger.debug(f"Local input copy: {source.absolute()}")
        # destination = pathlib.Path(args.output_file)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
