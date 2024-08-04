import fitz 
from PIL import Image
import numpy as np
import io
import logging
import yaml
import os
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CommandHandler

def convert_image_to_dark_theme(image):
    # Определяем цвета
    background_color = np.array([51, 51, 51])  # rgb(51, 51, 51)
    text_color = np.array([74, 190, 210])      # rgb(74, 190, 210)

    img_array = np.array(image)
    brightness = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
    inverted_brightness = 255 - brightness

    # Создаем новое изображение с заданным фоном
    custom_img = np.full_like(img_array, background_color)
    threshold = 30
    for i in range(3):
        custom_img[..., i] = np.where(inverted_brightness > threshold,
                                      background_color[i] + (text_color[i] - background_color[i]) * inverted_brightness / 255,
                                      background_color[i])

    return Image.fromarray(custom_img.astype('uint8'), 'RGB')
def create_custom_theme_scanned_pdf(input_path, output_path):
    pdf_document = fitz.open(input_path)
    custom_pdf = fitz.open()

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        new_page = custom_pdf.new_page(width=page.rect.width, height=page.rect.height)
        
        if page.get_pixmap().n < 4:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            custom_img = convert_image_to_dark_theme(img)
            
            img_byte_arr = io.BytesIO()
            custom_img.save(img_byte_arr, format='JPEG', quality=100)
            img_byte_arr.seek(0)
            
            new_page.insert_image(new_page.rect, stream=img_byte_arr.read())
        
        else:
            new_page.draw_rect(new_page.rect, color=(51, 51, 51), fill=(51, 51, 51))
            
            for text_block in page.get_text("dict")["blocks"]:
                if text_block["type"] == 0:
                    for line in text_block["lines"]:
                        for span in line["spans"]:
                            new_page.insert_text(
                                (span["bbox"][0], span["bbox"][1]),
                                span["text"],
                                fontsize=span["size"],
                                color=(74 / 255, 190 / 255, 210 / 255),
                            )

    custom_pdf.save(output_path)
    custom_pdf.close()
    pdf_document.close()

def is_user_whitelisted(user_id, whitelist):
    return user_id in whitelist
# Функция обработки документа
async def handle_document(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not is_user_whitelisted(user_id, context.bot_data['whitelist']):
        await update.message.reply_text(f'Ваш ID ({user_id}) не в белом списке.')
        return
    await update.message.reply_text('Начинаю обработку...')
    file = update.message.document
    file_id = file.file_id
    file_name = file.file_name
    new_file = await context.bot.get_file(file_id)
    
    input_path = f'tmp/{user_id}_{file_id}.pdf'
    output_path = f'tmp/{file_name}'

    await new_file.download_to_drive(input_path)
    
    create_custom_theme_scanned_pdf(input_path, output_path)
    
    with open(output_path, 'rb') as f:
        await update.message.reply_document(document=InputFile(f, filename=output_path))

    os.remove(output_path)

async def add_to_whitelist(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not is_user_whitelisted(user_id, context.bot_data['admins']):
        await update.message.reply_text('У вас нет прав для выполнения этой команды.')
        return

    if context.args:
        new_user_id = int(context.args[0])
        if new_user_id not in context.bot_data['whitelist']:
            context.bot_data['whitelist'].append(new_user_id)
            with open('config.yaml', 'w') as file:
                yaml.safe_dump({'telegram': {'token': context.bot_data['token'], 'whitelist': context.bot_data['whitelist'], 'admins': context.bot_data['admins']}}, file)
            await update.message.reply_text(f'Пользователь {new_user_id} добавлен в белый список.')
        else:
            await update.message.reply_text(f'Пользователь {new_user_id} уже в белом списке.')
    else:
        await update.message.reply_text('Пожалуйста, укажите ID пользователя.')

# Команда для удаления пользователя из белого списка
async def remove_from_whitelist(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not is_user_whitelisted(user_id, context.bot_data['admins']):
        await update.message.reply_text('У вас нет прав для выполнения этой команды.')
        return

    if context.args:
        remove_user_id = int(context.args[0])
        if remove_user_id in context.bot_data['whitelist']:
            context.bot_data['whitelist'].remove(remove_user_id)
            with open('config.yaml', 'w') as file:
                yaml.safe_dump({'telegram': {'token': context.bot_data['token'], 'whitelist': context.bot_data['whitelist'], 'admins': context.bot_data['admins']}}, file)
            await update.message.reply_text(f'Пользователь {remove_user_id} удалён из белого списка.')
        else:
            await update.message.reply_text(f'Пользователь {remove_user_id} не найден в белом списке.')
    else:
        await update.message.reply_text('Пожалуйста, укажите ID пользователя.')

async def start_message(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Добро пожайловать в бота, который полностью сгенерила сетка. С тебя pdf, с меня перенос ее на темную сторону 😈')

if not os.path.exists("tmp/"):
    # Если папка не существует, создаем ее
    os.makedirs("tmp/")

# Основная функция для запуска бота
def main() -> None:
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    # Чтение конфигурации из файла YAML
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        token = config['telegram']['token']
        whitelist = config['telegram']['whitelist']
        admins = config['telegram']['admins']
    
    # Создайте объект `Application` и передайте токен
    application = Application.builder().token(token).build()
    
    # Зарегистрируйте обработчики
    application.bot_data['token'] = token
    application.bot_data['whitelist'] = whitelist
    application.bot_data['admins'] = admins
    
    # Зарегистрируйте обработчики
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CommandHandler('addu', add_to_whitelist))
    application.add_handler(CommandHandler('delu', remove_from_whitelist))
    application.add_handler(CommandHandler('start', start_message))
    
    # Запустите бота
    application.run_polling()

if __name__ == '__main__':
    main()
