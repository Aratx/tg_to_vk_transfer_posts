import vk_api
from environs import Env
import os

def upload_vk_photo(upload, message, vk_group_id, vk, message_info):
    attachment = []
    
    # Обрабатываем фото
    if message_info['tgm_photo_url']:
        photos_attachments = process_photos(upload, vk_group_id, message_info)
        attachment.extend(photos_attachments)
    
    # Обрабатываем видео
    if message_info['tgm_video_url']:
        videos_attachments = process_videos(upload, vk_group_id, message_info)
        attachment.extend(videos_attachments)
    
    # Обрабатываем URL
    if message_info['tgm_url']:
        attachment.append(message_info['tgm_url'])
    
    # Публикуем пост со всеми вложениями
    try:
        if attachment:
            vk.wall.post(
                owner_id=f'-{vk_group_id}', 
                message=message, 
                attachment=','.join(attachment)
            )
            print(f"Опубликован пост с {len(attachment)} вложениями")
        else:
            vk.wall.post(owner_id=f'-{vk_group_id}', message=message)
            print("Опубликован текстовый пост")
    except Exception as e:
        print(f"Ошибка при публикации в VK: {e}")
        raise

def process_photos(upload, vk_group_id, message_info):
    """Обрабатывает все фото и возвращает attachments"""
    attachments = []
    
    if message_info['tgm_photo_url']:
        # Создаем папку для фото если нет
        os.makedirs('downloads/photos', exist_ok=True)
        
        # Загружаем все фото
        photo_files = []
        for photo_url in message_info['tgm_photo_url']:
            filename = os.path.basename(photo_url)
            file_path = os.path.join('downloads', 'photos', filename)
            photo_files.append(file_path)
        
        try:
            # Загружаем все фото одним запросом
            photo_list = upload.photo_wall(photo_files, group_id=vk_group_id)
            attachments.extend([f'photo{item["owner_id"]}_{item["id"]}' for item in photo_list])
            print(f"Загружено {len(photo_list)} фото")
        except Exception as e:
            print(f"Ошибка при загрузке фото: {e}")
    
    return attachments

def process_videos(upload, vk_group_id, message_info):
    """Обрабатывает все видео и возвращает attachments"""
    attachments = []
    
    if message_info['tgm_video_url']:
        # Создаем папку для видео если нет
        os.makedirs('downloads/videos', exist_ok=True)
        
        # Загружаем каждое видео отдельно
        for video_url in message_info['tgm_video_url']:
            try:
                filename = os.path.basename(video_url)
                file_path = os.path.join('downloads', 'videos', filename)
                
                video_data = upload.video(
                    video_file=file_path,
                    group_id=vk_group_id,
                    name=f"Video from Telegram"
                )
                attachments.append(f'video{video_data["owner_id"]}_{video_data["video_id"]}')
                print(f"Загружено видео: {filename}")
            except Exception as e:
                print(f"Ошибка при загрузке видео {video_url}: {e}")
    
    return attachments

if __name__ == '__main__':
    env = Env()
    env.read_env()
    vk_token = env('VK_TOKEN')
    vk_group_id = env('VK_GROUP_ID')
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    upload = vk_api.upload.VkUpload(vk_session)