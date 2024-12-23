import openai
import json

# Set your OpenAI API key
openai.api_key = 'your-api-key-here'

def analyze_transcript(file_path):
    # Read the transcript from the file
    with open(file_path, 'r') as file:
        transcript = file.read()

    # Define the prompt
    prompt = (
        "Extract the high-level features discussed in the meeting transcript and format them into a JSON object. "
        "Each feature should include a brief description and, if applicable, associated sub-features or requirements."
    )

    # Call the OpenAI API
    response = openai.Completion.create(
        engine="gpt-4o",  # Use the appropriate engine
        prompt=prompt + "\n\n" + transcript,
        max_tokens=1500,  # Adjust as needed
        temperature=0.5  # Adjust as needed
    )

    # Parse the response
    features = response.choices[0].text.strip()

    # Convert the response to a JSON object
    try:
        features_json = json.loads(features)
    except json.JSONDecodeError:
        print("Failed to decode JSON. Please check the response format.")
        return

    # Write the JSON object to a file
    output_file_path = 'features.json'
    with open(output_file_path, 'w') as json_file:
        json.dump(features_json, json_file, indent=4)

    print(f"Features extracted and saved to {output_file_path}")

# Example usage
analyze_transcript('transcript.txt')