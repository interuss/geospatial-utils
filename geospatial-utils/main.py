import argparse
import json
import os
import pathlib
import sys

import adjusters
import convert
import fileutils
import validate
from config import ConverterConfiguration
from fileutils import ed269
from implicitdict import ImplicitDict
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

    convert_cmd.add_argument(
        "-c",
        "--config",
        help="Path to the configuration to use.",
        default="configs/FOCA.json",
    )

    args = parser.parse_args()

    if args.command == "convert":
        logger.debug(f"Converting {args.input_url} to {args.output_file}")
        source = fileutils.get(args.input_url, int(args.ttl))
        logger.debug(f"Local input copy: {source.absolute()}")

        # Load source
        ed269_data = ed269.loads(source)

        # Load config
        with open(args.config) as f:
            data = json.load(f)
            config = ImplicitDict.parse(data, ConverterConfiguration)
        logger.info(f"Using configuration {config.name}")

        # Conversion
        ed318_data = convert.from_ed269_to_ed318(
            ed269_data, config=config.ed318_additions
        )

        # Adjustments
        for adjuster in config.adjusters:
            if not hasattr(adjusters, adjuster):
                logger.error(f"Unknown adjuster: {adjuster}")
                sys.exit(1)

            ed318_data = getattr(adjusters, adjuster).adjust(ed318_data)

        # Save to file
        output = pathlib.Path(args.output_file)
        json_output = json.dumps(ed318_data)
        output.write_text(json_output, encoding="utf-8")
        logger.debug(f"Successful conversion. File saved to: {output.absolute()}")

        # Validation
        errors = validate.ed318(json.loads(json_output))
        if len(errors) > 0:
            for e in errors:
                logger.error(f"{e.json_path}: {e.message}")
            sys.exit(1)
        logger.info(
            f"Successful conversion and validation. ED-318 saved to {output.absolute()}"
        )

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
