#!/usr/bin/env python3

import asyncio
import click
import json
import logging
import pkg_resources

from collections import defaultdict
from jsonschema import ValidationError, validate
from typing import Any, Dict, Union

from . import inputschemajson

log = logging.getLogger(__name__)


class Crunchr:
    def __init__(self) -> None:
        self.system_results = defaultdict(lambda: defaultdict(int))
        self.output = []

    async def load_json(self, filename: str) -> Union[Dict[str, Any], bool]:
        """
        Helper function to handle potential json exceptions
        """
        try:
            with open(filename) as s:
                schema = json.load(s)
        except json.JSONDecodeError as e:
            log.error(f"input schema file cannot be loaded:")
            log.error(e)
            return False

        return schema

    async def get_input(
        self, filename: str, schemafile: str
    ) -> Union[Dict[str, Any], bool]:
        """
        This function gets the input files and validates them, it's not
        very exciting
        """
        if not schemafile:
            schema = json.loads(inputschemajson.inputschema)
        else:
            schema = await self.load_json(schemafile)
        inputdata = await self.load_json(filename)

        if not schema or not inputdata:
            return False

        try:
            validate(inputdata, schema)
        except ValidationError as e:
            log.error("input json failed to validate")
            return False

        return inputdata

    async def verify_report_sanity(self, payload: Dict[str, Any]) -> (bool, str):
        """
        This function contains the business logic for job failures
        """
        # docs say that failures include
        #  a negative number of jobs
        # -- this isn't possible since jobs is a count of input blocks and not a parameter
        # - more failures than total units procsssed
        # additionally
        # - structure has already been taken care of in the validation
        # - type has already been taken care of in the validation
        if payload["units_failed"] > payload["units_processed"]:
            return (
                False,
                f"units_failed {payload['units_failed']} > units_processed {payload['units_processed']}",
            )

        if payload["units_failed"] < 0:
            return (False, f"units failed {payload['units_failed']} < 0")

        if payload["units_processed"] < 0:
            return (False, f"units processed {payload['units_processed']} < 0")

        # these verify string is not empty since verification did type
        if not payload["job_id"]:
            return (False, f"job_id cannot be empty")

        if not payload["system_id"]:
            return (False, f"system_id cannot be empty")
        ###

        return (True, "")

    async def process_job_report(self, payload: Dict[str, Any]) -> None:
        """
        Process a job report from the server
        """

        report_status = await self.verify_report_sanity(payload)

        if report_status[0]:
            sysid = payload["system_id"]
            self.system_results[sysid]["jobs"] += 1
            self.system_results[sysid]["units_processed"] += payload["units_processed"]
            self.system_results[sysid]["units_failed"] += payload["units_failed"]

            self.output.append(
                {"system_id": sysid, "job_id": payload["job_id"], "status": "success"}
            )
        else:
            # if a report has failed the sanity check, don't tally its stats,
            # they're unreliable
            status = f"failed: {report_status[1]}"
            self.output.append(
                {
                    "system_id": payload["system_id"],
                    "job_id": payload["job_id"],
                    "status": status,
                }
            )

    async def process_system_query(self, payload: Dict[str, Any]) -> None:
        """
        Process a system query
        """
        stats = defaultdict(int)
        if payload["get_stats"]:
            s = payload["get_stats"]
            stats["total_job_count"] += self.system_results[s]["jobs"]
            stats["total_units_processed"] += self.system_results[s]["units_processed"]
            stats["total_units_failed"] += self.system_results[s]["units_failed"]
        else:
            for s in self.system_results:
                stats["total_job_count"] += self.system_results[s]["jobs"]
                stats["total_units_processed"] += self.system_results[s][
                    "units_processed"
                ]
                stats["total_units_failed"] += self.system_results[s]["units_failed"]

        stats["total_units_succeded"] = (
            stats["total_units_processed"] - stats["total_units_failed"]
        )
        # correcting 'successfull' to 'successful', rounding to 1 digit as per docs
        stats["percent_successful"] = round(
            (stats["total_units_succeded"] / stats["total_units_processed"]) * 100, 1
        )

        self.output.append(stats)

    # Note that this doesn't scale.  By trying to collate all the output
    # into a single json structure, it requires holding all the info
    # until the end of the process.  Streaming it to a log file or api as
    # the code ran would allow us to drop the self.output storage mechanism.
    async def output_stats(self, output_file: str, printout: bool) -> None:
        """
        Sends the resultant data to an output file, optionally print
        """
        with open(output_file, "w") as f:
            json.dump({"output": self.output}, f, indent=2)

        if printout:
            print(json.dumps({"output": self.output}, indent=2))


async def run(input: str, output: str, schema: str, printout: str) -> None:
    """
    Main entry point
    """
    c = Crunchr()
    inputdata = await c.get_input(input, schema)
    if not inputdata:
        # input could not be loaded, errors already printed
        log.error("Errors found trying to load data, exiting")
        return

    for payload in inputdata["input"]:
        # payload is already validated above
        if "system_id" in payload:
            await c.process_job_report(payload)
        else:
            await c.process_system_query(payload)

    await c.output_stats(output, printout)


@click.command()
@click.option("-i", "--input", default="INPUT.json", help="input file")
@click.option("-o", "--output", default="OUTPUT.json", help="output file")
@click.option(
    "-s", "--schema", type=str, default=None, help="override json schema file"
)
@click.option(
    "-p", "--printout", default=False, is_flag=True, help="print to stdout as well"
)
def cli(input: str, output: str, schema: str, printout: bool) -> None:
    """
    cli option handler and async laucher
    """
    asyncio.run(run(input, output, schema, printout))


if __name__ == "__main__":
    cli()
