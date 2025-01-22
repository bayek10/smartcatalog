# PURPOSE: for each example in dataset, if ground truth empty, set it equal to model output 
# (means I've already checked & the model output was correct)

import json
import glob

# Path to your dataset directory - adjust this path as needed
dataset_path = "./dataset/*/data.json"

# Process each data.json file
for file_path in glob.glob(dataset_path):
    # Skip table_010
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if len(data.get('ground_truth', [])) > 0:
            print(f"Skipping (non-empty ground_truth): {file_path}")
            continue

        # Set ground_truth equal to model_output
        data['ground_truth'] = data['model_output']
        
        # Write back to the file with proper indentation
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Updated: {file_path}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

print("Done!")