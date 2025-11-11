#!/usr/bin/env python3
"""
Python native JSON processing benchmark
"""
import sys
import json

task = sys.argv[1]
data = json.load(sys.stdin)

if task == 'select_name':
    for item in data:
        print(item['name'])

elif task == 'filter_value':
    for item in data:
        if item['value'] > 500:
            print(json.dumps(item))

elif task == 'map_value':
    mapped = [item['value'] * 2 for item in data]
    print(json.dumps(mapped))

elif task == 'sum_values':
    total = sum(item['value'] for item in data)
    print(total)

elif task == 'deep_nested':
    for item in data:
        try:
            city = item.get('user', {}).get('profile', {}).get('location', {}).get('city')
            if city:
                print(city)
        except (KeyError, AttributeError):
            pass

else:
    print(f'Unknown task: {task}', file=sys.stderr)
    sys.exit(1)
