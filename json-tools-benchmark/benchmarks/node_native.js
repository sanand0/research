#!/usr/bin/env node
/**
 * Node.js native JSON processing benchmark
 */

const fs = require('fs');

const task = process.argv[2];

// Read stdin
let inputData = '';
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
    const data = JSON.parse(inputData);

    switch(task) {
        case 'select_name':
            data.forEach(item => console.log(item.name));
            break;

        case 'filter_value':
            const filtered = data.filter(item => item.value > 500);
            filtered.forEach(item => console.log(JSON.stringify(item)));
            break;

        case 'map_value':
            const mapped = data.map(item => item.value * 2);
            console.log(JSON.stringify(mapped));
            break;

        case 'sum_values':
            const sum = data.reduce((acc, item) => acc + item.value, 0);
            console.log(sum);
            break;

        case 'deep_nested':
            data.forEach(item => {
                try {
                    const city = item.user?.profile?.location?.city;
                    if (city) console.log(city);
                } catch(e) {}
            });
            break;

        default:
            console.error('Unknown task:', task);
            process.exit(1);
    }
});
