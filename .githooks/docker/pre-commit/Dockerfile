FROM python:3.12-alpine

WORKDIR /app

RUN pip install --no-cache-dir black

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]
