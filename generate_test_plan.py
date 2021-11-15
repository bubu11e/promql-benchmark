#!/usr/bin/env python3
"""
This scipt is used to generate a JMeter plan from a set of requests
"""

import argparse
import json
import logging
import os
import re
from jinja2 import Template
from queries import InstantQuery, Queries, RangeQuery

def convert_query(name, query, parameters):
    """
    This function is used to replace PromQL query parameters by the one provided.
    """
    variables = set(re.findall(r"\$([^\"\]]*)", query))
    for variable in variables:
        if variable not in parameters:
            raise Exception ("Query {} contains a {} var but you did not provide any parameter with that name".format(name, variable))

        query = query.replace("${}".format(variable), parameters[variable])

    return query

def cmdline_parser():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Script use to convert Grafana dashboard into JMeter test plan for PromQL endpoint"
    )

    parser.add_argument(
        "-t", "--template", help="JMeter test template to use", required=True
    )

    parser.add_argument(
        "-o", "--output", help="Where to write the final JMeter test file", required=True
    )

    parser.add_argument(
        "-n", "--now", help="Last unix timestamp of the interval for requests in seconds (0 means use current timestamp)", required=False, type=int
    )

    parser.add_argument(
        "-i", "--interval", help="Time interval in seconds for requests", required=False, type=int
    )

    parser.add_argument(
        "-s", "--step", help="Step parameters for requests", required=False, type=int
    )

    parser.add_argument(
        "-p",
        "--parameters",
        help="Json file containing fix parameters to populate the template with",
        required=False
    )

    parser.add_argument(
        "-r", "--requests", help="File use to load requests and matching hash", required=True
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="Debug mode (DEBUG level)",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose mode (INFO level)",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    return args

def main():
    """
    Principal function of the script
    """
    args = cmdline_parser()

    # Load queries from provided file
    queries = Queries({}, {})
    with open(args.requests, 'r', encoding='utf8') as requests_file2:
        queries = Queries(**json.load(requests_file2))

    # Load template from provided file
    template = Template('')
    with open(args.template, 'r', encoding='utf8') as template_file:
        template = Template(template_file.read())

    # Load parameters
    parameters = {}
    if args.parameters is not None:
        if os.path.isfile(args.parameters):
            with open(args.parameters, 'r', encoding='utf8') as parameters_file:
                parameters = json.loads(parameters_file.read())
        else:
            parameters = json.loads(args.parameters)

    # Setup instant queries for JMeter
    instant_queries = {}
    for name, instant_query in queries.instant_queries.items():
        query = instant_query['query']
        time = instant_query['time']

        # If time is not defined, we replace it by 'now'
        if args.now is not None:
            if args.now == 0:
                time = "${__time(/1000)}"
            else:
                time = args.now

        query = convert_query(name, query, parameters)

        if time is None:
            raise Exception("Failed to create query: {}, one of the following parameter is not set: {{ time: {}}}".format(name, time))
        instant_queries[name] = InstantQuery(query, time)

    # Setup instant queries for JMeter
    range_queries = {}
    for name, range_query in queries.range_queries.items():
        query = range_query['query']
        start = range_query['start']
        end = range_query['end']
        step = range_query['step']

        # If start is not defined, we replace it by 'now - interval_s'
        if args.now is not None:
            if args.now == 0:
                end = "${__time(/1000)}"
            else:
                end = args.now

        if args.interval is not None:
            if args.now == 0:
                start = "${{__jexl2(${{__time(/1000)}} - {})}}".format(args.interval)
            else:
                start = end - args.interval

        if args.step is not None:
            step = args.step

        query = convert_query(name, query, parameters)

        if start is None or end is None or step is None:
            raise Exception("Failed to create query: {}, one of the following parameter is not set: {{ start: {}, end: {}, step: {} }}".format(name, end, start, step))
        range_queries[name] = RangeQuery(query, start, end, step)

    # Build JMeter test plan using the provided template
    with open(args.output, 'w', encoding='utf8') as output_file:
        output_file.write(template.render(instant_queries=instant_queries, range_queries=range_queries, parameters=parameters))

if __name__ == "__main__":
    main()
