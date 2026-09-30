result1 = average_sensor_value([
    {"sensor": "溫度A", "value": 20},
    {"sensor": "溫度B", "value": None},
    {"sensor": "溫度C", "value": 30},
])

result2 = average_sensor_value([
    {"sensor": "X", "value": None},
    {"sensor": "Y", "value": None},
])

result3 = average_sensor_value([
    {"sensor": "Z1", "value": 10},
    {"sensor": "Z2", "value": 15},
    {"sensor": "Z3", "value": 20},
])
