import requests
from environs import Env


def get_token(vk_app_client_id, client_secret):
    url = 'https://oauth.vk.com/authorize'
    params = {
        'client_id': vk_app_client_id,
        'client_secret': client_secret,
        'response_type': 'token',
        'scope': 'video, manage, docs, app_widget, photos, stories, groups, offline, wall'
    }
    response = requests.get(url, params=params)
    print(response.url)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tgm_token = env('TGM_TOKEN')
    tgm_id = env('TGM_ID')
    vk_token = env('VK_TOKEN')
    vk_group_id = env('VK_GROUP_ID')
    client_secret = env('VK_CLIENT_SECRET')
    vk_app_client_id = env('VK_APP_CLIENT_ID')
    get_token(vk_app_client_id, client_secret)
