
import streamlit as st
import os
import pyaudio
import wave
import openai
from gtts import gTTS
import pygame
import os
import uuid
import pygame
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Initialize Pygame for playing audio
pygame.init()
pygame.mixer.init()

# Set up OpenAI API key
openai.api_key = 'sk-proj-CKbUfZXFyPGBNaFijKKkT3BlbkFJ80NY7Oq0VVT6kzfwbhs8'  # Ensure to securely manage your API key

# Function to record audio
def record_audio(output_file):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = 5
    p = pyaudio.PyAudio()

    st.write("🎤 Recording...")
    stream = p.open(format=sample_format, channels=channels, rate=fs,
                    input=True, frames_per_buffer=chunk)
    frames = []

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    st.write("Finished recording.")

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe speech to text using OpenAI
def speech_to_text(audio_file):
    response = openai.Audio.transcribe(
        model="whisper-1",
        file=open(audio_file, "rb")
    )
    return response['text']

# Function to generate response using GPT based on user input
def chat_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a chatty compassionate friend assisting people who are walking in dark alleys.Reassure people. limit your responses to two sentences and engage in conversation. Ask questions where ever needed"},
                  {"role": "user", "content": text}]
    )
    return response.choices[0].message['content']

# Function to convert text to speech
pygame.mixer.init()

# Set up Eleven Labs client with API key
ELEVENLABS_API_KEY = os.getenv("583eb8256754ed974ad2cff13a5214d7")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech(text, language='en'):
    # Generate a unique filename for each .mp3 file
    unique_id = uuid.uuid4().hex
    filename = f"output_{unique_id}.mp3"

    # Calling the Eleven Labs text_to_speech conversion API
    response = client.text_to_speech.convert(
        voice_id="ThT5KcBeYPX3keUQqHPh",  # Specific pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",  # Low latency model
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=0.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Stop the music if it is playing
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    # Write the audio to the file (overwrite existing file)
    with open(filename, 'wb') as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    # Load and play the audio file
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait for the music to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.delay(100)

def main():
    st.title("Alleymate here to assist you")

    conversation_started = st.session_state.get("conversation_started", False)

    if not conversation_started:
        st.write("Click the button to start the conversation.")
        if st.button("Start Conversation"):
            st.session_state.conversation_started = True
            st.session_state.counter = 0

    else:
        audio_file = f"your_audio_file_{st.session_state.counter}.wav"
        if st.button("🎤 Speak"):
            record_audio(audio_file)
            st.session_state.counter += 1

            # Transcribe recorded audio to text
            transcript = speech_to_text(audio_file)
            st.write("You:", transcript)

            # Generate response using GPT
            response_text = chat_with_gpt(transcript)
            st.write("Assistant:", response_text)

            # Convert response to speech and play
            text_to_speech(response_text)

if __name__ == "__main__":
    main()
