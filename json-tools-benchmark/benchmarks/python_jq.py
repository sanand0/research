#!/usr/bin/env python3
"""
Python jq bindings benchmark
"""
import sys
import jq
import json

task = sys.argv[1]
input_text = sys.stdin.read()

if task == 'select_name':
    program = jq.compile('.[].name')
    for result in program.input_text(input_text):
        print(result)

elif task == 'filter_value':
    program = jq.compile('.[] | select(.value > 500)')
    for result in program.input_text(input_text):
        print(json.dumps(result))

elif task == 'map_value':
    program = jq.compile('[.[] | .value * 2]')
    result = program.input_text(input_text).first()
    print(json.dumps(result))

elif task == 'sum_values':
    program = jq.compile('[.[] | .value] | add')
    result = program.input_text(input_text).first()
    print(result)

elif task == 'deep_nested':
    program = jq.compile('.[].user.profile.location.city // empty')
    for result in program.input_text(input_text):
        print(result)

else:
    print(f'Unknown task: {task}', file=sys.stderr)
    sys.exit(1)
