import logging
import re

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Set up logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

logging.basicConfig(level=logging.DEBUG)

# Set up bot and dispatcher
bot = Bot(token="5198363111:AAH4LZHDvGjL1S_vLLGLsStxud4gksLscoA")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=MemoryStorage())


async def varianti_otvetov(x):
    state = dp.current_state(user=x)
    user_data = await state.get_data()
    return user_data['varianti_otvetov']


class MyStates(StatesGroup):
    STATE1 = State()
    STATE2 = State()
    STATE3 = State()
    STATE4 = State()
    STATE5 = State()
    # Add more states as needed


# Handler for /start command
@dp.message_handler(commands=['start'], state="*")
async def start_command_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    # Ask for access code
    del_link = await message.answer("Добрый день, коллега!\n\n"
                                    "Для того, чтобы получить доступ ко всем обучениям, бонусам и фишкам этого бота необходимо поделиться с ним информацией о себе.\n\n"
                                    "Для начала пришлите свое ФИО.")
    # Set the state to "awaiting_access_code"
    await MyStates.STATE1.set()
    await state.update_data(del_link=del_link, parent_back='start')


# Блок регистрации пользователя
# Обработка ФИО
@dp.message_handler(state=MyStates.STATE1, regexp=r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+$')
async def start_command_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    await bot.delete_message(message.chat.id, user_data['del_link']["message_id"])
    fio = re.findall(r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+$', message.text)
    # Ask for access code
    del_link = await message.answer(fio[0] + "\n\nПришлите Ваш город")
    # Set the state to "awaiting_access_code"
    await MyStates.STATE2.set()
    await state.update_data(del_link=del_link, parent_back='start', fio=fio)


@dp.message_handler(state=MyStates.STATE2)
async def start_command_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    await bot.delete_message(message.chat.id, user_data['del_link']["message_id"])
    del_link = await message.answer(user_data['fio'][0] + f"\n{message.text}" + "\n\nПришлите номер телефона")
    # Set the state to "awaiting_access_code"
    await MyStates.STATE3.set()
    await state.update_data(del_link=del_link, parent_back='start', city=message.text)


# Обработка номера телефона
@dp.message_handler(state=MyStates.STATE3, regexp=r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
async def start_command_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    await bot.delete_message(message.chat.id, user_data['del_link']["message_id"])
    mobile = re.findall(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message.text)
    # Ask for access code
    if len(mobile) < 1:
        await message.answer("Введите номер телефона в формате 79251234567")
    # Send greeting and inline buttons
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        types.InlineKeyboardButton(text="Агент", callback_data="agent"),
        types.InlineKeyboardButton(text="Руководитель", callback_data="button_2"),
        types.InlineKeyboardButton(text="Брокер", callback_data="button_3"),
        types.InlineKeyboardButton(text="Сущность 4", callback_data="button_4")
    )
    del_link = await message.answer(user_data['fio'][0] + f"\n{user_data['city']}" + f"\n{message.text}" + "\n\nВыберите роль", reply_markup=inline_keyboard)
    # Set the state to "awaiting_access_code"
    await MyStates.STATE4.set()
    await state.update_data(del_link=del_link, parent_back='start', mobile=message.text)


# Обработка роли пользователя
@dp.callback_query_handler(lambda c: c.data, state=[MyStates.STATE4, MyStates.STATE5])
async def inline_button_handler(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    user_data = await state.get_data()
    await bot.delete_message(callback_query.message.chat.id, user_data['del_link']["message_id"])
    button_text = callback_query.data
    if button_text == "agent":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Да", callback_data="yes"),
            types.InlineKeyboardButton(text="Нет", callback_data="no"),
        )
        del_link = await callback_query.message.answer("ФИО - " + user_data['fio'][0] + f"\nГород - {user_data['city']}" + "\nНомер телефона - " + user_data['mobile'] + "\nВаша роль - Агент.\n\nВсе верно?",
                                                       reply_markup=inline_keyboard)
        await state.update_data(del_link=del_link, parent_back='start')
        await MyStates.STATE5.set()
    if button_text == "yes":
        del_link = await callback_query.message.answer("Введите код доступа для своей роли")
        await state.update_data(del_link=del_link, parent_back='start')
        await MyStates.STATE5.set()


@dp.message_handler(state=MyStates.STATE5)
async def start_command_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    # Ask for access code
    text = message.text
    if text == "Агент":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Знакомство", callback_data="knowing"),
            types.InlineKeyboardButton(text="Как заработать с нами?", callback_data="earn"),
            types.InlineKeyboardButton(text="Обучение по скриптам", callback_data="education"),
            types.InlineKeyboardButton(text="Скрипт", callback_data="script"),
            types.InlineKeyboardButton(text="Наш сайт", url="https://xn--90afe6abbdn.xn--p1ai/"),
            types.InlineKeyboardButton(text="Запись на консультацию", url="https://forms.amocrm.ru/rrdxmmv"),
        )
        del_link = await message.answer("Вы добавлены в систему!", reply_markup=inline_keyboard)
        await state.reset_state()
        await state.update_data(del_link=del_link, parent_back='start')
    else:
        del_link = await message.answer("Не верный код доступа. Попробуйте еще раз, или моете вернуться в самое начало /start")


##################################################################################################################################
@dp.message_handler(commands="short")
async def start_command_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    # Ask for access code
    text = message.text
    await state.reset_state()
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        types.InlineKeyboardButton(text="Знакомство", callback_data="knowing"),
        types.InlineKeyboardButton(text="Как заработать с нами?", callback_data="earn"),
        types.InlineKeyboardButton(text="Обучение по скриптам", callback_data="education"),
        types.InlineKeyboardButton(text="Скрипт", callback_data="script"),
        types.InlineKeyboardButton(text="Наш сайт", url="https://xn--90afe6abbdn.xn--p1ai/"),
        types.InlineKeyboardButton(text="Запись на консультацию", url="https://forms.amocrm.ru/rrdxmmv"),
    )
    del_link = await message.answer("Привет коллега!", reply_markup=inline_keyboard)
    await state.update_data(del_link=del_link, parent_back='start')


