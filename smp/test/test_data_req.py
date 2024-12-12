from smp.utils.data_req import data_requester
from smp.data.endpoints import endpoints

for key, value in endpoints.items():
    print(f"Requesting data from {key}")
    data = data_requester(value)
    print(data)
    print("--------------------------------\n\n")
      