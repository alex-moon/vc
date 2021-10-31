import json
import csv


def to_float(input: str):
    return float(input) if input else 0.


steps = []
with open('planning/october.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames
    ground = None
    for row in reader:
        if ground is None:
            ground = row['ground']

        if row['ground'] != ground:
            ground = row['ground']
            steps.append({
                'texts': ['a burst of flames, a flash of burning fire'],
                'styles': ['%s _ | %s' % (row['ground'], row['style'])],
                'x_velocity': to_float(row['x']),
                'y_velocity': to_float(row['y']),
                'z_velocity': to_float(row['z']),
                'pan_velocity': to_float(row['pan']),
                'tilt_velocity': to_float(row['tilt']),
                'roll_velocity': to_float(row['roll']),
                'upscale': True,
                'interpolate': True,
                'epochs': 5,
                'iterations': 200,
                'transition': 5,
            })

        steps.append({
            'texts': [row['text']],
            'styles': ['%s _ | %s' % (row['ground'], row['style'])],
            'x_velocity': to_float(row['x']),
            'y_velocity': to_float(row['y']),
            'z_velocity': to_float(row['z']),
            'pan_velocity': to_float(row['pan']),
            'tilt_velocity': to_float(row['tilt']),
            'roll_velocity': to_float(row['roll']),
            'upscale': True,
            'interpolate': True,
            'epochs': 10,
            'transition': 10,
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
