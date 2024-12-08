FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ src/
COPY src/main.py .
COPY data/ data/

# Run the main script by default
CMD ["python", "src/main.py"]