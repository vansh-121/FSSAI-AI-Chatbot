from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from gtts import gTTS
import tempfile
import re

# Load environment variables
load_dotenv()

# Configure the Google API with the provided key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to get the Gemini response and aggregate streamed chunks
def get_gemini_response(question):
    # More detailed instructions to ensure responses cover FSSAI-related information
    restricted_prompt = (
        f"Respond to this question with information from the FSSAI (Food Safety and Standards Authority of India), "
        f"its website (https://fssai.gov.in), or related data sources. If the question is related to food safety, food standards, "
        f"licensing, regulations, or hygiene ratings in India, provide an FSSAI-based answer. "
        f"If the question is not related to any of these topics, respond with: 'This question is outside the scope of FSSAI.' "
        f"Here is the question: {question}"
    )
    response_chunks = chat.send_message(restricted_prompt, stream=True)
    full_response = "".join([chunk.text for chunk in response_chunks])
    return full_response

# Initialize Streamlit app
st.set_page_config(page_title="FSSAI AI Chatbot")

st.header("FSSAI AI Chatbot")

# Initialize session state for chat history and tracking the first question
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'first_question' not in st.session_state:
    st.session_state['first_question'] = True  # True means the first question has not been asked

# Function to generate a response with the introduction on the first query
def get_introduction_and_response(question):
    # Add instruction for structured response and FSSAI introduction
    intro_prompt = (
        f"First, introduce yourself as FSSAI's Virtual AI Assistant. "
        f"Then, respond to this question using only FSSAI-related information, its website (https://fssai.gov.in), "
        f"or other official data sources. If the question is related to food safety, standards, licensing, or "
        f"anything under FSSAI's domain, provide a relevant answer. If not, respond with: 'This question is outside the scope of FSSAI.' "
        f"Here is the question: {question}"
    )
    return get_gemini_response(intro_prompt)

def text_to_speech(text):
    """Converts text to speech and returns the path to the audio file."""
    # Show "Generating Audio..." message
    st.info("Generating Audio...")

    # Remove any markdown formatting (like bold **, italics *, etc.)
    clean_text = re.sub(r'[*_~`]', '', text)

    # Convert cleaned text to speech
    tts = gTTS(text=clean_text, lang='en')
    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    tts.save(temp_file_path)

    # Update the status to "Audio generated!"
    st.success("Audio generated!")

    return temp_file_path

# Input from user
input = st.text_input("Ask a question:", key="input")
submit = st.button("Submit")

# Process user input and generate response
if submit and input:
    # If it's the user's first question, include the introduction
    if st.session_state['first_question']:
        response = get_introduction_and_response(input)
        st.session_state['first_question'] = False  # Set to False so the introduction doesn't repeat
    else:
        # If not the first question, get a normal response
        response = get_gemini_response(input)

    # Add the user query and bot response to the chat history
    st.session_state['chat_history'].append(("You", input))
    st.session_state['chat_history'].append(("Bot", response))

    # Display the bot's response in a clean, structured layout
    st.subheader("Response")
    st.markdown(f"**Bot:** {response}")

    # Convert the response to speech and play the audio
    audio_file_path = text_to_speech(response)
    audio_file = open(audio_file_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

# Display the chat history
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    st.markdown(f"**{role}:** {text}")