# # Сохранение пользователя
# @dp.callback_query_handler(lambda c: c.data, state=MyStates.STATE5)
# async def inline_button_handler(callback_query: types.CallbackQuery):
#     state = dp.current_state(user=callback_query.from_user.id)
#     user_data = await state.get_data()
#     await bot.delete_message(callback_query.message.chat.id, user_data['del_link']["message_id"])
#     button_text = callback_query.data
#     if button_text == "yes":
#         inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
#         inline_keyboard.add(
#             types.InlineKeyboardButton(text="Знакомство", callback_data="hello"),
#             types.InlineKeyboardButton(text="Как заработать с нами?", callback_data="reffer"),
#             types.InlineKeyboardButton(text="Наш сайт", url="https://xn--90afe6abbdn.xn--p1ai/"),
#             types.InlineKeyboardButton(text="Запись на консультацию", url="https://forms.amocrm.ru/rrdxmmv"),
#         )
#         del_link = await callback_query.message.answer("Вы добавлены в систему!", reply_markup=inline_keyboard)
#         await state.update_data(del_link=del_link, parent_back='start')
#     await state.reset_state()


# Handler for text messages
@dp.message_handler(state=[MyStates.STATE1, MyStates.STATE2])
async def access_code_handler(message: types.Message, state: FSMContext):
    # Check if the access code is correct
    state = dp.current_state(user=message.from_user.id)
    user_data = await state.get_data()
    if message.text == "Agento":
        # Send greeting and inline buttons
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Button 1", callback_data="button_1"),
            types.InlineKeyboardButton(text="Button 2", callback_data="button_2"),
            types.InlineKeyboardButton(text="Button 3", callback_data="button_3")
        )
        del_link = await message.answer("Welcome! Please choose an option:", reply_markup=inline_keyboard)
        await state.reset_state()
        await state.update_data(del_link=del_link, parent_back='start')

    else:
        await message.answer("Access denied. Please try again.")


