import os
import threading
import tempfile
from datetime import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
import openai
import tkinter as tk
from tkinter import scrolledtext, filedialog
import queue

API_KEY = "INSERT API KEY HERE"
openai.api_key = API_KEY

SAMPLERATE = 16000         
CHUNK_DURATION = 3       
CHUNK_SAMPLES = SAMPLERATE * CHUNK_DURATION

audio_buffer = []
buffer_lock = threading.Lock()

def audio_callback(indata, frames, time, status):
    if status:
        print("Recording status:", status)
    with buffer_lock:
        audio_buffer.append(indata.copy())

def transcribe_chunk(audio_chunk):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        temp_filename = tmpfile.name
    try:
        sf.write(temp_filename, audio_chunk, SAMPLERATE)
        with open(temp_filename, "rb") as audio_file:
            transcript_response = openai.Audio.transcribe("gpt-4o-transcribe", audio_file)
        transcript_text = transcript_response.get("text", "")
        return transcript_text
    except Exception as e:
        print("Transcription error:", e)
        return ""
    finally:
        try:
            os.remove(temp_filename)
        except Exception as e:
            print("Error cleaning up temp file:", e)

def transcription_loop(stop_event, transcript_queue):
    global audio_buffer
    while not stop_event.is_set():
        with buffer_lock:
            if audio_buffer:
                buffer_data = np.concatenate(audio_buffer, axis=0)
            else:
                buffer_data = np.empty((0, 1), dtype=np.float32)
            if buffer_data.shape[0] >= CHUNK_SAMPLES:
                chunk = buffer_data[:CHUNK_SAMPLES]
                leftover = buffer_data[CHUNK_SAMPLES:]
                audio_buffer = [leftover] if leftover.size > 0 else []
            else:
                chunk = None
        if chunk is not None:
            transcript = transcribe_chunk(chunk)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] {transcript}\n"
            transcript_queue.put(message)
        else:
            stop_event.wait(0.1)

class GUIApplication:
    def __init__(self, master):
        self.master = master
        master.title("ClatScribe Speech-To-Text & Transcription Tool v1.00")
        header_frame = tk.Frame(master)
        header_frame.pack(pady=10)
        
        ascii_art = r"""

                      ██████╗██╗      █████╗ ████████╗███████╗ ██████╗██████╗ ██╗██████╗ ███████╗                      
                      ██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝██╔════╝██╔══██╗██║██╔══██╗██╔════╝                      
                      ██║     ██║     ███████║   ██║   ███████╗██║     ██████╔╝██║██████╔╝█████╗                        
                      ██║     ██║     ██╔══██║   ██║   ╚════██║██║     ██╔══██╗██║██╔══██╗██╔══╝                        
                      ╚██████╗███████╗██║  ██║   ██║   ███████║╚██████╗██║  ██║██║██████╔╝███████╗                      
                       ╚═════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝                    
"""
        self.label_ascii = tk.Label(header_frame, text=ascii_art, fg="red", font=("Courier", 10), justify="center", anchor="center")
        self.label_ascii.pack()
        
        self.label_title = tk.Label(header_frame, text="SPEECH TO TEXT & TRANSCRIPTION TOOL", fg="blue", font=("Helvetica", 16, "bold"))
        self.label_title.pack()
        
        self.label_version = tk.Label(header_frame, text="GUI Version 1.00", fg="red", font=("Helvetica", 12))
        self.label_version.pack()
        
        self.label_by = tk.Label(header_frame, text="By Joshua M Clatney - Ethical Pentesting Enthusiast", fg="black", font=("Helvetica", 10))
        self.label_by.pack()

        self.text_log = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=20, font=("Helvetica", 10))
        self.text_log.pack(padx=10, pady=10)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)
        
        self.start_button = tk.Button(btn_frame, text="Start Transcribing", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(btn_frame, text="Stop Transcribing", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = tk.Button(btn_frame, text="Save Transcript", command=self.save_transcript, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.transcript_queue = queue.Queue()
        
        self.stop_event = None
        self.transcription_thread = None
        self.stream = None

        self.master.after(100, self.update_transcript)
    
    def start_recording(self):
        global audio_buffer
        with buffer_lock:
            audio_buffer = []
        self.stop_event = threading.Event()
        self.transcription_thread = threading.Thread(target=transcription_loop, args=(self.stop_event, self.transcript_queue), daemon=True)
        self.transcription_thread.start()
        self.stream = sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=audio_callback)
        self.stream.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.text_log.insert(tk.END, "Transcription started...\n")
        self.text_log.see(tk.END)
    
    def stop_recording(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.stop_event:
            self.stop_event.set()
        if self.transcription_thread:
            self.transcription_thread.join()
        self.text_log.insert(tk.END, "Transcription stopped.\n")
        self.text_log.see(tk.END)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
    
    def update_transcript(self):
        try:
            while True:
                message = self.transcript_queue.get_nowait()
                self.text_log.insert(tk.END, message)
                self.text_log.see(tk.END)
        except queue.Empty:
            pass
        self.master.after(100, self.update_transcript)
    
    def save_transcript(self):
        transcript = self.text_log.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                self.text_log.insert(tk.END, f"Transcript saved to {file_path}\n")
                self.text_log.see(tk.END)
            except Exception as e:
                self.text_log.insert(tk.END, f"Error saving transcript: {e}\n")
                self.text_log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApplication(root)
    root.mainloop()