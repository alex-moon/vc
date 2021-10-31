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
        if season is None:
            season = row['season']

        if row['season'] != season:
            season = row['season']
            steps.append({
                'texts': ['a burst of flames, a flash of burning fire | %s' % row['text']],
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
                'iterations': 200,
                'transition': 1,
            })

        steps.append({
            'texts': [row['text']],
            'styles': ['%s _ | %s' % (row['season'], row['style'])],
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
