import streamlit as st
import PyPDF2
import spacy
from google.cloud import speech_v1p1beta1 as speech
import pyttsx3
import pyaudio
import wave
import urllib.parse

# Assuming pdf_path is obtained from a URL-like source
pdf_path = 'file:///C:/Users/Admin/Downloads/25_Python_Important_Interview_Questions.pdf'

# Extract the local file path
local_path = urllib.parse.unquote(urllib.parse.urlparse(pdf_path).path)

# Now you can use local_path in your code


# Initialize spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize Text-to-Speech
engine = pyttsx3.init()

# PDF Parsing
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

# Question Generation
def generate_questions(text):
    doc = nlp(text)
    questions = []
    for sent in doc.sents:
        questions.append({"question": sent.text, "answer": ""})  # You might need a more sophisticated method for generating questions
    return questions

# Speech Recognition using Google Cloud Speech-to-Text API
def recognize_speech(audio_file):
    client = speech.SpeechClient()
    with open(audio_file, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript

# Text-to-Speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Record audio and save it to file
def record_audio(file_path, duration=5, channels=1, rate=44100, chunk=1024, format=pyaudio.paInt16, input_device_index=None):
    audio = pyaudio.PyAudio()
    device_count = audio.get_device_count()
    if input_device_index is None:
        for i in range(device_count):
            if audio.get_device_info_by_index(i)['maxInputChannels'] > 0:
                input_device_index = i
                break
        if input_device_index is None:
            raise ValueError("No input device found")
    stream = audio.open(format=format, channels=channels,
                        rate=rate, input=True, input_device_index=input_device_index,
                        frames_per_buffer=chunk)
    st.write("Recording...")
    frames = []
    for i in range(int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    st.write("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# Main Program
def main():
    # Streamlit UI
    st.title("Interview Preparation App")
    pdf_path = st.text_input("Please provide the path to the PDF file:")
    if st.button("Start Interview"):
        if pdf_path:
            pdf_text = extract_text_from_pdf(pdf_path)
            questions = generate_questions(pdf_text)
            for question in questions:
                st.write("Question: ", question["question"])
                st.write("Please answer after the beep.")
                record_audio("audio.wav")
                user_answer = recognize_speech("audio.wav")
                question["answer"] = user_answer
                st.write("Your answer was: ", user_answer)

if __name__ == "__main__":
    main()