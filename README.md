# ClatScribe
ClatScribe is a speech-to-text tool that captures real-time audio, transcribes 3-second chunks via OpenAI API, timestamps and logs the text. The 3 second audio files are deleted after the newest file is written, so it does not take up lots of space. It has a CLI and a GUI. The outputs are optimized for transcribing audio from 1 person at a time, with no requirement for fast transcription. Because of the way the OpenAI transcribing models work, there will be a lag. If you'd like a tool that is quicker and outputs word per word instead of in chunks, check out ClatScribe 2.0 at github.com/clats97/clatscribe2.0 which uses the Google Transcription API.

# Speech-to-Text & Transcription Tool (Version 1.00)

CLI: ![Screenshot 2025-03-28 211432](https://github.com/user-attachments/assets/99cdff08-ceef-4e71-8113-9e0b2faff776)

GUI: ![Screenshot 2025-03-28 211141](https://github.com/user-attachments/assets/9b10157b-e080-46ae-9c9d-961a81864a52)


**By Joshua M Clatney - Ethical Pentesting Enthusiast**

![ClatScribe](https://github.com/user-attachments/assets/47c8bc54-cae2-44d9-bfb4-f063773a4d42)

---

## Overview

This command-line & graphical user interface speech-to-text transcription tool captures audio from your microphone, processes audio in fixed-duration chunks, and transcribes the speech using OpenAI’s transcription API (gpt-4o-transcribe, or whispher-1). It features real-time audio capture, chunked transcription, timestamped logging, and an interactive interface that lets you start/stop recording and save the transcription log.

---

## Features

- **Real-time Audio Capture:** Uses `sounddevice` to record audio from your microphone.
- **Audio Buffering & Chunking:** Buffers the incoming audio and processes it in 3-second chunks.
- **Speech Transcription:** Uses OpenAI's transcription API (`gpt-4o-transcribe` model, or whispher-1) to convert speech into text.
- **Timestamped Logging:** Each transcription is timestamped and printed, with the option to save the log to a file.
- **Colored CLI Interface:** Displays an ASCII art banner and colored text using ANSI escape codes.

---

## Modules Required

### Built-in Modules
- `os`
- `threading`
- `tempfile`
- `datetime`

### Third-party Modules
- **numpy** – for handling and processing audio data arrays  
  [NumPy Documentation](https://numpy.org/doc/stable/)
- **sounddevice** – for capturing real-time audio input  
  [SoundDevice Documentation](https://python-sounddevice.readthedocs.io/)
- **soundfile** – for writing audio data to temporary WAV files  
  [SoundFile Documentation](https://pysoundfile.readthedocs.io/)
- **openai** – for interfacing with OpenAI’s transcription API  
  [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/introduction)

---

## Installation

Ensure you have Python installed. Then install the required third-party modules using pip:

pip install numpy sounddevice soundfile openai==0.28 **YOU MUST USE 0.28 OR IT WILL NOT WORK**

---

## Usage

1. **Set Up the API Key:**  
   The OpenAI API key is hard-coded in the script. For better security, consider using an environment variable to store the API key.

2. **Run the Script:**  
   Execute the script via your terminal or download it directly from Github.

3. **Interactive Process:**
   - **Start Transcription:** Press **Enter** (in CLI version) or press **Start Transcribing** (in GUI version) to begin recording.
   - **Speak:** The script will capture your audio, process it in 3-second chunks, and display the transcribed text with a timestamp.
   - **Stop Transcription:** Press **Enter** again or press **Stop Transcribing** to stop recording.
   - **Save Log:** You will be prompted to save the transcription log to a file if desired.

---

## How It Works

1. **Banner Display:**  
   The script starts by printing an ANSI-colored ASCII art banner and tool details (title, version, and author).

2. **Audio Capture & Buffering:**  
   - Uses `sounddevice` with an audio callback (`audio_callback`) to capture real-time audio.
   - Audio data is stored in a global buffer (`audio_buffer`) with thread-safe access using a lock.

3. **Chunk Processing:**  
   - Audio is buffered until it reaches 3 seconds’ worth (as determined by the `CHUNK_SAMPLES` constant).
   - The buffered audio is then segmented into chunks for transcription.

4. **Transcription:**  
   - Each chunk is temporarily written to a WAV file.
   - The file is sent to OpenAI's transcription API, gpt-4o-transcribe or whisper-1.
   - The returned transcript is timestamped and printed/logged.

5. **Logging & Cleanup:**  
   - The transcript, along with its timestamp, is added to a log.
   - Users are prompted to save the log to a text file after transcription ends.
   - Temporary audio files are removed after transcription to avoid clutter.

---

## Security & Considerations

- **API Key Management:**  
  The API key is directly embedded in the script, which is a potential security risk. Consider retrieving it from an environment variable instead.

- **Buffer Management:**  
  The current implementation concatenates audio chunks in a simple buffer. In production, more robust handling may be needed to prevent data overlap or loss.

- **Thread Synchronization:**  
  While a lock is used for thread safety, real-time audio processing might benefit from additional error handling or buffering strategies to ensure smooth performance.
  
---

## License

This project is licensed under the Apache 2.0 License.
