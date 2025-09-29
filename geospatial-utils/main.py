import argparse
import json
import pathlib
import fileutils
import os
import sys
from fileutils import ed269
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

        data = ed269.loads(source)
        # output = pathlib.Path(args.output_file)
        # output.write_text(json.dumps(data, indent=2))

        logger.debug(json.dumps(data, indent=2))
        logger.error("Work in progress. The parser has not been fully implemented yet. The ED269 parser output was printed above for inspection. (debug log level required)")
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
