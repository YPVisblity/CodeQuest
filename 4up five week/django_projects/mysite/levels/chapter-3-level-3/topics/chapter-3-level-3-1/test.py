result1 = clean_sensor_data([
    {"sensor": "溫度A","value": 25.3},
    {"sensor": "溫度B","value": None},
    {"sensor": "濕度A","value": 60},
])

result2 = clean_sensor_data([
    {"sensor": "X","value": None},
    {"sensor": "Y","value": None},
])

result3 = clean_sensor_data([
    {"sensor": "Z1","value": 0},
    {"sensor": "Z2","value": 100},
])
