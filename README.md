# RAG Chatbot

## Introduction

Welcome to the **RAG Chatbot** project! This project is a sophisticated chatbot designed to interact with various types of files and provide insightful responses using a powerful language model. The chatbot integrates several technologies to process text from images, PDFs, and spreadsheets, and generates meaningful responses based on the extracted content.

![RAG Chatbot](https://github.com/anshh-arora/RAG-Chatbot/blob/main/66825cdfbe8fac92ad183f74_superteams_llama3.jpg)

## Use Case and Features

The RAG Chatbot is designed to help users interact with different types of documents and extract useful information efficiently. Here’s what you can do with it:

- **Text Extraction:** Extract text from images, PDFs, and spreadsheets.
- **File Handling:** Upload and process images, PDFs, and Excel/CSV files.
- **Chat Interface:** Engage in a conversation with the chatbot to get answers based on the extracted text.
- **Document Analysis:** Automatically detect and handle large documents, providing text extraction and summaries as needed.

## How It Works

### Language Model (LLM)

The chatbot uses a Large Language Model (LLM) to understand and generate responses based on the extracted text. Specifically, we are using Groq's LLM, which allows for sophisticated natural language processing tasks. The LLM helps in:

- Generating contextually relevant responses.
- Handling user queries based on the content extracted from the uploaded documents.

### Tesseract OCR

Tesseract OCR (Optical Character Recognition) is used for extracting text from images. It converts printed or handwritten text from images into machine-encoded text. This is crucial for processing image files and extracting readable content.

- **Tesseract Path Setup:** 
  - Ensure Tesseract is installed on your system.
  - Add the path to the Tesseract executable to your environmental variables.
  - Example path in the code: `pytesseract.pytesseract.tesseract_cmd = r"C:\Path\To\Tesseract-OCR\tesseract.exe"`

### Poppler

Poppler is used for converting PDF pages into images. This is necessary for extracting text from PDFs that are not directly supported by text extraction libraries.

- **Poppler Path Setup:** 
  - Ensure Poppler is installed.
  - Add the path to the Poppler bin directory to your environmental variables.
  - Example path in the code: `poppler_path = r"C:\Path\To\Poppler\bin"`

## Video Demonstration

Check out the video below to see the RAG Chatbot in action:

[Watch the Project Video](https://github.com/anshh-arora/RAG-Chatbot/blob/main/chatbot%20testing%20vedio.mp4)

## How to Clone the Repository

To get started with the RAG Chatbot, clone the repository using the following command:

```bash
git clone https://github.com/your_username/rag-chatbot.git
cd rag-chatbot


