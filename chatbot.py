import gradio as gr
from groq import Groq, RateLimitError
import pandas as pd
from PIL import Image
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
import os
import time

# Set the path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = #path to pytesseract .exe file

# Set the path to Poppler for PDF image extraction
poppler_path = #path to bin folder of poppler file

# Your Groq API key
YOUR_GROQ_API_KEY = #your Groq Api Key

# Initialize Groq client
client = Groq(api_key=YOUR_GROQ_API_KEY)

# Global variable to store extracted text
extracted_text = ""

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def remove_header_footer(image, header_height=3.9, footer_height=2.27):
    width, height = image.size
    header_height_pixels = int(header_height * 96)  # Convert inches to pixels (assuming 96 DPI)
    footer_height_pixels = int(footer_height * 96)
    cropping_box = (0, header_height_pixels, width, height - footer_height_pixels)
    return image.crop(cropping_box)

def handle_file(file, page_range=None):
    global extracted_text
    extracted_text = ""
    
    if file is None:
        return None, "No file uploaded"
    
    file_name = file.name.lower()
    
    if file_name.endswith(('png', 'jpg', 'jpeg')):
        image = Image.open(file)
        extracted_text = extract_text_from_image(image)
        return image, extracted_text
    
    elif file_name.endswith('pdf'):
        text = ""
        pdf_images = []
        start_page = 1
        end_page = None

        if page_range:
            try:
                start_page, end_page = map(int, page_range.split('-'))
            except ValueError:
                start_page = int(page_range)
                end_page = start_page

        with pdfplumber.open(file) as pdf_file:
            total_pages = len(pdf_file.pages)
            end_page = end_page or total_pages

            for page_number in range(start_page - 1, end_page):
                page = pdf_file.pages[page_number]
                page_text = page.extract_text() or ""
                text += f"Page {page_number + 1}:\n{page_text}\n"

                try:
                    page_images = convert_from_path(file.name, first_page=page_number + 1, last_page=page_number + 1, poppler_path=poppler_path)
                    page_images = [remove_header_footer(img) for img in page_images]
                    pdf_images.extend(page_images)
                    for img in page_images:
                        image_text = extract_text_from_image(img)
                        text += f"Page {page_number + 1} (Image):\n{image_text}\n"
                except Exception as e:
                    text += f"Error processing images on page {page_number + 1}: {e}\n"

        extracted_text = text
        if pdf_images:
            return pdf_images[0], extracted_text
        else:
            return None, extracted_text
    
    elif file_name.endswith(('xls', 'xlsx')):
        df = pd.read_excel(file)
        extracted_text = df.to_string()
        return None, extracted_text
    
    elif file_name.endswith('csv'):
        df = pd.read_csv(file)
        extracted_text = df.to_string()
        return None, extracted_text
    
    else:
        return None, "Unsupported file type"

def split_text(text, max_length=2000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        word_length = len(word) + 1  # +1 for the space or punctuation
        if current_length + word_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def is_rate_limited():
    # Implement a method to check rate limit status if needed
    return False


def chat_groq_sync(user_input, history, extracted_text):
    retries = 5
    while retries > 0:
        rate_limit_status = is_rate_limited()
        if rate_limit_status:
            return f"{rate_limit_status} Please try again later."

        messages = [{"role": "system", "content": "The following text is extracted from the uploaded file:\n" + extracted_text}]
        for msg in history:
            messages.append({"role": "user", "content": msg[0]})
            messages.append({"role": "assistant", "content": msg[1]})
        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=1000,
                temperature=0.4
            )

            response_content = response.choices[0].message.content
            return response_content
        except RateLimitError as e:
            error_info = e.args[0] if e.args else {}
            error_message = error_info.get('error', {}).get('message', '') if isinstance(error_info, dict) else str(error_info)

            wait_time = 60
            if 'try again in' in error_message:
                try:
                    wait_time = float(error_message.split('try again in ')[-1].split('s')[0])
                except ValueError:
                    pass

            print(f"Rate limit error: {error_message}")
            print(f"Retrying in {wait_time:.2f} seconds...")
            retries -= 1
            if retries > 0:
                time.sleep(wait_time)
            else:
                return "Rate limit exceeded. Please try again later."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred. Please try again later."

def update_chat(user_input, history):
    global extracted_text
    response = chat_groq_sync(user_input, history, extracted_text)
    history.append((user_input, response))
    return history, history, ""

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("# RAG Chatbot")
            gr.Markdown("Check out the [GitHub](https://github.com/anshh-arora?tab=repositories) for more information.")
        
            file = gr.File(label="Upload your file")
            page_range = gr.Textbox(label="If the uploaded document is a PDF and has more than 10 pages, enter the page range (e.g., 1-3) or specific page number (e.g., 2):", lines=1, visible=False, interactive=True)
            file_upload_button = gr.Button("Upload File")
            image_display = gr.Image(label="Uploaded Image", visible=False)
            extracted_text_display = gr.Textbox(label="Extracted Text", interactive=False)
        
        with gr.Column(scale=3):
            gr.Markdown("# Chat with your file")
            history = gr.State([])
            with gr.Column():
                chatbot = gr.Chatbot(height=500, bubble_full_width=False)
                user_input = gr.Textbox(placeholder="Enter Your Query", visible=True, scale=7, interactive=True)
                
                clear_btn = gr.Button("Clear")
                undo_btn = gr.Button("Undo")
                
                user_input.submit(update_chat, [user_input, history], [chatbot, history, user_input])
                clear_btn.click(lambda: ([], []), None, [chatbot, history])
                undo_btn.click(lambda h: h[:-2], history, history)
            
    def show_page_range_input(file):
        if file and file.name.lower().endswith('pdf'):
            with pdfplumber.open(file) as pdf_file:
                if len(pdf_file.pages) > 10:
                    return gr.update(visible=True)
        return gr.update(visible=False)

    file.change(show_page_range_input, inputs=file, outputs=page_range)
    file_upload_button.click(handle_file, [file, page_range], [image_display, extracted_text_display])

if __name__ == "__main__":
    demo.launch(share=True)
