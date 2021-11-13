#!/usr/bin/env python3
"""
This module aims to help extracting grafana dashboard queries into a json file.
"""

import json
import argparse
import logging
from queries import Queries, RangeQuery

def find_expr(obj, key):
    """
    This function is used to convert a Grafana dashboard into a Queries object
    """
    queries = Queries({}, {})
    if key in obj:
        queries.add_range_query(RangeQuery(query=obj[key], start=None, end=None, step=None))

    for _,value in obj.items():
        if isinstance(value, dict):
            queries.merge(find_expr(value, key))
        if isinstance(value, list):
            for element in value:
                if isinstance(element, dict):
                    queries.merge(find_expr(element, key))

    return queries

def cmdline_parser():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Script use to convert Grafana dashboard into JMeter test plan for PromQL endpoint"
    )

    parser.add_argument(
        "-g", "--grafana-dashboard",
        help="Dashboard to convert into test",
        required=True
    )

    parser.add_argument(
        "-r", "--requests",
        help="File use to store requests found into dashboard and matching hash",
        required=True
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

    # Convert dashboard into queries
    queries = Queries({}, {})
    with open(args.grafana_dashboard, 'r', encoding='utf8') as dashboard_file:
        dashboard = json.load(dashboard_file)
        queries = find_expr(dashboard, 'expr')

    # Save queries into provided file
    with open(args.requests, 'w', encoding='utf8') as requests_file:
        requests_file.write(json.dumps(
            queries, default=lambda o: o.__dict__, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
