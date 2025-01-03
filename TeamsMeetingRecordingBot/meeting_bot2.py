from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import threading
import keyboard
import time
import os

# Load environment variables
load_dotenv()
email = os.getenv("MEETING_EMAIL")
password = os.getenv("MEETING_PASSWORD")
bot_name = "MeetingBot"  # Set the bot name here

driver = None
ffmpeg_process = None
stop_event = threading.Event()  # Event to signal threads to stop

def list_audio_devices():
    """List all audio devices and return VB-Cable device index."""
    p = pyaudio.PyAudio()
    print("Available audio devices:")
    vb_cable_index = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        print(f"Device {i}: {device_info['name']}")
        if "Cable Output (VB-Audio Virtual Cable)" in device_info["name"]:
            vb_cable_index = i
    p.terminate()
    if vb_cable_index is None:
        print("VB-Cable device not found! Ensure VB-Cable is properly installed.")
    return vb_cable_index

def start_audio_recording(audio_file, device_index):
    """Start recording system audio using PyAudio from VB-Cable."""
    print("Starting audio recording with PyAudio...")
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024

    p = pyaudio.PyAudio()

    try:
        # Open the VB-Cable device for recording
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)

        frames = []
        while not stop_event.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save recorded audio to a file
        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        print(f"Audio recording saved to {audio_file}.")
    except Exception as e:
        print(f"Error during recording: {e}")

# Setup Chrome driver with options
def setup_chrome_driver():
    """Set up Chrome WebDriver with options."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")

    chrome_prefs = {
        "profile.default_content_setting_values.media_stream_camera": 2,  # Block camera
        "profile.default_content_setting_values.media_stream_mic": 2,     # Block mic
        "profile.default_content_setting_values.notifications": 2,        # Block notifications
    }
    options.add_experimental_option("prefs", chrome_prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Function to dismiss permission pop-ups using keyboard
def dismiss_permission_popup_fallback():
    print("Attempting to dismiss the pop-up using keyboard...")
    time.sleep(3)
    try:
        keyboard.press_and_release('enter')
    except Exception as e:
        print("Failed to dismiss pop-up with keyboard:", e)

# Function to disable mic and camera
def press_keys_to_disable_mic_camera():
    print("Simulating key presses to disable mic and camera...")
    time.sleep(3)
    keyboard.press_and_release('enter')  # Press Enter to dismiss pop-ups
    time.sleep(0.5)
    keyboard.press_and_release('tab')    # Navigate to the mic button
    time.sleep(0.5)
    keyboard.press_and_release('tab')    # Navigate to the camera button
    time.sleep(0.5)
    keyboard.press_and_release('enter')  # Press Enter to turn off the camera
    print("Mic and camera toggled off using keyboard simulation.")

# Handle audio/video pop-up
def handle_audio_video_popup():
    try:
        popup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Continue without audio or video")]'))
        )
        popup_button.click()
        print("Clicked 'Continue without audio or video' button.")
    except Exception as e:
        print("Failed to handle the audio/video pop-up:", e)

# Function to join a meeting
def join_meeting(meeting_url, audio_file, stop_event):
    global driver
    driver = setup_chrome_driver()
    try:
        print(f"Navigating to: {meeting_url}")
        driver.get(meeting_url)

        time.sleep(10)
        dismiss_permission_popup_fallback()

        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Continue on this browser")]'))
        )
        continue_button.click()
        print("Clicked 'Continue on this browser' button.")

        time.sleep(10)
        handle_audio_video_popup()
          
        name_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Type your name"]'))
        )
        name_field.clear()
        name_field.send_keys(bot_name)
        print("Bot name entered.")
          
        time.sleep(10)

        press_keys_to_disable_mic_camera()
        join_now_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Join now")]'))
        )
        join_now_button.click()
        print("Clicked 'Join now' button.")

        start_audio_recording(audio_file)

        print("Monitoring meeting... Waiting for stop signal.")
        while not stop_event.is_set():
            time.sleep(5)

    except Exception as e:
        print(f"Error during meeting: {e}")
    finally:
        exit_meeting(audio_file)

# Function to exit the meeting
def exit_meeting(audio_file):
    global driver
    try:
        if driver:
            print("Attempting to leave the meeting...")
            try:
                leave_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Leave")]'))
                )
                leave_button.click()
                print("Leave meeting button clicked.")
                time.sleep(3)
            except Exception as e:
                print("Could not locate 'Leave' button:", e)

            print("Closing the browser...")
            driver.quit()

        stop_audio_recording(audio_file)
        print("Meeting bot has exited the meeting.")
    except Exception as e:
        print(f"Error while exiting meeting: {e}")
