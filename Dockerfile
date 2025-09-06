FROM python:3.11-slim


# Essential Linux packages and all Google Chrome dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    gnupg \
    jq \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf-2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libxss1 \
    libappindicator3-1 \
    lsb-release \
    libexpat1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxfixes3 \
    libxkbcommon0 \
    --no-install-recommends \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*


# Install Chrome for Testing (CfT) bundle with matching ChromeDriver
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install


# Add Chrome & ChromeDriver to PATH
ENV PATH="/usr/local/bin:${PATH}"

# Install Selenium for Python
RUN pip install --no-cache-dir selenium

# Default working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY .env .

# Set display port to avoid crash
ENV DISPLAY=:99

# Run main.py
CMD ["python", "main.py"]