FROM python:3.12-slim

WORKDIR /app

COPY requiremets.txt requiremets.txt

RUN pip insatll -r requiremets.txt

COPY . .

CMD ["python", "main.py"]