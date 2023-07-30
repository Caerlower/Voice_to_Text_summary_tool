import tkinter as tk
from tkinter import ttk, filedialog
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from transformers import pipeline
import json
import subprocess
import os
import threading

FRAME_RATE = 16000
CHANNEL = 1

def voice_recognition(filename):
    model = Model(model_name="vosk-model-en-us-0.22")
    recog = KaldiRecognizer(model, FRAME_RATE)
    recog.SetWords(True)
      
    audio = AudioSegment.from_mp3(filename)
    audio = audio.set_channels(CHANNEL)
    audio = audio.set_frame_rate(FRAME_RATE)
    
    step = 45000
    transcript = ""
    
    for i in range(0, len(audio), step):
        print(f"Progress: {i/len(audio)}")
        segment = audio[i:i+step]
        recog.AcceptWaveform(segment.raw_data)
        result = recog.Result()
        text = json.loads(result)["text"]
        transcript += text
        
    cased = subprocess.check_output('/Users/gaurav.goyal/Desktop/Codes/projectvenv/bin/python vosk-recasepunc-en-0.22/recasepunc.py predict vosk-recasepunc-en-0.22/checkpoint', shell=True, text=True, input=transcript)
    return cased

def summarize_transcript(transcript):
    summary_maker = pipeline("summarization")
    spl_value = transcript.split(" ")
    trans = []
    for i in range(0, len(spl_value), 850):
        selection = " ".join(spl_value[i:(i+850)])
        trans.append(selection)
    summary = summary_maker(trans)
    summary_1 = "\n\n".join([d["summary_text"] for d in summary])
    return summary_1


def process_file(file_path):
    processing_dialog = tk.Toplevel(root)
    processing_dialog.title("Processing...")
    processing_dialog.geometry("200x100")
    processing_label = ttk.Label(processing_dialog, text="Processing... \n this might take a few min...", font=("Helvetica", 14))
    processing_label.pack(pady=20)
    processing_dialog.update()

    transcript = voice_recognition(file_path)
    summary = summarize_transcript(transcript)

    processing_dialog.destroy()  
    heading_label.config(text="Hello user, here is your summary for given audio file", foreground="black")

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, summary)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        
        thread = threading.Thread(target=process_file, args=(file_path,))
        thread.start()

root = tk.Tk()
root.title("Voice Recognition and Summarization")

root = tk.Tk()
root.title("Voice Recognition and Summarization")

window_width = 600
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Helvetica", 12), padding=5)
style.configure("TLabel", font=("Helvetica", 16, "bold"))
style.configure("TText", font=("Helvetica", 12))

browse_button = ttk.Button(root, text="Browse MP3 File", command=browse_file)
browse_button.pack(pady=10)

heading_label = ttk.Label(root, text="", foreground="blue", padding=10)
heading_label.pack()
heading_label.grid_remove() 
output_text = tk.Text(root, height=10, wrap=tk.WORD)
output_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop() 