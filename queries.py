"""
This module aims to represent PromQL queries
"""
from typing import Dict

class InstantQuery:
    """
    This class represent an instant query ans it's parameters.
    """
    def __init__(self, query: str, time: int):
        self.query = query
        self.time = time

    def __eq__(self, other):
        return self.query == other.query and self.time == other.time

    def __hash__(self):
        return hash((self.query, self.time))

class RangeQuery:
    """
    This class represent a range query and it's parameters
    """
    def __init__(self, query:str, start: int, end: int, step: int):
        self.query = query
        self.start = start
        self.end = end
        self.step = step

    def __eq__(self, other):
        return (self.query == other.query and self.start == other.start and self.end == other.end and self.step == other.step)

    def __hash__(self):
        return hash((self.query, self.start, self.end, self.step))

class Queries:
    """
    This class represent two set of queries, one for the instant one and one for the range one.
    """
    def __init__(self, instant_queries: Dict[str, InstantQuery],range_queries: Dict[str, RangeQuery]):
        self.range_queries = range_queries if range_queries else {}
        self.instant_queries = instant_queries if instant_queries else {}

    def add_range_query(self, query):
        """
        Add a range query to the set
        """
        self.range_queries[hex(hash(query))] = query

    def add_instant_query(self, query):
        """
        Add an instant query to the set
        """
        self.instant_queries[hex(hash(query))] = query

    def merge(self, other):
        """
        Merge an other Queries object into this one
        """
        self.instant_queries.update(other.instant_queries)
        self.range_queries.update(other.range_queries)

    def __str__(self):
        return str(self.__dict__)
