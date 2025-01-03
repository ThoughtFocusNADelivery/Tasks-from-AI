import io
import logging
from pydub import AudioSegment
from pyannote.audio import Pipeline
from pyannote.core import Annotation

logger = logging.getLogger(__name__)

def initialize_pipeline(hugging_face_access_token):
    """
    Initialize the speaker diarization pipeline.
    """
    try:
        logger.info("Loading the speaker diarization pipeline...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hugging_face_access_token
        )
        logger.info("Pipeline loaded successfully!")
        return pipeline
    except Exception as e:
        logger.error(f"Error loading pipeline: {e}")
        return None

def preprocess_audio(input_path):
    """
    Preprocess audio using pydub: convert to mono and resample to 16kHz.
    Store the processed audio in memory instead of saving to a file.
    """
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        processed_audio = io.BytesIO()
        audio.export(processed_audio, format="wav")
        processed_audio.seek(0)  # Reset the pointer for reading
        logger.info(f"Processed audio for {input_path} stored in memory.")
        return processed_audio
    except Exception as e:
        logger.error(f"Error preprocessing {input_path}: {e}")
        return None

def refine_diarization(diarization, min_segment_duration=0.5):
    """
    Refine diarization by merging short segments and assigning consistent labels.
    Save the refined diarization as an in-memory RTTM file.
    """
    refined_diarization = Annotation()
    speaker_mapping = {}
    speaker_count = 1

    for segment, _, label in diarization.itertracks(yield_label=True):
        if segment.duration < min_segment_duration:
            continue

        if label not in speaker_mapping:
            speaker_mapping[label] = f"SPEAKER_{speaker_count:02d}"
            speaker_count += 1

        refined_label = speaker_mapping[label]
        refined_diarization[segment] = refined_label

    # Save RTTM content to in-memory file
    rttm_buffer = io.StringIO()
    refined_diarization.write_rttm(rttm_buffer)
    rttm_buffer.seek(0)  # Reset buffer for reading
    logger.info("RTTM file saved in memory.")

    return refined_diarization, rttm_buffer
