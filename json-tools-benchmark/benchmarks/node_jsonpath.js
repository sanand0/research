#!/usr/bin/env node
/**
 * Node.js JSONPath benchmark
 */

const jp = require('jsonpath-plus');

const task = process.argv[2];

// Read stdin
let inputData = '';
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
    const data = JSON.parse(inputData);

    switch(task) {
        case 'select_name':
            const names = jp.JSONPath({ path: '$[*].name', json: data });
            names.forEach(name => console.log(name));
            break;

        case 'filter_value':
            const filtered = jp.JSONPath({
                path: '$[?(@.value > 500)]',
                json: data
            });
            filtered.forEach(item => console.log(JSON.stringify(item)));
            break;

        case 'map_value':
            const values = jp.JSONPath({ path: '$[*].value', json: data });
            const mapped = values.map(v => v * 2);
            console.log(JSON.stringify(mapped));
            break;

        case 'sum_values':
            const vals = jp.JSONPath({ path: '$[*].value', json: data });
            const sum = vals.reduce((acc, v) => acc + v, 0);
            console.log(sum);
            break;

        case 'deep_nested':
            const cities = jp.JSONPath({
                path: '$[*].user.profile.location.city',
                json: data
            });
            cities.forEach(city => console.log(city));
            break;

        default:
            console.error('Unknown task:', task);
            process.exit(1);
    }
});
