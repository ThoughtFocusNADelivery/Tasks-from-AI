import tkinter as tk
from tkinter import messagebox

# --- Animation Function ---
def animate_text(label, text, delay=50, index=0):
    if index <= len(text):
        label.config(text=text[:index])
        label.after(delay, animate_text, label, text, delay, index + 1)

# --- Meeting Functions ---
def join_meeting():
    meeting_link = link_entry.get()
    if not meeting_link:
        messagebox.showwarning("Input Error", "Please paste a meeting link.")
        return

    if "teams.microsoft.com" in meeting_link or "meet.google.com" in meeting_link:
        messagebox.showinfo("Meeting Bot", f"The bot is attempting to join the meeting")
    else:
        messagebox.showerror("Invalid Link", "Please enter a valid Teams or Google Meet link.")

def exit_meeting():
    messagebox.showinfo("Meeting Bot", "The bot has exited the meeting.")

# --- Page Functions ---
def show_home():
    clear_frame()
    tk.Label(content_frame, text="Welcome to Meeting Bot", font=("Helvetica", 24, "bold"), bg="#e6f7ff", fg="#004080").place(relx=0.5, rely=0.2, anchor="center")
    tk.Label(content_frame, text="Paste Meeting Link (Teams or Google Meet):", font=("Arial", 14), bg="#e6f7ff", fg="#333").place(relx=0.5, rely=0.4, anchor="center")

    global link_entry
    link_entry = tk.Entry(content_frame, width=50, font=("Arial", 12))
    link_entry.place(relx=0.5, rely=0.45, anchor="center")

    # Use a Frame to contain buttons
    button_frame = tk.Frame(content_frame, bg="#e6f7ff")
    button_frame.place(relx=0.5, rely=0.55, anchor="center")

    # Buttons with spacing (pady)
    tk.Button(button_frame, text="Join Meeting", font=("Arial", 12, "bold"), bg="#28a745", fg="white", 
              command=join_meeting, relief="flat", bd=0, padx=10, pady=5).pack(side=tk.LEFT, padx=15)

    tk.Button(button_frame, text="Exit Meeting", font=("Arial", 12, "bold"), bg="#dc3545", fg="white", 
              command=exit_meeting, relief="flat", bd=0, padx=10, pady=5).pack(side=tk.LEFT, padx=15)

def show_summary_report():
    clear_frame()
    tk.Label(content_frame, text="Summary Report", font=("Helvetica", 24, "bold"), bg="#e6f7ff", fg="#004080").place(relx=0.5, rely=0.2, anchor="center")
    tk.Label(content_frame, text="Summary report content goes here...", font=("Arial", 14), bg="#e6f7ff", fg="#333").place(relx=0.5, rely=0.5, anchor="center")

def show_contact_us():
    clear_frame()
    tk.Label(content_frame, text="Contact Us", font=("Helvetica", 24, "bold"), bg="#e6f7ff", fg="#004080").place(relx=0.5, rely=0.2, anchor="center")
    contact_info = "Email: support@meetingbot.com\nPhone: +1234567890"
    tk.Label(content_frame, text=contact_info, font=("Arial", 14), bg="#e6f7ff", fg="#333", justify="center").place(relx=0.5, rely=0.5, anchor="center")

# --- Utility Functions ---
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()

# --- Main Application ---
app = tk.Tk()
app.title("Meeting Bot UI")
app.geometry("800x600")
app.configure(bg="#eaeaea")

# Navigation Bar
nav_frame = tk.Frame(app, bg="#004080")
nav_frame.pack(fill=tk.X)

tk.Button(nav_frame, text="Home", font=("Arial", 12, "bold"), bg="#004080", fg="white", command=show_home, relief="flat", padx=10).pack(side=tk.LEFT, pady=10)
tk.Button(nav_frame, text="Summary Report", font=("Arial", 12, "bold"), bg="#004080", fg="white", command=show_summary_report, relief="flat", padx=10).pack(side=tk.LEFT, pady=10)
tk.Button(nav_frame, text="Contact Us", font=("Arial", 12, "bold"), bg="#004080", fg="white", command=show_contact_us, relief="flat", padx=10).pack(side=tk.LEFT, pady=10)

# Content Frame
content_frame = tk.Frame(app, bg="#e6f7ff")  # Set light blue background
content_frame.pack(fill=tk.BOTH, expand=True)

# Initialize Home Page
show_home()

# Run the Application
app.mainloop()
