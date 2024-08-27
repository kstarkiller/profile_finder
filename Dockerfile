# Description: Dockerfile for the AI based Profile Matching Streamlit app
# Authors: Kevin SIMON, Thibaut BOGUSZEWSKI
# Version: 1.3
# Date: 2024-08-27

# Use an official Python runtime as a parent image
FROM python:3.11.9-slim

# Set the working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy model
RUN python -m spacy download fr_core_news_lg

# Copy the rest of the application code
COPY . /app

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define build arguments
ARG AZURE_OPENAI_API_KEY
ARG AZURE_OPENAI_ENDPOINT
ARG AZURE_SEARCH_API_KEY
ARG AZURE_SEARCH_ENDPOINT

# Set environment variables from build arguments
ENV AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
ENV AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
ENV AZURE_SEARCH_API_KEY=${AZURE_SEARCH_API_KEY}
ENV AZURE_SEARCH_ENDPOINT=${AZURE_SEARCH_ENDPOINT}

# Run app.py when the container launches
CMD ["streamlit", "run", "main.py", "--server.port=8080"]