# IMPORTING NECESSARY LIBRARIES
import requests
import streamlit as st
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
import google.generativeai as genai
import os


# Streamlit app layout
st.set_page_config(page_title="Drawing Enhancer", page_icon="🎨", layout="wide")
st.title("🎨 Drawing Enhancer")

# links to get API keys
st.markdown("### Obtain Your API Keys")
st.write("To use this app, you will need API keys from both Gemini and ClipDrop:")
st.markdown("- [Get your Gemini API Key](https://ai.google.dev/gemini-api)")
st.markdown("- [Get your ClipDrop API Key](https://clipdrop.co)")

# Take user input for their API keys
GENAI_API_KEY = st.text_input("Enter your Gemini API Key:",  "")
SKETCH_TO_IMAGE_API_KEY = st.text_input("Enter your ClipDrop API Key:", "")

# Configure Gemini API based on user input
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
else:
    st.warning("Please enter your Gemini API key.")

# Function to generate a prompt from the sketch using Gemini API
def generate_prompt_from_sketch(file_path):
    if not GENAI_API_KEY:
        return None  # Exit if no API key
    uploaded_file = genai.upload_file(file_path)
    if uploaded_file:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([uploaded_file, "\n\n", "Describe the scene in this sketch."])
        if response:
            prompt = response.text
            return prompt
    return None

# Function to enhance the drawing using ClipDrop API with user-provided key
def enhance_drawing_text_to_image_api(prompt):
    if not SKETCH_TO_IMAGE_API_KEY:
        st.error("Please enter your ClipDrop API key.")
        return None
    
    url = "https://clipdrop-api.co/text-to-image/v1"
    headers = {"x-api-key": SKETCH_TO_IMAGE_API_KEY}
    files = {"prompt": (None, prompt)}

    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        with open("result.jpg", "wb") as f:
            f.write(response.content)
        return "result.jpg"
    else:
        st.error("Failed to generate enhanced image.")
        return None

# Streamlit layout for drawing tool
st.sidebar.markdown("### Customize Your Drawing")
drawing_mode = st.sidebar.selectbox("Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform"))
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#ffffff")
realtime_update = st.sidebar.checkbox("Update in realtime", True)

# Create a canvas for drawing
canvas_result = st_canvas( 
    fill_color=bg_color,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=400,
    width=400,
    update_streamlit=realtime_update,
    drawing_mode=drawing_mode,
    key="canvas"
)

# Display the sketch and process the enhancement
if canvas_result.image_data is not None:
    st.image(canvas_result.image_data, caption='Your Drawing', use_column_width=True)

if st.button("Enhance Drawing"):
    if not GENAI_API_KEY or not SKETCH_TO_IMAGE_API_KEY:
        st.error("Please enter both your Gemini and ClipDrop API keys before enhancing the drawing.")
    elif canvas_result.image_data is not None:
        sketch_image = Image.fromarray(canvas_result.image_data.astype(np.uint8))
        file_path = "sketch.png"
        sketch_image.save(file_path, format='PNG')

        prompt = generate_prompt_from_sketch(file_path)
        if prompt:
            enhanced_image_path = enhance_drawing_text_to_image_api(prompt)
            if enhanced_image_path:
                st.image(enhanced_image_path, caption='Enhanced Drawing', use_column_width=True)
            else:
                st.error("Failed to generate enhanced image.")
        else:
            st.error("Failed to generate prompt from sketch.")
