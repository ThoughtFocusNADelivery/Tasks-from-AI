import logging
import json
from pyannote.core import Annotation, Segment
from whisper import load_model
from datetime import datetime
from pydub import AudioSegment
import numpy as np
import io

logger = logging.getLogger(__name__)
whisper_model = load_model("base")

def parse_rttm(rttm_buffer):
    """
    Parse RTTM content from the in-memory buffer, handling unexpected fields like `<NA>`.
    """
    from pyannote.core import Annotation, Segment

    diarization = Annotation()
    rttm_buffer.seek(0)

    for line in rttm_buffer:
        parts = line.strip().split()
        if len(parts) < 9 or parts[0] != "SPEAKER":
            logger.warning(f"Skipping invalid RTTM line: {line.strip()}")
            continue

        try:
            # Extract relevant fields while ignoring `<NA>` placeholders
            _, _, _, start_time, duration, _, _, speaker, *_ = parts
            start_time = float(start_time)
            duration = float(duration)
            segment = Segment(start_time, start_time + duration)
            diarization[segment] = speaker
        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing RTTM line: {line.strip()} - {e}")
            continue

    return diarization

def preprocess_audio_segment(segment, audio_file, language="en"):
    """
    Extract and transcribe a segment of audio using the Whisper model.
    """
    try:
        # Convert in-memory audio file to pydub AudioSegment
        audio_file.seek(0)
        full_audio = AudioSegment.from_file(audio_file)

        # Extract the audio segment
        start_ms = int(segment.start * 1000)  # Convert seconds to milliseconds
        end_ms = int(segment.end * 1000)  # Convert seconds to milliseconds
        segment_audio = full_audio[start_ms:end_ms]

        # Export the segment to a temporary in-memory buffer
        temp_audio = io.BytesIO()
        segment_audio.export(temp_audio, format="wav")
        temp_audio.seek(0)

        # Convert the audio segment to a NumPy array
        audio_segment = AudioSegment.from_file(temp_audio)
        samples = np.array(audio_segment.get_array_of_samples())

        # Normalize the audio to the range [-1.0, 1.0]
        samples = samples.astype(np.float32) / np.iinfo(samples.dtype).max

        # Transcribe with Whisper
        result = whisper_model.transcribe(samples, language=language)
        temp_audio.close()

        return result["text"].strip()
    except Exception as e:
        logger.error(f"Error transcribing segment {segment}: {e}")
        return ""

def process_transcript(base_name, rttm_buffer, audio_file, title, participants, transcript_path, location="Video Call", language="en"):
    """
    Process the in-memory RTTM file and audio file to generate a transcript.
    """
    try:
        diarization = parse_rttm(rttm_buffer)

        dialog = []
        speakers = set()  # To track unique speakers dynamically
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            statement = preprocess_audio_segment(segment, audio_file, language=language)
            if statement:
                dialog.append({"Speaker": speaker, "Statement": statement})
                speakers.add(speaker)

        # Update participants dynamically with unique speaker labels
        participants = sorted(speakers)

        transcript = {
            "Meeting": {
                "Title": title,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Location": location,
                "Participants": participants,
                "Dialog": dialog,
                "ClosingNote": "End of meeting transcript."
            }
        }

        with open(transcript_path, "w") as f:
            json.dump(transcript, f, indent=4)
        logger.info(f"Transcript saved to {transcript_path}")
    except Exception as e:
        logger.error(f"Error processing transcript for {base_name}: {e}")

