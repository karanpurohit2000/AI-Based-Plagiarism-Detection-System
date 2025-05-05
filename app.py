# app.py
import streamlit as st
import os
import base64
from PIL import Image
from file_processor import FileProcessor
from ai_service import AIService
from config import Config
from report_generator import generate_plagiarism_report
from datetime import datetime
import sys
from pathlib import Path

# Add project directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Custom CSS Injection
def inject_custom_css():
    st.markdown("""
    <style>
        :root {
            --primary: #6e48aa;
            --secondary: #9d50bb;
            --accent: #4776e6;
            --dark-bg: #121212;
            --dark-card: #1e1e1e;
            --dark-text: #e0e0e0;
            --dark-border: #333;
            --success: #28a745;
            --warning: #fd7e14;
            --danger: #dc3545;
        }
        
        .stApp {
            background-color: var(--dark-bg) !important;
            color: var(--dark-text) !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary) !important;
            font-weight: 700 !important;
            text-align: center !important;
        }
        
        .stButton>button {
            border-radius: 25px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
            background: linear-gradient(to right, var(--primary), var(--secondary)) !important;
            color: white !important;
            border: none !important;
            width: 100%;
        }
        
        .stFileUploader>div>div {
            border: 2px dashed var(--primary) !important;
            border-radius: 15px !important;
            background-color: var(--dark-card) !important;
            padding: 30px !important;
        }
        
        .score-display {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
            color: var(--primary);
            animation: pulse 2s infinite;
        }
        
        .card {
            background: var(--dark-card);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
            border: 1px solid var(--dark-border);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .download-btn {
            display: inline-block;
            padding: 12px 28px;
            background: linear-gradient(135deg, #6e48aa, #9d50bb);
            color: white !important;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(110, 72, 170, 0.3);
            border: none;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 0;
            text-align: center;
            width: 100%;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(110, 72, 170, 0.4);
            background: linear-gradient(135deg, #9d50bb, #4776e6);
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Plagiarism Checker Pro",
        layout="wide",
        page_icon="🔍",
        initial_sidebar_state="expanded"
    )
    inject_custom_css()
    handle_navigation()
    
def show_features():
    st.markdown("""
    <div style="margin-top: 40px;">
        <h2>✨ Key Features</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div class="card">
                <h3>📝 Document Analysis</h3>
                <p>Detect text plagiarism in PDF, DOCX, and TXT files with advanced AI algorithms.</p>
            </div>
            <div class="card">
                <h3>🖼️ Visual Similarity</h3>
                <p>Check images and logos for potential copyright infringement using deep learning.</p>
            </div>
            <div class="card">
                <h3>🔗 Citation Generator</h3>
                <p>Automatically generate proper citations and references for your content.</p>
            </div>
            <div class="card">
                <h3>📊 Detailed Reports</h3>
                <p>Download comprehensive plagiarism reports in PDF format.</p>
            </div>
            <div class="card">
                <h3>⚡ Real-time Analysis</h3>
                <p>Get instant results with our high-performance processing engine.</p>
            </div>
            <div class="card">
                <h3>🔒 Privacy Focused</h3>
                <p>Your documents are processed securely and never stored permanently.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def handle_navigation():
    st.markdown("""
    <div class="card">
        <h1 style="text-align: center;">🔍 AI Plagiarism Detection System</h1>
        <p style="text-align: center;">Comprehensive analysis for documents and images</p>
    </div>
    """, unsafe_allow_html=True)

    if 'analysis_type' not in st.session_state:
        st.session_state.analysis_type = "document"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Document Analysis", key="doc_btn"):
            st.session_state.analysis_type = "document"
    with col2:
        if st.button("🖼 Image Analysis", key="img_btn"):
            st.session_state.analysis_type = "image"

    # Show features section after navigation buttons
    

    if st.session_state.analysis_type == "document":
        handle_document()
    else:
        handle_image()

def handle_document():
    file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])
    
    if file:
        with st.spinner("Analyzing content..."):
            fp = FileProcessor()
            temp_path = f"temp_{file.name}"
            
            try:
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                
                text = fp.process(temp_path)
                ai = AIService(Config.COHERE_API_KEY)
                analysis = ai.analyze_content(text)
                
                display_results(text, analysis, file.name)
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    show_features()

