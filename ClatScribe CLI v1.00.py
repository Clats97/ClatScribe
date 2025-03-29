print("\033[31m" + r"""
██████╗██╗      █████╗ ████████╗███████╗ ██████╗██████╗ ██╗██████╗ ███████╗                      
██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝██╔════╝██╔══██╗██║██╔══██╗██╔════╝                      
██║     ██║     ███████║   ██║   ███████╗██║     ██████╔╝██║██████╔╝█████╗                        
██║     ██║     ██╔══██║   ██║   ╚════██║██║     ██╔══██╗██║██╔══██╗██╔══╝                        
╚██████╗███████╗██║  ██║   ██║   ███████║╚██████╗██║  ██║██║██████╔╝███████╗                      
 ╚═════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝                      
""" + "\033[0m")
print("\033[34mSPEECH TO TEXT & TRANSCRIPTION TOOL\033[0m", end=" ")
print("\033[31mVersion 1.00\033[0m")
print("By Joshua M Clatney - Ethical Pentesting Enthusiast")

import os
import threading
import tempfile
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf
import openai

API_KEY = "INSERT API KEY HERE"
openai.api_key = API_KEY

SAMPLERATE = 16000       
CHUNK_DURATION = 2         
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

def transcription_loop(stop_event, transcript_log):
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
            print(f"[{timestamp}] {transcript}", flush=True)
            transcript_log.append(f"[{timestamp}] {transcript}")
        else:
            stop_event.wait(0.1)

def main():
    # Wait for the user to press Enter to start transcription
    input("Press Enter to start transcription...")
    
    transcript_log = []
    stop_event = threading.Event()
    transcription_thread = threading.Thread(target=transcription_loop, args=(stop_event, transcript_log))
    transcription_thread.start()
    with sd.InputStream(samplerate=SAMPLERATE, channels=1, callback=audio_callback):
        print("Converting Speech To Text. Press Enter to stop...")
        input()
    stop_event.set()
    transcription_thread.join()
    
    # Ask if the user wants to save the log file before saving
    save_choice = input("Do you want to save the transcription log to a file? (y/n): ")
    if save_choice.lower().startswith("y"):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        log_filename = os.path.join(script_dir, "transcription_log.txt")
        try:
            with open(log_filename, "w", encoding="utf-8") as f:
                for entry in transcript_log:
                    f.write(entry + "\n")
            print(f"Transcription log saved to {log_filename}")
        except Exception as e:
            print("An error occurred while saving the transcription log:")
            print(e)
    else:
        print("Transcription log not saved.")

if __name__ == "__main__":
    main()