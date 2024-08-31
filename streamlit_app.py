import streamlit as st
from openai import OpenAI
import numpy as np
import base64
from io import BytesIO

# Function to convert audio data to WAV format
def audio_bytes_to_wav(audio_bytes):
    audio_data = base64.b64decode(audio_bytes)
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    return audio_data

# Show title and description.
st.title("💬 Spanish Practice Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses in Spanish. "
    "You can practice your Spanish through text or voice. "
    "Please provide your OpenAI API key to use this app."
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # JavaScript for recording audio
    st.markdown("""
    <script>
    let mediaRecorder;
    let audioChunks = [];

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
        });
    }

    function stopRecording() {
        return new Promise(resolve => {
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks);
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64audio = reader.result.split(',')[1]; // Get base64 string
                    resolve(base64audio);
                }
                reader.readAsDataURL(audioBlob);
            };
            mediaRecorder.stop();
        });
    }

    async function record() {
        startRecording();
        await new Promise(resolve => setTimeout(resolve, 3000)); // Record for 3 seconds
        const audioBase64 = await stopRecording();
        fetch(`/audio?audio=${audioBase64}`);
    }
    </script>
    """, unsafe_allow_html=True)

    # Button to start recording
    if st.button("Record Audio"):
        st.markdown('<script>record();</script>', unsafe_allow_html=True)

    # Handle audio data received from JavaScript
    if st.experimental_get_query_params().get('audio'):
        audio_data = st.experimental_get_query_params()['audio'][0]
        prompt = audio_bytes_to_wav(audio_data)

        # Append user input to chat history
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )

            # Display the assistant's response
            with st.chat_message("assistant"):
                st.markdown(response['choices'][0]['message']['content'])
            st.session_state.messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})

    # Create a chat input field for typing messages
    if prompt := st.chat_input("Type your message in Spanish"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )

        # Display the assistant's response
        with st.chat_message("assistant"):
            st.markdown(response['choices'][0]['message']['content'])
        st.session_state.messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        st.session_state.messages.append({"role": "assistant", "content": response})
