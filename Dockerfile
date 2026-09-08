# Gunakan image python slim yang sangat ringan (base image hanya ~50MB)
FROM python:3.13-slim

# Set environment variables untuk performa dan keamanan
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install dependensi sistem minimal yang diperlukan (gcc untuk kompilasi native jika wheel tidak tersedia)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install dependensi Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code aplikasi
COPY . .

# Expose port yang digunakan uvicorn
EXPOSE 8000

# Jalankan aplikasi
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
