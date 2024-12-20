# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_PORT=8501 \
    FASTAPI_PORT=8000

# Install Python 3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the ports for Streamlit and FastAPI
EXPOSE ${STREAMLIT_PORT} ${FASTAPI_PORT}

# Command to run both Streamlit and FastAPI using a shell script
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${FASTAPI_PORT} & streamlit run streamlit-app.py --server.port=${STREAMLIT_PORT} --server.address=0.0.0.0"]
