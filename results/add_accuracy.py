import json
import os

# Set the path to the "results" directory
results_dir = "results"

# Iterate over all files in the "results" directory
for filename in os.listdir(results_dir):
    # Check if the file has a ".json" extension
    if filename.endswith(".json"):
        # Construct the full file path
        file_path = os.path.join(results_dir, filename)

        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Check if the "per question results" field exists
        if len(data['per_question_results']):
            # Compute the size of the "per question results" list
            size_of_dataset = len(data['per_question_results'])
        else:
            # Set the size of the dataset to 1000 if the field is missing
            size_of_dataset = 1000

        # Add the "size_of_dataset" field to the "summary" field
        data['summary']['size_of_dataset'] = size_of_dataset

        accuracy_fields = {}
        for key, value in data['summary'].items():
            if "correct" in key:
                accuracy_key = key.replace("correct", "accuracy")
                accuracy_fields[accuracy_key] = value / size_of_dataset

        # Update the "summary" dictionary with the accuracy fields
        data['summary'].update(accuracy_fields)

        # Write the updated JSON data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

print("Size of the dataset added to the summary field for all JSON files.")
