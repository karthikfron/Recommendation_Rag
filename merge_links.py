import os
import json

def merge_json_files(input_folder, output_file):
    merged_data = []

    # Loop through all JSON files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Extracting only the productFactSheet link from each JSON
                if "productFactSheet" in data:
                    merged_data.append({
                        "title": data.get("title"),
                        "productFactSheet": data.get("productFactSheet")
                    })
    
    # Save the merged data into one output file
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(merged_data, output, indent=4)

    print(f"Merged {len(merged_data)} files into {output_file}")

# Paths to the folders containing your JSON files
individual_folder = "individual-solutions"
pre_packed_folder = "pre-packaged-solutions"
output_file = "merged_product_fact_sheet.json"

# Merge JSON files from both folders
merge_json_files(individual_folder, output_file)
merge_json_files(pre_packed_folder, output_file)
