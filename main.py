import os
import logging
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from identify_speakers import initialize_pipeline, preprocess_audio, refine_diarization
from transcript import process_transcript

# Load configuration
CONFIG_FILE = "config.json"
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)

DATA_FOLDER = config["folders"]["data_folder"]
TRANSCRIPT_FOLDER = config["folders"]["transcript_folder"]
LOG_FOLDER = config["folders"]["log_folder"]

os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

def setup_logger(audio_file_name, debug_mode=False):
    """
    Set up a logger for the current audio file.
    Includes INFO and ERROR level logs and supports DEBUG mode.
    """
    log_file_name = f"{audio_file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file_path = os.path.join(LOG_FOLDER, log_file_name)

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    # Check if handlers are already attached to avoid duplicates
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        # Create file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)

        # Create stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)

        # Set formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return log_file_path

def process_file(input_file, pipeline, title="Meeting", participants=None, location="Video Call"):
    """
    Process a single audio file: preprocess, diarize, and generate a transcript.
    """
    if participants is None:
        participants = []

    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Set up logger for this file
    log_file_path = setup_logger(base_name)
    logger = logging.getLogger(__name__)
    logger.info(f"Processing file: {input_file}")

    processed_audio = preprocess_audio(input_file)
    if not processed_audio:
        logger.warning(f"Skipping {input_file} due to preprocessing errors.")
        return

    try:
        diarization = pipeline(processed_audio)
        refined_diarization, rttm_buffer = refine_diarization(diarization)

        transcript_path = os.path.join(TRANSCRIPT_FOLDER, f"{base_name}.json")
        process_transcript(base_name, rttm_buffer, processed_audio, title, participants, transcript_path, location)

    finally:
        processed_audio.close()
        rttm_buffer.close()
        logger.info(f"Cleared memory for {input_file}")
        logger.info(f"Log file saved at {log_file_path}")

if __name__ == "__main__":
    # Initialize the pipeline
    HUGGING_FACE_ACCESS_TOKEN = os.getenv("HUGGING_FACE_ACCESS_TOKEN")
    pipeline = initialize_pipeline(HUGGING_FACE_ACCESS_TOKEN)

    if not pipeline:
        logging.error("Failed to initialize the pipeline.")
        exit(1)

    # Gather audio files from the data folder
    audio_files = [os.path.join(DATA_FOLDER, file) for file in os.listdir(DATA_FOLDER) if file.endswith(".wav")]

    if not audio_files:
        logging.warning(f"No audio files found in {DATA_FOLDER}.")
    else:
        with ThreadPoolExecutor() as executor:
            executor.map(lambda file: process_file(file, pipeline, "Meeting", ["Participant1", "Participant2"]), audio_files)