def handle_image():
    file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if file:
        with st.spinner("Analyzing image..."):
            temp_file = f"temp_{file.name}"
            try:
                with open(temp_file, "wb") as f:
                    f.write(file.getbuffer())
                
                ai = AIService(Config.COHERE_API_KEY)
                analysis = ai.analyze_image(temp_file)
                img = Image.open(temp_file)
                
                st.image(img, use_container_width=True, caption="Uploaded Image")
                display_image_analysis(analysis)
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    show_features()

def display_image_analysis(analysis):
    with st.expander("🌐 Web Matching Results"):
        if analysis['vision_analysis']['matching_images']:
            st.markdown("**Matching Images Found Online:**")
            for url in analysis['vision_analysis']['matching_images'][:3]:
                st.markdown(f"- [Source]({url})")
        else:
            st.info("No matching images found on the web")

    with st.expander("🎨 Visual Analysis"):
        st.markdown("**Dominant Colors:**")
        for color in analysis['vision_analysis']['colors'][:3]:
            st.markdown(
                f"<div class='color-box' style='background-color: rgb({color.red}, {color.green}, {color.blue})'></div>",
                unsafe_allow_html=True
            )

    with st.expander("📖 Extracted Text Analysis"):
        if analysis['text_analysis']['direct_quotes'] or analysis['text_analysis']['paraphrased']:
            display_text_analysis(analysis['text_analysis'])
        else:
            st.info("No significant text content found in image")

def display_text_analysis(analysis):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Direct Quotes")
        if analysis['direct_quotes']:
            for quote in analysis['direct_quotes']:
                st.markdown(f"- {quote['text']}")
                st.caption(f"Sources: {', '.join(quote['sources'])}")
        else:
            st.info("No direct quotes found")

    with col2:
        st.markdown("#### Paraphrased Content")
        if analysis['paraphrased']:
            for para in analysis['paraphrased']:
                st.markdown(f"- {para['text'][:200]}...")
                st.caption(f"Similarity: {para['similarity']:.1%}")
        else:
            st.info("No paraphrased content detected")

def display_results(text, analysis, filename):
    score_color = "#28a745" if analysis['plagiarism_score'] < 25 else "#fd7e14" if analysis['plagiarism_score'] < 50 else "#dc3545"
    st.markdown(f"""
    <div class="card" style="border: 2px solid {score_color};">
        <h3 style="color: {score_color}; text-align: center;">Plagiarism Score: {analysis['plagiarism_score']}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📄 Document Preview", expanded=True):
        st.text_area("Full Text", value=text[:3000] + (" [...]" if len(text) > 3000 else ""), height=300)

    with st.container():
        st.markdown("### 🔍 Analysis Results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Direct Quotes Found")
            if analysis['direct_quotes']:
                for quote in analysis['direct_quotes']:
                    st.markdown(f"**Quote**: _{quote['text']}_")
                    st.markdown(f"Sources: {', '.join(quote['sources'])}")
                    st.divider()
            else:
                st.info("No direct quotes detected")
        
        with col2:
            st.markdown("#### Potential Paraphrasing")
            if analysis['paraphrased']:
                for para in analysis['paraphrased']:
                    st.markdown(f"**Text**: {para['text'][:200]}...")
                    st.markdown(f"Similar Sources: {', '.join(para['sources'])}")
                    st.divider()
            else:
                st.info("No paraphrased content detected")
        
        st.markdown("#### Reference Validation")
        if analysis['references']:
            valid_refs = [r for r in analysis['references'] if r['valid']]
            st.success(f"✅ {len(valid_refs)} Valid References Found")
            st.error(f"❌ {len(analysis['references'])-len(valid_refs)} Invalid References")
            
            with st.expander("View References"):
                for ref in analysis['references']:
                    status = "✅ Valid" if ref['valid'] else "❌ Invalid"
                    st.markdown(f"{status}: {ref['reference']}")
        else:
            st.warning("No reference section found")

        # Download Report Button
        report_path = generate_plagiarism_report(text, analysis, filename)
        with open(report_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'''
            <a class="download-btn" href="data:application/pdf;base64,{b64}" 
               download="{filename}_report.pdf">
               📥 Download Full Report
            </a>
            '''
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    main()