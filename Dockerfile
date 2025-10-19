FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
# Install system build dependencies required by some Python packages (e.g. pycairo)
# Keep commands in one RUN to reduce image layers and remove apt caches to keep image small.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		pkg-config \
		libcairo2-dev \
		libgirepository1.0-dev \
		gir1.2-gtk-3.0 \
		python3-dev \
		meson \
		ninja-build \
		pandoc \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]