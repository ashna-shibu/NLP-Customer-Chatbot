# Use python 3.10 slim version
FROM python:3.10-slim

# Set the working directory to the root of the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download necessary NLTK data for your nlp_service.py
RUN python -m nltk.downloader punkt stopwords wordnet

# Copy all your project files (app folder, models, etc.) into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the app
# "app.main:app" tells uvicorn to look inside the "app" folder for "main.py"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]