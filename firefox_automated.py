from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import wave
import pyaudio
import time


class MeetingBot:
    def __init__(self, meeting_url, output_file):
        self.meeting_url = meeting_url
        self.output_file = output_file
        self.recording = False
        self.setup_driver()

    def setup_driver(self):
        """Set up the Firefox WebDriver with options."""
        firefox_options = Options()
        # Uncomment the next line for headless mode in cloud environments
        # firefox_options.add_argument("--headless")
        firefox_options.set_preference("dom.webnotifications.enabled", False)  # Disable notifications
        firefox_options.set_preference("permissions.default.microphone", 2)    # Block microphone access
        firefox_options.set_preference("permissions.default.camera", 2)        # Block camera access
        
        # Use selenium-manager to dynamically install and manage GeckoDriver and Firefox
        self.driver = webdriver.Firefox(
            service=Service(),  # No explicit driver path needed
            options=firefox_options
        )

    def record_audio(self):
        """Record audio from the system's default output device."""
        self.recording = True
        chunk = 1024  # Record in chunks of 1024 samples
        format = pyaudio.paInt16  # 16-bit resolution
        channels = 1  # Mono
        rate = 44100  # 44.1 kHz sampling rate

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

        print("Recording audio...")
        frames = []

        while self.recording:
            data = stream.read(chunk)
            frames.append(data)

        print("Stopping audio recording...")
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(self.output_file, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))

        print(f"Audio saved to {self.output_file}")

    def join_meeting(self):
        """Join the meeting and start audio recording."""
        try:
            print(f"Navigating to {self.meeting_url}")
            self.driver.get(self.meeting_url)
            time.sleep(10)

            # Click on the "Join meeting from this browser" button
            join_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Join meeting from this browser"]'))
            )
            join_button.click()
            time.sleep(15)

            # Enter bot name
            name_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Type your name"]'))
            )
            name_field.clear()
            name_field.send_keys("MeetingBot")
            print("Entered bot name.")

            # Click on the "Join now" button
            join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Join now")]'))
            )
            join_button.click()
            print("Clicked on 'Join now' button.")

            # Wait to be admitted
            print("Waiting to be admitted...")
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "meeting-content")]'))
            )
            print("Admitted to the meeting.")

            # Start audio recording in a separate thread
            audio_thread = threading.Thread(target=self.record_audio)
            audio_thread.start()

            print("Recording started. Monitoring meeting...")
            self.monitor_meeting(audio_thread)

        except Exception as e:
            print(f"Failed to join the meeting: {e}")
        finally:
            self.driver.quit()

    def monitor_meeting(self, audio_thread):
        """Monitor meeting and stop recording when participants are less than 2."""
        try:
            while True:
                time.sleep(10)  # Check every 10 seconds
                # try:
                #     participant_count_element = self.driver.find_element(
                #         By.XPATH, '//*[contains(@class, "participant-count")]'
                #     )
                #     participant_count = int(participant_count_element.text)
                #     print(f"Participants in the meeting (including bot): {participant_count}")

                #     if participant_count < 2:
                #         print("Less than 2 participants (excluding bot). Ending meeting.")
                #         break
                # except Exception as e:
                #     print(f"Error checking participant count: {e}")
        finally:
            self.recording = False
            audio_thread.join()
            print("Recording stopped and bot has exited the meeting.")


if __name__ == "__main__":
    meeting_url = "https://teams.microsoft.com/l/meetup-join/19%3ameeting_NTk5OGE3MzItZTVhYi00OTVhLTg2MjktOWZlOTc5MjcyMGU5%40thread.v2/0?context=%7b%22Tid%22%3a%22ce235d14-4b96-4b29-888d-073a6bd1ab58%22%2c%22Oid%22%3a%2215b177f8-eb1c-4faf-8f39-98c6091a87ff%22%7d"
    temp_file = r"D:\BOT\temp_recording.wav"
    bot = MeetingBot(meeting_url, temp_file)
    bot.join_meeting()
