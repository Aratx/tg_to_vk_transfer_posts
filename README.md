# Бот для переноса постов из группы Telegram в группу VK
Программа по реализации бота, для переноса постов из группы Telegram в группу VK.

Бот умеет принимать разные посты из Телеграма (ссылки, фотографии, видео, описания) и транслирует их в указанную группу ВК
# Установка без докера
- Установить `Python 3.12`
- Скачать репозиторий проекта:
```shell
git clone https://github.com/Aratx/tg_to_vk_transfer_posts
```
- Создайте и активируйте виртуальное окружение в корневой папке проекта:
```shell
cd verb_game/
python3 -m venv venv
source venv/bin/activate
```
- Установить рекомендации:
```shell
pip install -r requirements.txt
```
- Создайте в корне проекта файл `.env` и запишите в него необходимые ключи:
```shell
nano .env
```
- Создать группу ВК, можете это сделать по [этой ссылке](https://vk.com/groups?tab=admin&w=groups_create).
- Узнать `group_id` можно по [этой ссылке](https://regvk.com/id/)
- Заполняем .env
### Заполнение файла `.env`
- TGM_TOKEN = тут указывается токен вашего телеграм бота [Иснтрукция по получению](https://way23.ru/регистрация-бота-в-telegram.html)
- TGM_ID = Указываем ID канала, с которого нужно пересылать сообщения
- VK_GROUP_ID = id вашей группы VK
- VK_TOKEN = Acces токен(VK Admin), который мы получаем тут https://vkhost.github.io/
# Запуск
## Запускается коммандой
```Shell
python3 tg_bot.py
```
# Установка и запуск с Docker
- Скачать репозиторий проекта:
```shell
git clone https://github.com/Aratx/tg_to_vk_transfer_posts
```
- Установите Докер, инструкция по [ссылке](https://docs.docker.com/desktop/install/linux-install/)
- Поместите заполненный файл `.env` в основную директорию
-  Запустите комманду
```Shell
docker-compose up
```
# Автоматическое включение приложения на Linux
- Переносите файл `tg_bot.service` в каталог `systemd` путь: `etc/systemd/system`
- Прописываем его в системе:
```Shell
systemctl enable tg_bot
```
- Запускаем
```Shell
systemctl start tg_bot
```
- Проверяем статус:
```Shell
systemctl -l status tg_bot
```
# Работа бота:
- Добавляете бота в Telegram канал с правами администратора
- Пишите пост в Telegram канале
- Ваш пост автоматически перемещается в указанную в файле `.env` группу VK, на стену

