# Use official Python base image
FROM python:3.10

# Install system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 7860

# Run the Streamlit app
CMD ["streamlit", "run", "ugc_net_pdf_app.py", "--server.port=7860", "--server.address=0.0.0.0"]
