from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import wave
import pyaudio
import keyboard
import time
import os

# Load environment variables
load_dotenv()
email = os.getenv("MEETING_EMAIL")
password = os.getenv("MEETING_PASSWORD")
bot_name = "MeetingBot"  # Set the bot name here

driver = None
stop_event, audio_thread = None, None

# Function to start audio recording
def start_audio_recording(audio_file):
    """Start recording system audio and save it to a file."""
    global stop_event, audio_thread
    stop_event = threading.Event()

    def record_audio():
        print("Starting audio recording...")
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=2,
                            rate=44100,
                            input=True,
                            frames_per_buffer=1024)
        frames = []
        try:
            while not stop_event.is_set():  # Stop recording when event is set
                data = stream.read(1024)
                frames.append(data)
        except Exception as e:
            print("Error during audio recording:", e)
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
            print(f"Audio recording saved to {audio_file}")

    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()

# Setup Chrome driver with options
def setup_chrome_driver():
    """Set up Chrome WebDriver with options."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--use-fake-ui-for-media-stream")  # Disable mic/camera permission pop-ups
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")

    chrome_prefs = {
        "profile.default_content_setting_values.media_stream_camera": 1,  # Allow camera
        "profile.default_content_setting_values.media_stream_mic": 1,     # Allow mic
        "profile.default_content_setting_values.notifications": 2,        # Block notifications
        "protocol_handler.excluded_schemes.ms-teams": True                # Block external protocol pop-ups
    }
    options.add_experimental_option("prefs", chrome_prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service("D:/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

# Function to handle native pop-up
def dismiss_permission_popup_fallback():
    """Fallback to handle pop-up using keyboard."""
    print("Attempting to dismiss the pop-up using keyboard...")
    time.sleep(3)
    try:
        keyboard.press_and_release('enter')
    except Exception as e:
        print("Failed to dismiss pop-up with keyboard:", e)

# Function to disable mic and camera
def press_keys_to_disable_mic_camera():
    """Simulate key presses to disable mic and camera."""
    print("Simulating key presses to disable mic and camera...")
    time.sleep(3)  # Allow time for page to load
    keyboard.press_and_release('enter')  # Press Enter to dismiss pop-ups
    time.sleep(0.5)
    keyboard.press_and_release('tab')    # Navigate to the mic button
    time.sleep(0.5)
    keyboard.press_and_release('tab')    # Navigate to the camera button
    time.sleep(0.5)
    keyboard.press_and_release('enter')  # Press Enter to turn off the camera
    print("Mic and camera toggled off using keyboard simulation.")

def join_meeting(meeting_url, audio_file):
    """Join a meeting using the provided meeting URL."""
    global driver, stop_event
    driver = setup_chrome_driver()
    try:
        print(f"Navigating to: {meeting_url}")
        driver.get(meeting_url)
        dismiss_permission_popup_fallback()

        # Wait for "Continue on this browser" button and click
        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Continue on this browser")]'))
        )
        continue_button.click()
        print("Clicked 'Continue on this browser' button.")

        # Start recording audio
        start_audio_recording(audio_file)

        # Fill bot name
        name_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Type your name"]'))
        )
        name_field.clear()
        name_field.send_keys(bot_name)
        print("Bot name entered.")

        # Disable mic and camera (Try Selenium first, fallback to key presses if it fails)
        try:
            mic_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Mute microphone"]'))
            )
            mic_button.click()
            print("Microphone muted.")

            camera_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Turn camera off"]'))
            )
            camera_button.click()
            print("Camera turned off.")
        except Exception as e:
            print("Failed to mute mic or turn off camera using Selenium. Falling back to key presses.", e)
            

        # Click "Join now" button
        join_now_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Join now")]'))
        )
        join_now_button.click()
        print("Clicked 'Join now' button.")
        press_keys_to_disable_mic_camera()

        print("Monitoring meeting... Press Exit or Ctrl+C to leave.")
        while True:
            if stop_event and stop_event.is_set():
                print("Stop signal received. Exiting meeting loop.")
                break
            time.sleep(5)

    except Exception as e:
        print(f"Error during meeting: {e}")
    finally:
        exit_meeting()

def exit_meeting():
    """Cleanly exit the meeting and close resources."""
    global driver, stop_event, audio_thread
    try:
        # Attempt to leave the meeting if still in the call
        if driver:
            print("Attempting to leave the meeting...")
            try:
                # Locate and click "Leave meeting" button (Teams or Meet UI)
                leave_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Leave")]'))
                )
                leave_button.click()
                print("Leave meeting button clicked.")
                time.sleep(3)  # Allow time for meeting exit to complete
            except Exception as e:
                print("Could not locate 'Leave' button:", e)

            # Quit the browser
            print("Closing the browser...")
            driver.quit()
            driver = None

        # Stop audio recording-
        if stop_event:
            print("Stopping audio recording...")
            stop_event.set()

        # Wait for the audio recording thread to terminate
        if audio_thread:
            audio_thread.join()
            print("Audio recording thread stopped.")

        print("Meeting bot has exited the meeting.")
    except Exception as e:
        print(f"Error while exiting meeting: {e}")
