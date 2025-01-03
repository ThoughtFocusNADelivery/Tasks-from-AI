# Speaker labelling and Transcription

This project makes use of Pyannote.audio and WHisper by OpenAI to analysis call recording to provide speaker diarization, speaker labelling and transcript JSON generation.
## Table of Content
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)

---

## Prerequisites

Before running the project, make sure you have the following installed:

1. **Python 3.12.x**: Python 3.12.x must be installed on your machine. You can download it from [python.org](https://www.python.org/downloads/) or [Microsoft Store](https://apps.microsoft.com/detail/9NCVDN91XZQP?hl=en-us&gl=US&ocid=pdpshare).

2. OpenAI API Key from [OpenAI](https://platform.openai.com/signup/)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone --branch feature/ATA-76 https://github.com/ThoughtFocusNADelivery/Tasks-from-AI.git
   cd Tasks-from-AI
   ```

2. **Set Up a Python Virtual Environment**:
   ```bash
   python3.12 -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Setup .evn with your OpenAI API and HuggingFace API key in the root of the project folder**
   ```bash
   HUGGING_FACE_ACCESS_TOKEN = [YOUR-API-KEY]
   OPENAI_API_KEY = [YOUR-API-KEY]
   ```

2. **Setup config.json with output path for transcript and log files(Optional)**
   ```
   {
    "folders": {
    "data_folder": "./data/audio",
    "transcript_folder": "./transcript",
    "log_folder": "./data/log"
      }
   }
   ```

## Running the Project

1. **Navigate to /Tasks-from-AI folder in the terminal**

2. **Place the audio file in ./data/audio folder**
 
3. **Run the python file**
   ```bash
   python main.py
   ```

## Note

- The output transcript file is saved in ./transcript
- The log files are stored in ./data/log
