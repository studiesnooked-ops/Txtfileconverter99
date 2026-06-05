FROM python:3.9-slim-bullseye

# Create a safe directory for your app
WORKDIR /app

RUN apt-get -qq update && apt-get -qq install -y git wget pv jq python3-dev ffmpeg mediainfo

# Copy your files into /app
COPY . .

# Install requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Start only your main Python script
CMD ["python3", "main.py"]
