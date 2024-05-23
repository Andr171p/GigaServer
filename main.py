import telebot
from telebot import types
import time
import requests
from langchain.memory import ConversationBufferMemory
from telegram_bot.auth_token import bot_token
from telegram_bot.bot.message_interface import MessageView
from llm.model.giga_chat import GiGaChatBot
from llm.prompt.template import join_prompt
from telegram_bot.config import get_feedback_access_id
from database.manage import db_add_user_info, db_add_comments, check_user_id_exists, get_db_data_to_array

# create telegram bot:
bot = telebot.TeleBot(bot_token)

# user menu memory:
user_menu = {}

# user conversation history:
user_conversation = {}

# create giga-chat bot:
giga_chat_bot = GiGaChatBot()
giga_chat_bot.create_giga_model()

# init prompts dict:
prompts = join_prompt(
    system_path=r"/app/llm/prompt/system/strana_development.txt",
    user_directory_path=r"/app/llm/prompt/user"
)


# init message interface:
message_view = MessageView()


@bot.message_handler(commands=['start'])
def start(message):
    # create main menu:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info_button = types.KeyboardButton("Инструкция")
    roles_button = types.KeyboardButton("Специалисты")
    feedback_button = types.KeyboardButton("Обратная связь")
    markup.add(info_button, roles_button, feedback_button)

    bot.send_message(message.chat.id, message_view.start_message, reply_markup=markup,
                     parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Инструкция')
def about_project(message):
    bot.send_message(message.chat.id, message_view.info_message, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Назад ↩')
def back_to_main_menu(message):
    bot.send_message(message.chat.id, message_view.back_message)
    start(message)


@bot.message_handler(func=lambda message: message.text == 'Обратная связь')
def feedback_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    comments_button = types.KeyboardButton("Оставить отзыв")
    # stars_button = types.KeyboardButton("Поставить оценку")
    comments_view_button = types.KeyboardButton("Смотреть комментарии")
    back_button = types.KeyboardButton("Назад ↩")
    # check user_id for view comments access:
    access_id = get_feedback_access_id()
    if message.from_user.id in access_id:
        markup.add(comments_button, comments_view_button, back_button)
    else:
        markup.add(comments_button, back_button)

    bot.send_message(message.chat.id, "Здесь вы можете предложить свои идеи по улучшению проекта, \n"
                                      "а также поставить оценку нашему проекту", reply_markup=markup)
    user_menu[message.chat.id] = "main"

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_surname = message.from_user.last_name
    username = message.from_user.username

    if not check_user_id_exists(user_id=user_id):
        db_add_user_info(
            user_id=user_id,
            user_name=user_name,
            user_surname=user_surname,
            username=username
        )


@bot.message_handler(func=lambda message: message.text == 'Смотреть комментарии')
def view_comments(message):
    comments_data = get_db_data_to_array()
    for row in comments_data:
        time.sleep(3)
        bot.send_message(message.chat.id, f"Пользователь: {row[0]}\n"
                                          f"Комментарий: {row[1]}\n")


@bot.message_handler(func=lambda message: message.text == 'Оставить отзыв')
def write_comment(message):
    bot.send_message(message.chat.id, "Мы будем рады каждому оставленному отзыву")
    bot.register_next_step_handler(message, save_comment)


def save_comment(message):
    user_id = message.chat.id
    db_add_comments(
        user_id=user_id,
        user_comment=message.text
    )
    bot.send_message(user_id, "Благодарим за оставленный отзыв")


'''@bot.message_handler(func=lambda message: message.text == 'Поставить оценку')
def stars_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    star_1_button = types.KeyboardButton("1")
    star_2_button = types.KeyboardButton("2")
    star_3_button = types.KeyboardButton("3")
    star_4_button = types.KeyboardButton("4")
    star_5_button = types.KeyboardButton("5")
    back_button = types.KeyboardButton("Назад ↩")
    markup.add(star_1_button, star_2_button, star_3_button, star_4_button, star_5_button, back_button)
    bot.send_message(message.chat.id, "Мы будем очень рады вашей оценке", reply_markup=markup)
    user_menu[message.chat.id] = "main"'''


'''@bot.message_handler(regexp=r"\d+")
def give_stars_mark(message):
    user_id = message.from_user.id
    try:
        count_stars = int(message.text)
        db_add_mark(
            user_id=user_id,
            user_mark=count_stars
        )
        bot.send_message(message.chat.id, "Благодарим за оставленную оценку")
    except Exception as _ex:
        print(_ex)
        bot.send_message(message.chat.id, "Вы должны ввести число")'''


@bot.message_handler(func=lambda message: message.text == 'Специалисты')
def giga_chats_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    copywriter_button = types.KeyboardButton("Копирайтер 📝")
    smm_button = types.KeyboardButton("Рерайтер 🖋️")
    redactor_button = types.KeyboardButton("Редактор 📖")
    email_button = types.KeyboardButton("Рассылка писем 📩")
    corrector_button = types.KeyboardButton("Корректор 📑")
    back_button = types.KeyboardButton("Назад ↩")
    markup.add(copywriter_button, smm_button, back_button, redactor_button, email_button, corrector_button)

    bot.send_message(message.chat.id, "Выберите специалиста:", reply_markup=markup)
    user_menu[message.chat.id] = "main"


@bot.message_handler(func=lambda message: message.text == 'Копирайтер 📝')
def create_copywriter_chat(message):
    giga_chat_bot.add_system_message(prompts["copywriter"])
    bot.send_message(message.chat.id, message_view.copywriter_message)


@bot.message_handler(func=lambda message: message.text == 'Рерайтер 🖋️')
def create_rewriter_chat(message):
    giga_chat_bot.add_system_message(prompts["rewriter"])
    bot.send_message(message.chat.id, message_view.rewriter_message)


@bot.message_handler(func=lambda message: message.text == 'Редактор 📖')
def create_redactor_chat(message):
    giga_chat_bot.add_system_message(prompts["redactor"])
    bot.send_message(message.chat.id, message_view.redactor_message)


@bot.message_handler(func=lambda message: message.text == 'Корректор 📑')
def create_corrector_chat(message):
    giga_chat_bot.add_system_message(prompts["corrector"])
    bot.send_message(message.chat.id, message_view.corrector_message)


@bot.message_handler(func=lambda message: message.text == 'Рассылка писем 📩')
def create_email_chat(message):
    giga_chat_bot.add_system_message(prompts["email"])
    bot.send_message(message.chat.id, message_view.email_message)


@bot.message_handler(func=lambda message: True)
def giga_answer(message):
    try:
        user_id = message.chat.id
        if user_id not in user_conversation:
            user_conversation[user_id] = ConversationBufferMemory()

        giga_chat_bot.conversation.memory = user_conversation[user_id]

        response = giga_chat_bot.giga_dialog(user_message=message.text)
        bot.send_message(user_id, response)
        # bot.send_message(user_id, giga_chat_bot.conversation.memory.chat_memory.messages[-1].content)
        time.sleep(2)
    except Exception as _ex:
        print(f"[def giga_answer]:\n"
              f"{_ex}")
        bot.send_message(message.chat.id, message_view.error_message)


@bot.message_handler(content_types=['document'])
def giga_document_answer(message):
    try:
        if 'txt' == message.document.file_name.split('.')[1]:
            file_info = bot.get_file(message.document.file_id)
            file_path = f"https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}"
            response = requests.get(file_path)
            text = response.text
            query = f"{message_view.redactor_txt_task_message}{text}"

            giga_response = giga_chat_bot.giga_dialog(user_message=query)

            bot.send_message(message.chat.id, giga_response)
    except Exception as _ex:
        print(f"[def giga_document_answer(message)] : \n"
              f"{_ex}")
        bot.send_message(message.chat.id, "Что то пошло не так")


bot.polling(none_stop=True)

