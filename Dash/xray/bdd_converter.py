import json

def convert_bdd_to_json(input_file, output_file):
    with open(input_file, 'r') as file:
        bdd_text = file.read()
    
    tests = bdd_text.strip().split('#')  # Split by the separator
    result = []

    for test in tests:
        if not test.strip():  # Skip empty sections
            continue

        lines = test.strip().split('\n')
        steps = []
        examples = {}
        title = None
        in_example_section = False
        example_headers = []
        example_rows = []

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            if line.startswith("Scenario:") or line.startswith("Scenario Outline:"):
                title = line

            if line.lower().startswith("examples:"):
                in_example_section = True
                continue

            if in_example_section and '|' in line:
                row = [col.strip() for col in line.split('|') if col.strip()]
                if not example_headers:
                    example_headers = row
                else:
                    example_rows.append(row)
            elif not in_example_section:
                steps.append(line)

        if example_headers:
            for i, header in enumerate(example_headers):
                examples[header] = [row[i] for row in example_rows]

        result.append({
            "title": title,
            "steps": steps,
            "examples": examples
        })

    with open(output_file, 'w') as file:
        json.dump(result, file, indent=4)

def main():
    input_file = "/home/ubuntu/BDD/Dash/xray/all_features.txt"
    output_file = "/home/ubuntu/BDD/Dash/bdd_tests.json"
    convert_bdd_to_json(input_file, output_file)
    print(f"BDD tests have been saved in '{output_file}'")

if __name__ == "__main__":
    main()
