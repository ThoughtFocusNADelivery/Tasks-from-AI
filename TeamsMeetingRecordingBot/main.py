import tkinter as tk
from tkinter import messagebox
from meeting_bot import join_meeting, exit_meeting
import threading
import signal
import sys

# Audio file path for recording
audio_file = "meeting_audio.wav"

# Global variables
threads = []
stop_event = threading.Event()  # Stop event to signal threads to exit

# --- Meeting Functions ---
def start_bot():
    """Start the bot to join the meeting."""
    meeting_link = link_entry.get()
    if not meeting_link:
        messagebox.showwarning("Input Error", "Please paste a meeting link.")
        return

    if "teams.microsoft.com" in meeting_link or "meet.google.com" in meeting_link:
        messagebox.showinfo("Meeting Bot", "Joining the meeting...")
        thread = threading.Thread(target=join_meeting_thread, args=(meeting_link,))
        thread.start()
        threads.append(thread)
    else:
        messagebox.showerror("Invalid Link", "Please enter a valid Teams or Google Meet link.")

def join_meeting_thread(meeting_link):
    """Thread wrapper for joining a meeting."""
    global stop_event
    stop_event.clear()  # Clear any existing stop signal
    join_meeting(meeting_link, audio_file, stop_event)

def stop_bot():
    """Exit the bot from the meeting."""
    messagebox.showinfo("Meeting Bot", "Exiting the meeting...")
    stop_event.set()  # Signal threads to stop
    threading.Thread(target=exit_meeting, args= (audio_file,)).start()

def refresh_input():
    """Clear the input field."""
    link_entry.delete(0, tk.END)

# --- Page Functions ---
def show_home():
    """Display the Home Page."""
    clear_frame()
    tk.Label(content_frame, text="Welcome to Meeting Bot", font=("Helvetica", 24, "bold"), bg="#e6f7ff").place(relx=0.5, rely=0.2, anchor="center")
    tk.Label(content_frame, text="Paste Meeting Link (Teams or Google Meet):", font=("Arial", 14), bg="#e6f7ff").place(relx=0.5, rely=0.4, anchor="center")

    global link_entry
    link_entry = tk.Entry(content_frame, width=50, font=("Arial", 12))
    link_entry.place(relx=0.5, rely=0.45, anchor="center")

    # Buttons for Join, Exit, and Refresh
    button_frame = tk.Frame(content_frame, bg="#e6f7ff")
    button_frame.place(relx=0.5, rely=0.55, anchor="center")

    tk.Button(button_frame, text="Join Meeting", font=("Arial", 12), bg="#28a745", fg="white", 
              command=start_bot).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Exit Meeting", font=("Arial", 12), bg="#dc3545", fg="white", 
              command=stop_bot).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Refresh", font=("Arial", 12), bg="#ffc107", fg="black", 
              command=refresh_input).pack(side=tk.LEFT, padx=10)

def show_contact_us():
    """Display the Contact Us Page."""
    clear_frame()
    tk.Label(content_frame, text="Contact Us", font=("Helvetica", 24, "bold"), bg="#e6f7ff").place(relx=0.5, rely=0.2, anchor="center")
    tk.Label(content_frame, text="For support, contact us at:", font=("Arial", 14), bg="#e6f7ff").place(relx=0.5, rely=0.4, anchor="center")
    tk.Label(content_frame, text="Email: support@meetingbot.com", font=("Arial", 12), bg="#e6f7ff").place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(content_frame, text="Phone: +1-800-123-4567", font=("Arial", 12), bg="#e6f7ff").place(relx=0.5, rely=0.55, anchor="center")

def clear_frame():
    """Clear all widgets in the content frame."""
    for widget in content_frame.winfo_children():
        widget.destroy()

def handle_exit_signal(signum, frame):
    """Handle Ctrl+C and cleanly exit the program."""
    print("\nCtrl+C detected. Exiting application...")
    stop_event.set()  # Signal threads to stop
    for thread in threads:
        if thread.is_alive():
            print("Waiting for thread to complete...")
            thread.join(timeout=5)  # Timeout to prevent hanging
    sys.exit(0)

# --- Main Application ---
app = tk.Tk()
app.title("Meeting Bot UI")
app.geometry("800x600")
app.configure(bg="#eaeaea")

# Navigation Bar
nav_frame = tk.Frame(app, bg="#004080")
nav_frame.pack(fill=tk.X)

tk.Button(nav_frame, text="Home", font=("Arial", 12), bg="#004080", fg="white", command=show_home).pack(side=tk.LEFT, padx=10, pady=10)
tk.Button(nav_frame, text="Contact Us", font=("Arial", 12), bg="#004080", fg="white", command=show_contact_us).pack(side=tk.LEFT, padx=10, pady=10)

# Content Frame
content_frame = tk.Frame(app, bg="#e6f7ff")
content_frame.pack(fill=tk.BOTH, expand=True)

# Initialize Home Page
show_home()

# Handle Ctrl+C
signal.signal(signal.SIGINT, handle_exit_signal)

# Run the Application
try:
    app.mainloop()
except KeyboardInterrupt:
    handle_exit_signal(None, None)
