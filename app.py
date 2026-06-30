import streamlit as st
import fitz
import re
from io import BytesIO

st.set_page_config(page_title="PDF Number Replacer", layout="centered")
st.title("📄 Multi PDF Number Replacer")
st.markdown("**Saare phone numbers ko USA number se replace karega**")

usa_number = st.text_input("Naya USA Number", value="+1-888-974-0763")

uploaded_files = st.file_uploader(
    "PDF Files Upload Karein", 
    type="pdf", 
    accept_multiple_files=True
)

if st.button("🚀 Replace Numbers in All PDFs", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("Koi PDF upload nahi kiya!")
        st.stop()

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing: {uploaded_file.name}")

        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page in doc:
                # Find all text instances
                text_instances = page.get_text("dict")
                
                for block in text_instances["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"]
                                # Detect phone numbers
                                if re.search(r'[\+]?[0-9\s\-\(\)\.]{8,}', text):
                                    rect = fitz.Rect(span["bbox"])
                                    # Redact old text properly
                                    page.add_redact_annot(rect, fill=(1,1,1))
                                    page.apply_redactions()
                                    # Insert new number
                                    page.insert_text(
                                        rect.tl,
                                        usa_number,
                                        fontsize=span["size"] * 0.95,
                                        color=(0, 0, 0),
                                        fontname="helv"
                                    )

            # Save with optimization
            output_buffer = BytesIO()
            doc.save(output_buffer, garbage=3, clean=True, deflate=True)
            doc.close()

            st.download_button(
                label=f"⬇️ Download Modified - {uploaded_file.name}",
                data=output_buffer.getvalue(),
                file_name=f"MODIFIED_{uploaded_file.name}",
                mime="application/pdf",
                key=idx
            )

        except Exception as e:
            st.error(f"Error in {uploaded_file.name}: {str(e)}")

        progress_bar.progress((idx + 1) / len(uploaded_files))

    st.success("✅ Sab PDFs process ho gayi!")
    st.balloons()
