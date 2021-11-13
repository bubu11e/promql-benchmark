# promql-benchmark
Tool to benchmark PromQL endpoint performances

# Why
A PromQL query can be addressed to two endpoints :
 - /query for instant query taking as arguments a query, a time and
 - /query_range for range query taking as arguments a query, a start an end and a step
as explained here : https://prometheus.io/docs/prometheus/latest/querying/api/#instant-queries

This tool aims to simplify the generation of JMeter test plans for such query.

To build test representing a real workload, there are two phases:
 - The first one is to extract queries from production tools and this is the reason to be of the first script (grafana_dashboard_to_query.py) which can be used to convert an existing PromQL Grafana dashboard into a set of queries.
 - The second step is to schedule those tests among an infrastructure, we decided to go with JMeter test tool as PromQL requests are first of all HTTP requests. The second script (generate_test_plan) is here to generate a JMeter test plan using previously extracted requests and a provided template.

# ToDo
 - Implements instant queries conversion (today all queries are considered as range queries)