FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install pyyaml
CMD ["python", "test_input.py"]
