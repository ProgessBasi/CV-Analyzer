from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import time

# Configure page
st.set_page_config(
    page_title="AI Resume Expert 🚀",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        animation: fadeInDown 1s ease-out;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out 0.3s both;
    }

    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        transition: all 0.3s ease;
        animation: slideInUp 0.8s ease-out;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }

    .upload-area {
        border: 2px dashed #3b82f6;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(145deg, #f0f9ff 0%, #e0f2fe 100%);
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    }

    .upload-area:hover {
        border-color: #1d4ed8;
        background: linear-gradient(145deg, #dbeafe 0%, #bfdbfe 100%);
    }

    .success-message {
        background: linear-gradient(145deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #22c55e;
        animation: slideInRight 0.5s ease-out;
    }

    .action-button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }

    .response-container {
        background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 15px;
        padding: 2rem;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        animation: fadeIn 0.8s ease-out;
    }

    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f4f6;
        border-top: 4px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Configure API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert the PDF to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")


def show_loading():
    with st.spinner('🔍 Analyzing your resume with AI...'):
        time.sleep(1)  # Small delay for better UX


# Header Section
st.markdown('<h1 class="main-header">🚀 AI Resume Expert</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform your career with AI-powered resume analysis</p>', unsafe_allow_html=True)

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    # Job Description Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Job Description")
    st.markdown("Paste the job description you're targeting:")
    input_text = st.text_area(
        "",
        key="input",
        height=200,
        placeholder="Enter the job description here..."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # File Upload Section
    st.markdown('<div class="feature-card upload-area">', unsafe_allow_html=True)
    st.markdown("### 📄 Upload Your Resume")
    st.markdown("Upload your resume in PDF format for analysis:")
    uploaded_file = st.file_uploader(
        "",
        type=["pdf"],
        help="Only PDF files are supported"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Success message
    if uploaded_file is not None:
        st.markdown(
            '<div class="success-message">✅ PDF uploaded successfully! Ready for analysis.</div>',
            unsafe_allow_html=True
        )

with col2:
    # Sidebar with actions
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Analysis Options")
    st.markdown("Choose your analysis type:")

    st.markdown("---")

    # Action buttons with custom styling
    submit1 = st.button(
        "📊 Resume Analysis",
        help="Get detailed analysis of your resume",
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    submit3 = st.button(
        "🎯 Match Score",
        help="Check how well your resume matches the job",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Tips section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    - Use keywords from job description
    - Quantify your achievements
    - Keep format ATS-friendly
    - Tailor for each application
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

# Response handling
if submit1:
    if uploaded_file is not None and input_text.strip():
        with st.spinner('🔍 Analyzing your resume...'):
            try:
                pdf_content = input_pdf_setup(uploaded_file)
                response = get_gemini_response(input_prompt1, pdf_content, input_text)

                st.markdown('<div class="response-container">', unsafe_allow_html=True)
                st.markdown("### 📊 Resume Analysis Results")
                st.write(response)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("⚠️ Please upload your resume and enter a job description first!")

elif submit3:
    if uploaded_file is not None and input_text.strip():
        with st.spinner('🎯 Calculating match score...'):
            try:
                pdf_content = input_pdf_setup(uploaded_file)

                response = get_gemini_response(input_prompt3, pdf_content, input_text)

                st.markdown('<div class="response-container">', unsafe_allow_html=True)
                st.markdown("### 🎯 Match Score Results")
                st.write(response)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("⚠️ Please upload your resume and enter a job description first!")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #6b7280; margin-top: 2rem;">Made with ❤️ using Streamlit & Google AI</p>',
    unsafe_allow_html=True
)