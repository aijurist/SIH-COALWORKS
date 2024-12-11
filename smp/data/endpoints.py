# endpoints = {
#     "get_user": "http://localhost:8080/get_user",
#     "get_data": "http://localhost:8080/get_data",
#     "get_smp": "http://localhost:8080/get_smp",
#     "get_iot_data": "http://localhost:8080/get_iot_data",
#     "get_minutes_of_meetings": "http://localhost:8080/get_minutes_of_meetings",
#     "get_compliance": "http://localhost:8080/get_compliance",
#     "get_geographical_features": "http://localhost:8080/get_geographical_features",    
# }

endpoints = {
    "get_asset": "http://192.168.173.53:3000/api/v1/asset",
    "get_asset_type": "http://192.168.173.53:3000/api/v1/assettype",   
    "get_position": "http://192.168.173.53:3000/api/v1/position", 
    "get_round": "http://192.168.173.53:3000/api/v1/rounds",
    "get_mine_info": "http://192.168.173.53:3000/api/v1/mine",
    "get_shift_info": "http://192.168.173.53:3000/api/v1/shift",
    "get_user_info": "http://192.168.173.53:3000/api/v1/user",
    "get_smp_info": "http://192.168.173.53:3000/api/v1/smp"
}

endpoints = {
    "get_asset": "http://192.168.173.53:3000/api/v1/asset",
    "get_asset_type": "http://192.168.173.53:3000/api/v1/assettype",   
    "get_position": "http://192.168.173.53:3000/api/v1/position", 
    "get_round": "http://192.168.173.53:3000/api/v1/rounds",
    "get_mine_info": "http://192.168.173.53:3000/api/v1/mine",
    "get_shift_info": "http://192.168.137.88:3000/api/v1/shift",
    "get_user_info": "http://192.168.137.88:3000/api/v1/user",
    "get_smp_info": "http://192.168.137.88:3000/api/v1/smp",
    # "get_iot_info": "http://192.168.137.88:3000/api/v1/iot"
}

mapping = {
    "get_shift_info": "shift",
    "get_user_info": "user",
    "get_smp_info": "smp",
    # "get_iot_info": "iot"
}