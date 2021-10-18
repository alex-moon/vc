import json
import csv


def to_float(input: str):
    return float(input) if input else 0.


steps = []
with open('planning/october.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames
    season = None
    for row in reader:
        if season is not None and row['season'] != season:
            season = row['season']
            steps.append({
                'texts': ['a burst of flames, a flash of burning fire'],
                'styles': ['%s | %s' % (row['season'], row['style'])],
                'x_velocity': to_float(row['x']),
                'y_velocity': to_float(row['y']),
                'z_velocity': to_float(row['z']),
                'pan_velocity': to_float(row['pan']),
                'tilt_velocity': to_float(row['tilt']),
                'roll_velocity': to_float(row['roll']),
                'upscale': True,
                'interpolate': True,
                'epochs': 1,
                'iterations': 75,
            })
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
            'interpolate': True,
            'epochs': 10,
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
