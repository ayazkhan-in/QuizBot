import streamlit as st
import os
import google.generativeai as genai 
import fitz


# API key
os.environ["GEMINI_API_KEY"] = "AIzaSyCGIfKLFbZq0KFXXnvkIpUhyqmHvu_XzME"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Chat session with no initial history
chat_session = model.start_chat(history=[])

def chat_with_ai(message):
    response = chat_session.send_message(message)
    return response.text

st.title("AI Quiz Generator")

if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

if 'current_question' not in st.session_state:
    st.session_state['current_question'] = ""

if 'user_answer' not in st.session_state:
    st.session_state['user_answer'] = ""

difficulty = st.selectbox(
    'Choose Difficulty:',
    ['Really Easy', 'Easy', 'Medium', 'Difficult', 'Really Difficult']
)

text = None
topic = None
summarised_text = None

# Toggle between PDF upload or Topic input
input_method = st.radio(
    "Select Input Method",
    options=["Upload PDF", "Enter Topic Manually"]
)

# Function to convert PDF to text
def pdf_to_text(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()  # Extract text from each page
    
    return text

if input_method == "Upload PDF":
    # PDF Upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Display the file name
        st.write("You uploaded:", uploaded_file.name)
        
        # Convert PDF to text
        text = pdf_to_text(uploaded_file)

    topic = ""  # Clear topic when PDF is selected

elif input_method == "Enter Topic Manually":
    # Topic Input
    st.write("### Enter Quiz Topic")
    topic = st.text_input("")

context = f'''You are an AI teacher. Your task is to generate MCQ questions based on the given topic or the pdf summary provided to you.
               Generate only one question at a time in {difficulty} mode.
               Format:
               Question. 
               A) Option 1
               B) Option 2
               C) Option 3
               D) Option 4
               Ensure each option is on a new line.
            '''

#summarise pdf
if text:
    summarised_text = chat_with_ai(f"Summarise the text.\nText: {text}")

if st.button("Generate Question"):
    if topic or summarised_text:
        st.session_state['conversation_history'].append(f"Topic: {topic}")
        ai_response = chat_with_ai(f'{context}\nTopic: {topic} {summarised_text}')
        st.session_state['current_question'] = ai_response
        st.session_state['conversation_history'].append(f"AI: {ai_response}")
        st.write(f"**AI:** {ai_response}")

# Next Question
if st.button("Next Question"):
    if topic or summarised_text:
        ai_response = chat_with_ai(f'{context}\nTopic: {topic} {summarised_text}')
        st.session_state['current_question'] = ai_response
        st.session_state['user_answer'] = ""  # Reset user answer input
        st.session_state['conversation_history'].append(f"AI: {ai_response}")
        st.write(f"**AI:** {ai_response}")

# Answer Input ans Check Answer Button
if st.session_state['current_question']:
    st.session_state['user_answer'] = st.text_input("Enter your answer (A, B, C, or D):")

if st.button("Check Answer"):
    if st.session_state['current_question'] and st.session_state['user_answer']:
        check_answer = chat_with_ai(
            f"Check if the user's answer is correct.\nTopic: {topic} {summarised_text} \nQuestion: {st.session_state['current_question']}\nUser's Answer: {st.session_state['user_answer']}"
        )
        st.write(f"**AI:** {check_answer}")
        st.session_state['conversation_history'].append(f"User Answer: {st.session_state['user_answer']}")
        st.session_state['conversation_history'].append(f"AI: {check_answer}")

# if st.button("Clear Chat History"):
#     st.session_state['conversation_history'] = []
#     st.session_state['current_question'] = ""
#     st.session_state['user_answer'] = ""

# st.write("### Conversation History")
# for message in st.session_state['conversation_history']:
#     st.write(message)
