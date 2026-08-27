FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /vane_and_watt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Strip Windows carriage returns (CRLF -> LF)
RUN sed -i 's/\r$//' start.sh

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
