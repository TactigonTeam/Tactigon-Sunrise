import math

def rad(num):
    return num * math.pi/180

data = {
    "pos 1 (parcheggio)": [22.5, 15.5, -55.5, 0, 51, 0, 0],
    "pos 2": [45.8, -1.7, -59.9, 0, 94.12, 0],
    "pos 3": [53.9, 25.5, -24.7, 0, 105, 0],
    "pos 4": [34.3, 28.8, -21, 0, 103.9, 0],
    "off pos":[45.1, 30.3, -7.4, 0, 80.1, 0]
}

for d in data:
    values = data[d]
    print(d, [round(rad(v), 2) for v in values])
