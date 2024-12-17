import tkinter as tk
from tkinter import messagebox, ttk
import datetime

# Global variable to store meeting summaries
meeting_summaries = []

# --- Bot and Meeting Functions ---
def join_meeting():
    meeting_link = link_entry.get()
    if not meeting_link:
        messagebox.showwarning("Input Error", "Please paste a meeting link.")
        return

    if "teams.microsoft.com" in meeting_link:
        platform = "Microsoft Teams"
    elif "meet.google.com" in meeting_link:
        platform = "Google Meet"
    else:
        messagebox.showerror("Invalid Link", "Please enter a valid Google Meet or Microsoft Teams link.")
        return

    messagebox.showinfo("Meeting Bot", f"The bot is joining the {platform} meeting:\n{meeting_link}")
    bot_exit_summary(platform, meeting_link)

def bot_exit_summary(platform, meeting_link):
    summary = {
        "Platform": platform,
        "Link": meeting_link,
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Summary": "The meeting discussed tasks, subtasks, and follow-up actions. Key participants shared updates and future steps were outlined."
    }
    meeting_summaries.append(summary)
    messagebox.showinfo("Meeting Bot", "The bot has exited the meeting and generated a summary!")

def exit_bot():
    messagebox.showinfo("Meeting Bot", "The bot has exited successfully!")

# --- Navigation and Pages ---
def show_summary_report():
    clear_frame()
    draw_gradient_background("#ffffff", "#e6f7ff")
    title_label = tk.Label(content_frame, text="Summary Report", font=("Helvetica", 20, "bold"), bg="#e6f7ff", fg="#003366")
    title_label.place(relx=0.5, rely=0.3, anchor="center")

    if not meeting_summaries:
        tk.Label(content_frame, text="No summaries available yet.", font=("Arial", 12), bg="#e6f7ff", fg="#555").place(relx=0.5, rely=0.5, anchor="center")
    else:
        report_frame = tk.Frame(content_frame, bg="#e6f7ff")
        report_frame.place(relx=0.5, rely=0.5, anchor="center")
        for i, summary in enumerate(meeting_summaries, start=1):
            report_text = f"Meeting {i} ({summary['Platform']}):\nDate: {summary['Date']}\nSummary: {summary['Summary']}\n"
            tk.Label(report_frame, text=report_text, font=("Arial", 12), bg="#e6f7ff", fg="#333", justify="left", wraplength=700).pack(pady=5)

def show_contact_us():
    clear_frame()
    draw_gradient_background("#ffffff", "#ccf2f4")
    title_label = tk.Label(content_frame, text="Contact Us", font=("Helvetica", 20, "bold"), bg="#ccf2f4", fg="#006064")
    title_label.place(relx=0.5, rely=0.3, anchor="center")

    contact_info = """
Email: support@meetingbot.com
Phone: +123-456-7890
Website: www.meetingbot.com
"""
    tk.Label(content_frame, text=contact_info, font=("Arial", 14), bg="#ccf2f4", fg="#004d40", justify="center").place(relx=0.5, rely=0.5, anchor="center")

def show_home():
    clear_frame()
    draw_gradient_background("#ffffff", "#f2f2f2")
    title_label = tk.Label(content_frame, text="", font=("Helvetica", 24, "bold"), bg="#f2f2f2", fg="#003366")
    title_label.place(relx=0.5, rely=0.25, anchor="center")
    animate_text(title_label, "Welcome to Meeting Bot")

    tk.Label(content_frame, text="Paste Meeting Link (Google Meet or Microsoft Teams):", font=("Arial", 14), bg="#f2f2f2").place(relx=0.5, rely=0.4, anchor="center")
    global link_entry
    link_entry = ttk.Entry(content_frame, width=50, font=("Arial", 12))
    link_entry.place(relx=0.5, rely=0.45, anchor="center")

    button_frame = tk.Frame(content_frame, bg="#f2f2f2")
    button_frame.place(relx=0.5, rely=0.55, anchor="center")
    ttk.Button(button_frame, text="Join Meeting", command=join_meeting, style="Accent.TButton").pack(side=tk.LEFT, padx=15)
    ttk.Button(button_frame, text="Exit Bot", command=exit_bot, style="Exit.TButton").pack(side=tk.LEFT, padx=15)

# --- Utility Functions ---
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()

def draw_gradient_background(color1, color2):
    canvas = tk.Canvas(content_frame, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    width = content_frame.winfo_width()
    height = content_frame.winfo_height()

    for i in range(height):
        ratio = i / height
        color = gradient_color(color1, color2, ratio)
        canvas.create_line(0, i, width, i, fill=color)
    canvas.lower("all")

def gradient_color(start, end, ratio):
    r1, g1, b1 = int(start[1:3], 16), int(start[3:5], 16), int(start[5:7], 16)
    r2, g2, b2 = int(end[1:3], 16), int(end[3:5], 16), int(end[5:7], 16)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"

def animate_text(label, text, delay=50, index=0):
    if index <= len(text):
        label.config(text=text[:index])
        label.after(delay, animate_text, label, text, delay, index+1)

# --- Main Application ---
app = tk.Tk()
app.title("Meeting Bot UI")
app.geometry("900x600")
app.configure(bg="white")

# Modern Styles
style = ttk.Style()
style.theme_use("clam")
style.configure("Accent.TButton", font=("Arial", 12), padding=10, background="#28a745", foreground="white")
style.configure("Exit.TButton", font=("Arial", 12), padding=10, background="#dc3545", foreground="white")

# Navigation Bar
nav_frame = tk.Frame(app, bg="#004080")
nav_frame.pack(fill=tk.X)

ttk.Button(nav_frame, text="Home", command=show_home).pack(side=tk.LEFT, padx=20, pady=5)
ttk.Button(nav_frame, text="Summary Report", command=show_summary_report).pack(side=tk.LEFT, padx=20, pady=5)
ttk.Button(nav_frame, text="Contact Us", command=show_contact_us).pack(side=tk.LEFT, padx=20, pady=5)

# Content Frame
content_frame = tk.Frame(app, bg="#f2f2f2")
content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Initialize Home Page
show_home()

# Run Application
app.mainloop()