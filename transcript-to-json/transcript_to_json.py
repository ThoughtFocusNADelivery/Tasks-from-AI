import openai
import json
from dotenv import load_dotenv
import os
import logging
from openai import OpenAI
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
logging.debug(f"OpenAI API Key: {openai_api_key}")
if not openai_api_key:
    logging.error("OpenAI API key not found. Please set it in the .env file.")
    exit(1)

openai.api_key = openai_api_key

def analyze_transcript(file_path):
    """
    Analyzes a meeting transcript to extract high-level features and formats them into a JSON object.

    Args:
        file_path (str): The path to the transcript text file.
    """
    logging.info(f"Starting analysis for {file_path}")
    logging.info(f"Reading transcript from {file_path}")

    # Read the transcript from the file
    try:
        with open(file_path, 'r') as file:
            transcript = file.read()
    except FileNotFoundError:
        logging.error(f"Transcript file {file_path} not found.")
        return
    except Exception as e:
        logging.error(f"Error reading transcript file: {e}")
        return

    # Define the prompt for the OpenAI API, including the transcript
    prompt = (
        "Extract the tasks and epics discussed in the meeting transcript and format them into a JSON object. "
        "Each task and epic should include a title, description, status, priority, and other relevant details. "
        "Use the following JSON structure (JSON object only as plain text, do not add any code blocks):\n\n"
        "{\n"
        "    \"tasks\": [\n"
        "        {\n"
        "            \"title\": \"Task Title\",\n"
        "            \"description\": \"Brief description of the task\",\n"
        "            \"status\": \"todo | in-progress | done\",\n"
        "            \"priority\": \"low | medium | high\",\n"
        "            \"points\": Numeric value representing task complexity or importance,\n"
        "            \"subtasks\": [\n"
        "                {\n"
        "                    \"title\": \"Subtask Title\",\n"
        "                    \"status\": \"todo | in-progress | done\"\n"
        "                }\n"
        "            ]\n"
        "        }\n"
        "    ],\n"
        "    \"epics\": [\n"
        "        {\n"
        "            \"title\": \"Epic Title\",\n"
        "            \"description\": \"Brief description of the epic\",\n"
        "            \"status\": \"todo | in-progress | done\",\n"
        "            \"priority\": \"low | medium | high\",\n"
        "            \"isEpic\": true,\n"
        "            \"childTasks\": [\n"
        "                {\n"
        "                    \"title\": \"Child Task Title\",\n"
        "                    \"status\": \"todo | in-progress | done\",\n"
        "                    \"priority\": \"low | medium | high\"\n"
        "                }\n"
        "            ]\n"
        "        }\n"
        "    ]\n"
        "}\n\n"
        "Ensure that all tasks and epics from the transcript are included accurately. "
        "Only include relevant information about the project's tasks and epics, leaving out unrelated discussions.\n\n"
        "Transcript:\n"
        f"{transcript}"
    )

    logging.info("Sending request to OpenAI API")

    # Call the OpenAI API
    try:
        client = OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        # Extract the JSON serializable part of the response
        response_data = response.to_dict()  # Convert the response to a dictionary
        # Log the response JSON with proper formatting
        logging.debug("OpenAI API response: %s", json.dumps(response_data, indent=4))
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return

    # Parse the response
    features = response.choices[0].message.content.strip()
    logging.info("Received response from OpenAI API")

    # Convert the response to a JSON object
    try:
        features_json = json.loads(features)
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON. Please check the response format.")
        return

    # Write the JSON object to a file
    output_file_path = 'features.json'
    logging.debug(f"Output file path: {output_file_path}")
    try:
        with open(output_file_path, 'w') as json_file:
            json.dump(features_json, json_file, indent=4)
        logging.info(f"Features extracted and saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing to output file: {e}")

    logging.info("Finished analysis")

# Example usage
if __name__ == "__main__":
    analyze_transcript('transcript.txt')