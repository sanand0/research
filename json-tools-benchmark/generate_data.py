#!/usr/bin/env python3
"""
Generate test JSON data of various sizes and structures
"""
import json
import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_simple_objects(count):
    """Generate array of simple objects"""
    return [
        {
            "id": i,
            "name": random_string(20),
            "value": random.randint(1, 1000),
            "active": random.choice([True, False]),
            "category": random.choice(["A", "B", "C", "D"]),
            "score": round(random.uniform(0, 100), 2)
        }
        for i in range(count)
    ]

def generate_nested_objects(count):
    """Generate array of nested objects"""
    return [
        {
            "id": i,
            "user": {
                "name": random_string(15),
                "email": f"{random_string(10)}@example.com",
                "profile": {
                    "age": random.randint(18, 80),
                    "location": {
                        "city": random_string(10),
                        "country": random_string(10),
                        "coordinates": {
                            "lat": round(random.uniform(-90, 90), 6),
                            "lng": round(random.uniform(-180, 180), 6)
                        }
                    }
                }
            },
            "posts": [
                {
                    "id": j,
                    "title": random_string(30),
                    "views": random.randint(0, 10000),
                    "likes": random.randint(0, 1000)
                }
                for j in range(random.randint(1, 5))
            ],
            "metadata": {
                "created": "2025-01-01T00:00:00Z",
                "updated": "2025-01-10T00:00:00Z",
                "tags": [random_string(5) for _ in range(random.randint(1, 8))]
            }
        }
        for i in range(count)
    ]

# Generate small dataset (1K objects)
print("Generating small.json (1K objects)...")
with open('data/small.json', 'w') as f:
    json.dump(generate_simple_objects(1000), f)

# Generate medium dataset (10K objects)
print("Generating medium.json (10K objects)...")
with open('data/medium.json', 'w') as f:
    json.dump(generate_simple_objects(10000), f)

# Generate large dataset (100K objects)
print("Generating large.json (100K objects)...")
with open('data/large.json', 'w') as f:
    json.dump(generate_simple_objects(100000), f)

# Generate nested dataset (10K objects)
print("Generating nested.json (10K nested objects)...")
with open('data/nested.json', 'w') as f:
    json.dump(generate_nested_objects(10000), f)

# Generate single large object
print("Generating single_object.json...")
with open('data/single_object.json', 'w') as f:
    json.dump({
        "status": "success",
        "data": {
            "items": generate_simple_objects(1000),
            "metadata": {
                "total": 1000,
                "page": 1,
                "pageSize": 1000
            }
        }
    }, f)

print("Test data generation complete!")
