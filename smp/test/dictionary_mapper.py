from smp.data.endpoints import endpoints, mapping
from smp.utils.data_req import queries

for key, value in mapping.items():
    endpoint_url = endpoints[key]
    query = queries[value]
    print("endpoint_url:", endpoint_url, "query:", query)