import json
import csv


def to_float(input: str):
    return float(input) if input else 0.


steps = []
with open('planning/october.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames
    for row in reader:
        steps.append({
            'texts': [row['text']],
            'styles': ['%s | %s' % (row['season'], row['style'])],
            'x_velocity': to_float(row['x']),
            'y_velocity': to_float(row['y']),
            'z_velocity': to_float(row['z']),
            'pan_velocity': to_float(row['pan']),
            'tilt_velocity': to_float(row['tilt']),
            'roll_velocity': to_float(row['roll']),
            'upscale': True,
        })

print(json.dumps(steps))
