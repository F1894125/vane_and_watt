FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    postgresql-client \
    libpq-dev \
    wget \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://bootstrap.pypa.io/get-pip.py \
    && python3.13 get-pip.py \
    && rm get-pip.py \
    && ln -sf /usr/bin/python3.13 /usr/local/bin/python \
    && ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip

WORKDIR /vane_and_watt

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --ignore-installed -r requirements.txt

COPY . .

# Strip Windows carriage returns (CRLF -> LF)
RUN sed -i 's/\r$//' start.sh
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]