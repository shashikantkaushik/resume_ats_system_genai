from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content([input, pdf_content[0], prompt])
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
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")


# Set page config
st.set_page_config(
    page_title="ATS Resume Expert",
    page_icon="📝",
    layout="wide"
)

# Custom CSS that works in both light and dark modes
st.markdown("""
<style>
    .title-container {
        background: linear-gradient(90deg, #6328e1 0%, #9240dd 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        color: white;
        text-align: center;
    }

   

    .info-box {
        background-color: rgba(33, 150, 243, 0.1);
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border-left: 5px solid #2196f3;
    }

    .success-box {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4caf50;
    }

    .stButton>button {
        background: linear-gradient(90deg, #6328e1 0%, #9240dd 100%);
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        opacity: 0.7;
    }

    /* Make sure file uploader is visible in dark mode */
    .stFileUploader>div>label {
        color: inherit !important;
    }

    .stFileUploader>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown(
    '<div class="title-container"><h1>ATS Resume Expert</h1><p>AI-powered resume analysis against job descriptions</p></div>',
    unsafe_allow_html=True)

# Main sections using columns
col1, col2 = st.columns([6, 4])

with col1:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("### 📋 Job Description")
    st.markdown('<div class="info-box">Paste the job description you want to match your resume against</div>',
                unsafe_allow_html=True)
    input_text = st.text_area("", height=300, key="input", placeholder="Paste job description here...")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("### 📤 Resume Upload")
    st.markdown('<div class="info-box">Upload your resume as a PDF file</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"])

    if uploaded_file is not None:
        st.markdown('<div class="success-box">✅ PDF uploaded successfully</div>', unsafe_allow_html=True)
        # Display a preview
        try:
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            uploaded_file.seek(0)  # Reset file pointer after reading
            st.image(images[0], width=300, caption="Resume Preview")
        except:
            st.warning("Could not generate preview, but file was uploaded")
    st.markdown('</div>', unsafe_allow_html=True)

# Analysis buttons section
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown("### 🔍 Analysis Options")

# Use columns for buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit1 = st.button("📝 Professional Review", use_container_width=True)
with col2:
    submit2 = st.button("💡 Skill Improvement", use_container_width=True)
with col3:
    submit3 = st.button("📊 Match Percentage", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Define prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
Based on the resume and job description, identify skills gaps and provide actionable recommendations for the candidate to improve their profile. 
Suggest specific courses, certifications, or projects that would enhance their qualifications for this specific role.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. 
Give me the percentage match between the resume and job description. 
Structure your response as follows:
1. Overall match percentage
2. Keywords present in the resume
3. Critical keywords missing from the resume
4. Final thoughts and recommendations
"""

# Results section
if submit1 or submit2 or submit3:
    if uploaded_file is not None and input_text:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown("### 📊 Analysis Results")

        with st.spinner("Analyzing your resume..."):
            try:
                pdf_content = input_pdf_setup(uploaded_file)

                if submit1:
                    response = get_gemini_response(input_prompt1, pdf_content, input_text)
                    st.markdown("#### Professional Review")
                elif submit2:
                    response = get_gemini_response(input_prompt2, pdf_content, input_text)
                    st.markdown("#### Skills Improvement Recommendations")
                elif submit3:
                    response = get_gemini_response(input_prompt3, pdf_content, input_text)
                    st.markdown("#### ATS Match Analysis")

                st.markdown(response)
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Please upload your resume and provide a job description to continue.")

# Footer
st.markdown("""
<div class="footer">
    Powered by Google Gemini AI • Made with ❤️ by Shashi Kant
</div>
""", unsafe_allow_html=True)