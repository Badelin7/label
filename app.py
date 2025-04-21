import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io

# Function to clean text data
def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).replace("London", "").strip()

# Function to create label in PDF format
def create_label_pdf(row, box_num, num_boxes):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A6)
    postcode = str(row['Delivery Postcode']).upper()
    
    # Postcode in bold and large font
    c.setFont("Helvetica-Bold", 24)
    c.drawString(10 * mm, 135 * mm, postcode)

    # Address and other details
    c.setFont("Helvetica", 10)
    y = 120 * mm
    if pd.notna(row['Delivery Company Name']):
        c.drawString(10 * mm, y, clean_text(row['Delivery Company Name']))
        y -= 5 * mm

    c.drawString(10 * mm, y, clean_text(row['Delivery Name']))
    y -= 5 * mm

    c.drawString(10 * mm, y, clean_text(row['Delivery Address 1']))
    y -= 5 * mm

    if pd.notna(row['Delivery Address 2']):
        c.drawString(10 * mm, y, clean_text(row['Delivery Address 2']))
        y -= 5 * mm

    c.drawString(10 * mm, y, clean_text(row['Delivery Town/City']))
    y -= 10 * mm

    # Boxes
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10 * mm, y, f"{box_num} of {num_boxes}")
    y -= 8 * mm

    # Phone number
    if pd.notna(row['Phone']):
        c.setFont("Helvetica", 10)
        c.drawString(10 * mm, y, f"Phone: {row['Phone']}")
        y -= 6 * mm

    # Instructions
    if pd.notna(row['Instructions']):
        instructions = str(row['Instructions'])
        text_obj = c.beginText(10 * mm, y)
        text_obj.setFont("Helvetica", 10)
        for line in instructions.splitlines():
            text_obj.textLine(line)
        c.drawText(text_obj)

    c.save()
    buffer.seek(0)
    return buffer

# Streamlit interface
st.title('Label Generator for Deliveries')

# File uploader to upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load data from Excel file
    df = pd.read_excel(uploaded_file)

    # Display the data from the file
    st.write("Check the data from the file:")
    st.write(df.head())

    # Calculate the number of boxes
    num_boxes = int(df['Boxes'].max()) if 'Boxes' in df.columns else 1

    # Generate labels
    for index, row in df.iterrows():
        for box_num in range(1, num_boxes + 1):
            # Create PDF for each label
            pdf_buffer = create_label_pdf(row, box_num, num_boxes)
            st.download_button(
                label=f"Download label for box {box_num}",
                data=pdf_buffer,
                file_name=f"label_{index+1}_box_{box_num}_of_{num_boxes}.pdf",
                mime="application/pdf"
            )