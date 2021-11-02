import json
import csv
from re import split


def to_float(input: str):
    return float(input) if input else 0.


steps = []
with open('planning/october.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames
    ground = None
    for row in reader:
        row_ground = split('[^a-z]', row['ground'])[0]
        if ground is None:
            ground = row_ground

        if row_ground != ground:
            ground = row_ground
            steps.append({
                'texts': ['a burst of flames, a flash of burning fire'],
                'x_velocity': to_float(row['x']),
                'y_velocity': to_float(row['y']),
                'z_velocity': to_float(row['z']),
                'pan_velocity': to_float(row['pan']),
                'tilt_velocity': to_float(row['tilt']),
                'roll_velocity': to_float(row['roll']),
                'upscale': True,
                'interpolate': True,
                'epochs': 5,
                'iterations': 150,
                'transition': 5,
            })

        steps.append({
            'texts': [row['text']],
            'styles': ['%s | %s' % (row['ground'], row['style'])],
            'x_velocity': to_float(row['x']),
            'y_velocity': to_float(row['y']),
            'z_velocity': to_float(row['z']),
            'pan_velocity': to_float(row['pan']),
            'tilt_velocity': to_float(row['tilt']),
            'roll_velocity': to_float(row['roll']),
            'upscale': True,
            'interpolate': True,
            'epochs': 42,
            'iterations': 75,
        })

print(json.dumps({
    "spec": {
        "videos": [
            {
                "steps": steps
            }
        ]
    }
}))
