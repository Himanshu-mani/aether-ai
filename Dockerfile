FROM python:3.11-slim

WORKDIR /app

# Pehle requirements copy karo aur install karo (Taaki build fast ho)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saara code copy karo
COPY . .

# Tera main program
CMD ["python", "main.py"] 
