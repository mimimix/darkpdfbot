# Telegram Bot для создания темной темы PDF
> README, код бота и тд. полностью написал гпт. Я только контролировал и чуть поправлял...

Этот проект представляет собой Telegram бота, который преобразует PDF документы в формат с темной темой. Бот принимает PDF файлы, обрабатывает их, изменяет фон на черный, а текст делает синим. Он использует Docker для упаковки и развертывания.

## Функциональные возможности

- Преобразование PDF файлов в темную тему с черным фоном и синим текстом.
- Поддержка белого списка пользователей для ограничения доступа.
- Команды для добавления и удаления пользователей из белого списка.
- Использование Docker для упаковки и развертывания приложения.

## Установка и запуск

### Основа:

1. **Клонируйте репозиторий**

```bash
git clone --depth 1 https://github.com/mimimix/darkpdfbot
cd darkpdfbot
```

**Создайте файл конфигурации**

   Создайте файл `config.yaml` в корневом каталоге проекта и добавьте следующее содержимое:

```yaml
telegram:
  token: YOUR_TELEGRAM_BOT_TOKEN
  whitelist:
    - USER_ID_1
    - USER_ID_2
```

   Замените `YOUR_TELEGRAM_BOT_TOKEN` на токен вашего бота и добавьте идентификаторы пользователей, которые будут иметь доступ к боту.

### Лапками:
**1. Ставим зависимости**
```bash
pip install -r requirements.txt
```

**2. Запускаем**
```bash
python main.py
```
### Docker:
Варианта два:

**1. Не мучаться с билдом**
```bash
docker-compose up -d
```
**2. Мучаться с билдом**
```bash
docker-compose -f docker-compose.build.yml up -d 
```

   Это создаст Docker образ и запустит контейнер с вашим ботом.

## Использование

1. **Отправка PDF файла**

   Отправьте PDF файл вашему боту в Telegram. Бот обработает файл и вернет его с темной темой.

2. **Команды для управления белым списком**

   - `/addu USER_ID` — Добавляет пользователя в белый список.
   - `/delu USER_ID` — Удаляет пользователя из белого списка.

   Эти команды доступны только пользователям, указанным в белом списке.
