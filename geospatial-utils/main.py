import argparse
import json
import os
import pathlib
import sys

import adjusters.foca
import config
import convert
import fileutils
import validate
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

        # Load source
        ed269_data = ed269.loads(source)
        # TODO: Move hard-coded configuration to a json file.
        logger.warning(
            "Additional data not provided in ED269 is hard-coded with Swiss FOCA information. This will be moved to a configurable file in the near future."
        )

        # Conversion
        ed318_data = convert.from_ed269_to_ed318(ed269_data, config=config.FOCA)

        # Adjustments
        logger.warning(
            "The output is adjusted with Swiss FOCA configuration. The output contains non-conform ConditionExpressionType values."
        )
        ed318_data = adjusters.foca.adjust(ed318_data)

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
