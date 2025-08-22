FROM python:3.12
WORKDIR /Transferring_post_from_telegram_to_VK
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
