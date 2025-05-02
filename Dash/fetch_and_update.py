import os
import json


def fetch_data(directory):
    data = {
        'qa': [],
        'cp': [],
        'av': []
    }

    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    for filename in files:
        filepath = os.path.join(directory, filename)
        html_filename = filename.replace('.json', '.html')
        base_file_name = html_filename.split(".")[0]

        with open(filepath, 'r') as f:
            json_data = json.load(f)
            for hit in json_data['hits']['hits']:
                source = hit['_source']
                name = source['name']
                status = source['status']
                start_time = source['time']['start']
                duration = source['time']['duration']
                tag = source['properties']['tag']
                parent_uid = source['parentUid']
                if 'qa' in tag:
                    category = 'qa'
                elif 'av' in tag or "prod-3" in tag:
                    category = 'av'
                elif 'cp' in tag:
                    category = 'cp'

                farm = tag.split('_')[0]
                cluster = tag.split('_')[1]

                entry = {
                    'name': name,
                    'status': status,
                    'start_time': start_time,
                    'duration': duration,
                    'farm': farm,
                    'cluster': cluster,
                    'filename': html_filename,
                    'parentUid': parent_uid,
                    'category': category
                }

                if tag == base_file_name:
                    if 'qa' in tag:
                        data['qa'].append(entry)
                    elif 'cp' in tag:
                        data['cp'].append(entry)
                    elif 'av' in tag or 'prod-3' in tag:
                        data['av'].append(entry)

    return data


def main():
    # Directory containing JSON files
    DOWNLOAD_DIR = "/home/ubuntu/BDD/Dash/static/downloaded-reports"
    output_file = "/home/ubuntu/BDD/Dash/static/data.json"
    # Fetch data from JSON files
    data = fetch_data(DOWNLOAD_DIR)

    # Write data to data.json file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Generated data file: {output_file}")


if __name__ == "__main__":
    main()
