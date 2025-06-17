FROM python:3.11-slim

# Zet werkdirectory
WORKDIR /app

# Kopieer requirements en installeer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de volledige app (optioneel tijdens dev — meestal via volume)
COPY . .

# Zorg dat flask beschikbaar is
ENV FLASK_APP=app.py
# of jouw startbestand

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]