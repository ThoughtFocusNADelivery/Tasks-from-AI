from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import wave
import pyaudio
import pyautogui
import time
import os
import keyboard

# Load environment variables
load_dotenv()
email = os.getenv("MEETING_EMAIL")
password = os.getenv("MEETING_PASSWORD")
bot_name = "MeetingBot"  # Set the bot name here

# Function to start audio recording
def start_audio_recording(audio_file):
    """Start recording system audio and save it to a file."""
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

    return stop_event, audio_thread


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
        "profile.default_content_setting_values.media_stream_camera": 2,  # Block camera
        "profile.default_content_setting_values.media_stream_mic": 2,     # Block mic
        "profile.default_content_setting_values.notifications": 2,        # Block notifications
        "protocol_handler.excluded_schemes.ms-teams": True                # Block external protocol pop-ups
    }
    options.add_experimental_option("prefs", chrome_prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service("D:/chromedriver-win64/chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

# Function to handle native pop-up
def dismiss_permission_popup_fallback():
    """Fallback to handle pop-up using keyboard."""
    print("Attempting to dismiss the pop-up using keyboard...")
    time.sleep(3)  # Give time for pop-up to appear
    try:
        # Send 'Tab' and 'Enter' to focus on the 'Cancel' button
        keyboard.press_and_release('enter')
        time.sleep(0.5)
        keyboard.press_and_release('enter')
        print("Pop-up dismissed via keyboard automation.")
    except Exception as e:
        print("Failed to dismiss pop-up with keyboard:", e)
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
    keyboard.press_and_release('enter') # Press Enter to turn off the camera
    
    
    print("Mic and camera toggled off using keyboard simulation.")
# Main function to join the meeting
def join_meeting(meeting_url, audio_file):
    driver = setup_chrome_driver()
    stop_event, audio_thread = None, None
    try:
        print(f"Navigating to: {meeting_url}")
        driver.get(meeting_url)
        dismiss_permission_popup_fallback()
        # Wait for "Continue on this browser" button and click
        try:
            continue_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Continue on this browser")]'))
            )
            driver.execute_script("arguments[0].click();", continue_button)
            print("Clicked 'Continue on this browser' button.")
        except Exception as e:
            print("Failed to click 'Continue on this browser' button:", e)
            driver.save_screenshot("error_continue_browser.png")
            return
        
        # Start recording audio
        stop_event, audio_thread = start_audio_recording(audio_file)
        #press_keys_to_disable_mic_camera()
        # Fill bot name
        try:
            name_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Type your name"]'))
            )
            name_field.clear()
            name_field.send_keys(bot_name)
            print("Bot name entered.")
            time.sleep(1)
        except Exception as e:
            print("Failed to enter bot name:", e)
            driver.save_screenshot("error_name_field.png")
            return
        
        # Click "Join now" button
        try:
            join_now_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Join now")]'))
                
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", join_now_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", join_now_button)
            print("Clicked 'Join now' button.")
            press_keys_to_disable_mic_camera()
        except Exception as e:
            print("Failed to click 'Join now':", e)
            driver.save_screenshot("error_join_now.png")

        print("Monitoring meeting... Press Ctrl+C to exit.")
        while True:
            time.sleep(5)

    except KeyboardInterrupt:
        print("Exiting meeting...")
    finally:
        # Stop recording and clean up
        if stop_event:
            stop_event.set()
            print("Stop signal sent to audio recording thread.")
        if audio_thread:
            audio_thread.join()
            print("Audio recording thread joined.")
        driver.quit()
        print("Meeting ended, browser closed, and resources released.")




if __name__ == "__main__":
    meeting_url = "https://teams.microsoft.com/l/meetup-join/19%3ameeting_ZDFlY2NkYmQtYmIyOS00N2NlLTlhNzItMTVmMzU1NzI4YzBm%40thread.v2/0?context=%7b%22Tid%22%3a%22ce235d14-4b96-4b29-888d-073a6bd1ab58%22%2c%22Oid%22%3a%2215b177f8-eb1c-4faf-8f39-98c6091a87ff%22%7d"
    audio_file = r"D:\BOT\meeting_audio.wav"
    join_meeting(meeting_url, audio_file)
