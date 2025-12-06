# 1. Pakai Python versi slim (ringan)
FROM python:3.11-slim
# 2. Set folder kerja di dalam container
WORKDIR /code

# 3. Copy daftar belanjaan & Install
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. Copy seluruh kode project ke dalam container
COPY ./app /code/app
COPY ./templates /code/templates
COPY ./scripts /code/scripts

# 5. Buka port 8000
EXPOSE 8000

# 6. Perintah jalankan server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]