FROM python:3.12
WORKDIR /tg_to_vk_transfer_posts
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
