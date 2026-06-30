import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import re

st.set_page_config(page_title="PDF Number Replacer", layout="centered")
st.title("📄 Multi PDF Number Replacer")
st.markdown("**Ek saath multiple PDFs upload karo aur number replace karo**")

# Settings
usa_number = st.text_input("Naya USA Number (Replace ke liye)", value="+1-888-974-0763")

uploaded_files = st.file_uploader(
    "PDF Files Upload Karein", 
    type="pdf", 
    accept_multiple_files=True,
    help="Ek ya multiple PDFs select kar sakte hain"
)

if st.button("🚀 Replace Numbers in All PDFs", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("Koi PDF upload nahi kiya!")
        st.stop()
    
    if not usa_number:
        st.error("Naya number daalna zaroori hai!")
        st.stop()

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing: {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")

        try:
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page in doc:
                text = page.get_text()
                # Detect any phone numbers
                phones = re.findall(r'[\+]?[0-9]{1,4}[-\s\.]?[0-9]{2,}[-\s\.]?[0-9]{2,}', text)
                
                for phone in phones:
                    instances = page.search_for(phone)
                    for inst in instances:
                        page.add_redact_annot(inst)
                        page.apply_redactions()
                        page.insert_text(inst.tl, usa_number, fontsize=inst.height * 0.9)

            # Create download button
            output_buffer = BytesIO()
            doc.save(output_buffer)
            doc.close()

            st.download_button(
                label=f"⬇️ Download Modified - {uploaded_file.name}",
                data=output_buffer.getvalue(),
                file_name=f"MODIFIED_{uploaded_file.name}",
                mime="application/pdf",
                key=f"btn_{idx}"
            )

        except Exception as e:
            st.error(f"Error in {uploaded_file.name}: {str(e)}")
        
        progress_bar.progress((idx + 1) / len(uploaded_files))

    status_text.success("✅ Sab PDFs process ho gaye!")
    st.balloons()