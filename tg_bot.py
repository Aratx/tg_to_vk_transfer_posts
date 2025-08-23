import os
import pathlib
import re
import shutil
from urllib.parse import urlsplit
from collections import defaultdict
import asyncio

import requests
import vk_api
from environs import Env
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from vk_bot import upload_vk_photo

# Глобальная переменная для хранения медиагрупп
media_groups = defaultdict(dict)
media_groups_lock = asyncio.Lock()

def extract_file_extension(url):
    path, filename_tail = os.path.split(urlsplit(url).path)
    return filename_tail, path.split('/')[-1]

def download_file_image(url, message_info):
    filename_tail, path = extract_file_extension(url)
    pathlib.Path(os.path.join('downloads', path)).mkdir(
        parents=True,
        exist_ok=True
    )
    directory = os.path.join('downloads', path, filename_tail)
    response = requests.get(url)
    with open(directory, 'wb') as file:
        file.write(response.content)

async def publish_to_vk(context: ContextTypes.DEFAULT_TYPE, message_info):
    """Функция для публикации в VK"""
    print("=== PUBLISHING TO VK ===")
    print(f"Message info: {message_info}")
    
    # Проверяем, есть ли контент для отправки
    has_content = (message_info['tgm_photo_id'] or 
                  message_info['tgm_video_id'] or 
                  message_info['tgm_caption'])
    
    if not has_content:
        print('Нет контента для публикации')
        return

    # Обрабатываем текст с ссылками
    final_message = extract_links_from_message(message_info['tgm_caption'], message_info['tgm_entities'])
    
    # Получаем URL файлов
    if message_info['tgm_photo_id']:
        for photo_id in message_info['tgm_photo_id']:
            try:
                photo_file = await context.bot.get_file(photo_id)
                message_info['tgm_photo_url'].append(photo_file.file_path)
            except Exception as e:
                print(f"Error getting photo file: {e}")
    
    if message_info['tgm_video_id']:
        for video_id in message_info['tgm_video_id']:
            try:
                video_file = await context.bot.get_file(video_id)
                message_info['tgm_video_url'].append(video_file.file_path)
            except Exception as e:
                print(f"Error getting video file: {e}")
    
    # Если сообщение пустое после обработки, устанавливаем None
    if not final_message or not final_message.strip():
        final_message = None

    # Скачиваем файлы
    for url in message_info['tgm_photo_url']:
        download_file_image(url, message_info)
    for url in message_info['tgm_video_url']:
        download_file_image(url, message_info)
    
    # Публикуем в VK
    if message_info['tgm_photo_url'] or message_info['tgm_video_url'] or final_message:
        try:
            upload_vk_photo(upload, final_message, vk_group_id, vk, message_info)
            print('Пост размещён в VK')
        except Exception as e:
            print(f"Ошибка при публикации в VK: {e}")
    else:
        print('Нет контента для публикации')
    
    # Удаляем временные файлы
    if os.path.exists('downloads'):
        shutil.rmtree('downloads')

def extract_links_from_message(text, entities):
    """Извлекает ссылки и возвращает текст с ссылками в конце соответствующих фраз"""
    if not text or not entities:
        return text
    
    # Сортируем entities по offset в обратном порядке, чтобы не сбивать индексы при вставке
    sorted_entities = sorted(entities, key=lambda x: x.offset, reverse=True)
    
    result_text = text
    
    for entity in sorted_entities:
        if entity.type == "text_link" and entity.url:
            # Находим позицию конца текста ссылки
            end_pos = entity.offset + entity.length
            # Вставляем URL после текста ссылки
            result_text = result_text[:end_pos] + f" {entity.url}" + result_text[end_pos:]
    
    return result_text

async def process_media_group(media_group_id, context):
    """Обрабатывает всю медиагруппу после получения всех элементов"""
    async with media_groups_lock:
        group_data = media_groups.get(media_group_id)
        if not group_data:
            return
        
        # Ждем немного чтобы все медиа успели прийти
        await asyncio.sleep(2)
        
        # Публикуем всю группу
        await publish_to_vk(context, group_data)
        
        # Удаляем обработанную группу
        del media_groups[media_group_id]

async def intercept_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("=== NEW MESSAGE IN CHANNEL ===")
    print(update)
    
    # Проверяем, есть ли channel_post в update
    if not update.channel_post:
        return
    
    post = update.channel_post
    
    # Создаем структуру данных для сообщения
    current_message_info = {
        'tgm_media_group_id': None,
        'tgm_photo_id': [],
        'tgm_video_id': [],
        'tgm_photo_url': [],
        'tgm_video_url': [],
        'tgm_caption': None,
        'tgm_entities': None,
        'tgm_url': None
    }
    
    # Проверяем media_group_id (если есть)
    if hasattr(post, 'media_group_id') and post.media_group_id:
        media_group_id = post.media_group_id
        current_message_info['tgm_media_group_id'] = media_group_id
        
        if post.caption:
            current_message_info['tgm_caption'] = post.caption
            current_message_info['tgm_entities'] = post.caption_entities
        
        # Добавляем медиа в группу
        async with media_groups_lock:
            if media_group_id not in media_groups:
                media_groups[media_group_id] = current_message_info.copy()
            
            group_data = media_groups[media_group_id]
            
            if post.photo:
                group_data['tgm_photo_id'].append(post.photo[-1].file_id)
            if post.video:
                group_data['tgm_video_id'].append(post.video.file_id)
            
            # Сохраняем caption только из первого сообщения группы
            if post.caption and not group_data['tgm_caption']:
                group_data['tgm_caption'] = post.caption
                group_data['tgm_entities'] = post.caption_entities
        
        # Запускаем обработку группы с задержкой
        asyncio.create_task(process_media_group(media_group_id, context))

    else:
        # Обрабатываем одиночные сообщения
        if post.caption:
            current_message_info['tgm_caption'] = post.caption
            current_message_info['tgm_entities'] = post.caption_entities
        elif post.text:
            current_message_info['tgm_caption'] = post.text
            current_message_info['tgm_entities'] = post.entities
        
        if post.photo:
            current_message_info['tgm_photo_id'].append(post.photo[-1].file_id)
        if post.video:
            current_message_info['tgm_video_id'].append(post.video.file_id)
        
        # Немедленно публикуем одиночные сообщения
        await publish_to_vk(context, current_message_info)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start для ручного управления"""
    await update.message.reply_text('Бот запущен и слушает канал. Новые сообщения будут автоматически публиковаться в VK.')

if __name__ == '__main__':
    env = Env()
    env.read_env()
    tgm_token = env('TGM_TOKEN')
    vk_token = env('VK_TOKEN')
    vk_group_id = env('VK_GROUP_ID')
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    upload = vk_api.upload.VkUpload(vk_session)
    
    # Создаем Application вместо Updater
    application = Application.builder().token(tgm_token).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.ALL, intercept_message))
    
    print("Бот запущен и слушает канал...")
    # Запускаем бота
    application.run_polling()