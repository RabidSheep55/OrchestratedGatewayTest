# Base image
FROM python:3-alpine

# Work from in here
WORKDIR /usr/src/app

# Copy and install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy the app over
COPY app.py ./

# App API listens on this port
EXPOSE 8888

# Start app
CMD ["python3", "./app.py"]
