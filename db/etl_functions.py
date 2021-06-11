import json

# Write to JSON file in readable format
def to_json(data, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'{file} written')