import vk_api
from environs import Env
import os


def upload_vk_photo(upload, message, vk_group_id, vk, message_info):
    attachment = []
    if message_info['tgm_photo_url'] or message_info['tgm_video_url'] or message_info['tgm_url']:
        if message_info['tgm_photo_url'] and not message_info['tgm_video_url']:
            files_image = os.listdir(os.path.join('downloads', 'photos'))
            files_path_image = [os.path.join('downloads', 'photos', i) for i in files_image]
            photo_list = upload.photo_wall(files_path_image, group_id=vk_group_id)
            attachment = ['photo{owner_id}_{id}'.format(**item) for item in photo_list]
            vk.wall.post(owner_id=f'-{vk_group_id}', message=message, attachment=attachment)
        elif message_info['tgm_video_url'] and not message_info['tgm_photo_url']:
            files_video = os.listdir(os.path.join('downloads', 'videos'))
            files_path_video = [os.path.join('downloads', 'videos', i) for i in files_video]
            for file_path_video in files_path_video:
                video_list = upload.video(file_path_video, group_id=vk_group_id)
                attachment.append(f'video{video_list["owner_id"]}_{video_list["video_id"]}')
            vk.wall.post(owner_id=f'-{vk_group_id}', message=message, attachment=attachment)
        elif message_info['tgm_photo_url'] and message_info['tgm_video_url']:
            files_image = os.listdir(os.path.join('downloads', 'photos'))
            files_path_image = [os.path.join('downloads', 'photos', i) for i in files_image]
            photo_list = upload.photo_wall(files_path_image, group_id=vk_group_id)
            attachment = ['photo{owner_id}_{id}'.format(**item) for item in photo_list]
            files_video = os.listdir(os.path.join('downloads', 'videos'))
            files_path_video = [os.path.join('downloads', 'videos', i) for i in files_video]
            for file_path_video in files_path_video:
                video_list = upload.video(file_path_video, group_id=vk_group_id)
                attachment.append(f'video{video_list["owner_id"]}_{video_list["video_id"]}')
            vk.wall.post(owner_id=f'-{vk_group_id}', message=message, attachment=attachment)
        else:
            attachment = message_info['tgm_url']
            vk.wall.post(owner_id=f'-{vk_group_id}', message=message, attachment=attachment)
    else:
        attachment = None
        vk.wall.post(owner_id=f'-{vk_group_id}', message=message, attachment=attachment)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    vk_token = env('VK_TOKEN')
    vk_group_id = env('VK_GROUP_ID')
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    upload = vk_api.upload.VkUpload(vk_session)
    vk.wall.post(owner_id=f'-{vk_group_id}', message='message', attachment=['photo3251639_456239281', 'photo3251639_456239280'])
