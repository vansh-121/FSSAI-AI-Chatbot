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
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# Function to get the Gemini response and aggregate streamed chunks
def get_gemini_response(question):
    # Comprehensive instructions to ensure full FSSAI-related coverage
    optimized_prompt = (
        f"Respond to this question by referencing the FSSAI (Food Safety and Standards Authority of India) website (https://fssai.gov.in) "
        f"or any other FSSAI-approved data sources. Treat all queries related to food safety, hygiene, regulations, food standards, "
        f"labeling, food inspections, food licensing, food businesses, and consumer safety in India as being within the FSSAI's scope, "
        f"even if the acronym 'FSSAI' is not mentioned. Provide detailed information or direct the user to relevant sections of the FSSAI website. "
        f"If no direct answer is available, give a general response about how FSSAI addresses such queries, and encourage the user to visit the website "
        f"for more information. Here is the question: {question}"
    )
    response_chunks = chat.send_message(optimized_prompt, stream=True)
    full_response = "".join([chunk.text for chunk in response_chunks])
    return full_response

def text_to_speech(text):
    """Converts text to speech and returns the path to the audio file."""
    # Show "Generating Audio..." message
    st.info("Generating Audio...")

    # Remove any markdown formatting (like bold **, italics *, etc.) and URLs
    clean_text = re.sub(r'[*_~`]', '', text)
    # Remove URLs using a regular expression
    clean_text = re.sub(r'http\S+|www\S+|https\S+', '', clean_text, flags=re.MULTILINE)

    # Convert cleaned text to speech
    tts = gTTS(text=clean_text, lang='en')
    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    tts.save(temp_file_path)

    # Update the status to "Audio generated!"
    st.success("Audio generated!")

    return temp_file_path


# Initialize Streamlit app
st.set_page_config(page_title="FSSAI AI Chatbot")

st.header("FSSAI AI Chatbot")


# Add the suggested questions section here


# Now, the input field for the user to ask their own question
input = st.text_input("Ask a question:", key="manual_input")
submit = st.button("Submit", key="submit_button")


st.subheader("Suggested Questions")
suggested_questions = [
    "What are the FSSAI regulations for food labeling?",
    "How can I apply for a food business license?",
    "What is the process for food inspection?",
    "What are the safety standards for packaged food?"
]


for idx, question in enumerate(suggested_questions): 
    if st.button(question, key=f"suggested_{idx}"):
        input = question  # Set the input to the clicked suggested question
        response = get_gemini_response(input)

        # Add the suggested question and bot response to the chat history
        st.session_state['chat_history'].append(("You", input))
        st.session_state['chat_history'].append(("Bot", response))

        # Display the response
        st.markdown(f"**Bot:** {response}")

        # Convert the response to speech and play the audio
        audio_file_path = text_to_speech(response)
        audio_file = open(audio_file_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')


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