# Handler for inline button callbacks
@dp.callback_query_handler(lambda c: c.data)
async def inline_button_handler(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    user_data = await state.get_data()
    await bot.delete_message(callback_query.message.chat.id, user_data['del_link']["message_id"])
    button_text = callback_query.data
    if button_text == "start":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Знакомство", callback_data="knowing"),
            types.InlineKeyboardButton(text="Как заработать с нами?", callback_data="earn"),
            types.InlineKeyboardButton(text="Обучение по скриптам", callback_data="education"),
            types.InlineKeyboardButton(text="Скрипт", callback_data="script"),
            types.InlineKeyboardButton(text="Наш сайт", url="https://xn--90afe6abbdn.xn--p1ai/"),
            types.InlineKeyboardButton(text="Запись на консультацию", url="https://forms.amocrm.ru/rrdxmmv"),
        )
        del_link = await callback_query.message.answer("Доброго дня коллега!", reply_markup=inline_keyboard)
        await state.update_data(del_link=del_link, parent_back='start')
    if button_text == "knowing":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Назад", callback_data="start")
        )
        del_link = await callback_query.message.answer("+ короткий тест\n\nhttps://www.youtube.com/watch?v=s8zBfgH2HD4", reply_markup=inline_keyboard)
        await state.update_data(del_link=del_link, parent_back='start')
    if button_text == "earn":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Назад", callback_data="start")
        )
        del_link = await callback_query.message.answer("+ короткий тест\n\nhttps://www.youtube.com/watch?v=nK7dV4iXbzI&pp=ygUS0LfQsNGA0LDQsdC-0YLQvtC6", reply_markup=inline_keyboard)
        await state.update_data(del_link=del_link, parent_back='start')
    if button_text == "education":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Назад", callback_data="start")
        )
        del_link = await callback_query.message.answer("+ короткий тест\n\nhttps://www.youtube.com/watch?v=jSnw9A0VnWA&pp=ygUQ0L7QsdGD0YfQtdC90LjQtQ%3D%3D", reply_markup=inline_keyboard)
        await state.update_data(del_link=del_link, parent_back='start')
    if button_text == "script":
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Назад", callback_data="start")
        )
        del_link = await bot.send_document(callback_query.message.chat.id, f'BQACAgIAAxkBAAImNWS4JYFWmHJMnkdQz_qsfmz03wmyAAL-LwACKjPASQSmylgU9TfLLwQ', caption='короткий текст', reply_markup=inline_keyboard)
        await state.update_data(del_link=del_link, parent_back='start')


@dp.message_handler(content_types=['photo', 'video', 'document'])
async def start_handler(message):
    # state = dp.current_state(user=message.from_user.id)
    if 'document' in message:
        print(message['caption'])
        file_id = message.document
        file_id = file_id["file_id"]
        await bot.send_document(message.from_user.id, f'{file_id}')
        await bot.send_message(message.from_user.id, f'{file_id}')
        # db.add_ID(message['message_id'], file_id, f'{message["caption"]}')
    elif 'video' in message:
        file_id = message.video
        file_id = file_id["file_id"]
        await bot.send_video(message.from_user.id, f'{file_id}')
        await bot.send_message(message.from_user.id, f'{file_id}')
        # db.add_ID(message['message_id'], file_id, f'{message["caption"]}')
    elif 'photo' in message:
        file_id = message.photo
        file_id = file_id[0]["file_id"]
        await bot.send_photo(message.from_user.id, f'{file_id}')
        await bot.send_message(message.from_user.id, f'{file_id}')
        # db.add_ID(message['message_id'], file_id, f'{message["caption"]}')


if __name__ == '__main__':
    executor.start_polling(dp)
