from smp.data.endpoints import endpoints, mapping
from smp.utils.data_req import data_requester

host_url = "http://192.168.1:3000"

for key, value in endpoints.items():
    res = data_requester(endpoint_url=host_url+value)
    print(res,"\n", "-"*75)