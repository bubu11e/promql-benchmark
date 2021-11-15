#!/usr/bin/env python3
"""
This module aims to help extracting grafana dashboard queries into a json file.
"""

import json
import argparse
import logging
from queries import InstantQuery, Queries, RangeQuery

def find_queries(obj):
    """
    This function is used to convert a Grafana dashboard into a Queries object
    """
    queries = Queries({}, {})
    if isinstance(obj, dict):
        if 'targets' in obj and 'type' in obj:
            if obj['type'] in [ "gauge", "singlestat" ]:
                for target in obj['targets']:
                    queries.add_instant_query(InstantQuery(target['expr'], None))
            if obj['type'] == "graph":
                for target in obj['targets']:
                    queries.add_range_query(RangeQuery(target['expr'], None, None, None))

        for _, value in obj.items():
            queries.merge(find_queries(value))
    if isinstance(obj, list):
        for element in obj:
            if isinstance(element, dict):
                queries.merge(find_queries(element))

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
        queries = find_queries(dashboard)

    # Save queries into provided file
    with open(args.requests, 'w', encoding='utf8') as requests_file:
        requests_file.write(json.dumps(
            queries, default=lambda o: o.__dict__, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
