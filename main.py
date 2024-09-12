from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

BOT_TOKEN = '6954004997:AAFwnaJn6wyE6qx6vJ6_bFYZlgs1IF0oRfs'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()
#словарь для сохранения прогресса польз-ля
user_data = {}

regular_btn = KeyboardButton(
    text='\U0001F4CB Пройти опрос'
)
quiz_btn = KeyboardButton(
    text='\U0001F9E0 Пройти викторину'
)

# Добавляем кнопки в билдер
kb_builder.row(
    regular_btn,
    quiz_btn,
    width=3
)

# Создаем объект клавиатуры
keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
    resize_keyboard=True,
    input_field_placeholder='Нажмите кнопку "\U0001F4CB Пройти опрос" или "\U0001F9E0 Пройти викторину"',
    one_time_keyboard=True #исчезает после выбора
)
# опросник и варианты ответов
polls = [
    {"question": "Любите ли Вы учиться в БГИТУ?", "options": ["\U0001F44D Конечно да!", "\U0001F928 А есть другой ответ?"], "type": "regular"},
    {"question": "Ваш любимый цвет?", "options": ["\U0001F534 Красный", "\U0001F7E9 Зелёный", "\U0001F537 Синий", "\U0001F534 \U0001F7E9 \U0001F537 Мне нравятся все цвета, поэтому RGB"], "type": "regular"},
    {"question": "Ваш любимый фильм?", "options": ["Я фильмы не смотрю(", "Интерстеллар", "Начало (2010)", "Другое"], "type": "regular"}
]

# вопросы викторины, варианты ответов и правильные ответы
quizzes = [
    {"question": "Решите несложный пример: ((sqrt(-18*cos(8.199))-pow(9.888,8.199))/tan(5*3.111))*(sqrt(11*8.199-3));", "options": ["Чё? \U0001F928", "0", "8.73237e+09"], "correct_option_id": 2},
    {"question": "Столица России?", "options": ["Москва", "Париж", "Берлин"], "correct_option_id": 0},
    {"question": "Какая планета ближе всего к Солнцу?", "options": ["Земля", "Марс", "Меркурий"], "correct_option_id": 2}
]

# Команда /start
@dp.message(Command(commands='start'))
async def process_placeholder_command(message: Message):
    await message.answer(
        text='Привет! Что Вы хотите пройти: опрос или викторину?',
        reply_markup=keyboard
    )

# Обработчик кнопки "Пройти опрос"
@dp.message(lambda message: message.text == '\U0001F4CB Пройти опрос')
async def start_regular(message: Message):
    user_data[message.from_user.id] = {"regular_step": 0}
    await regular_question(message)

async def regular_question(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["regular_step"]
    poll = polls[step]
    kb_builder = ReplyKeyboardBuilder()
    for option in poll["options"]:
        kb_builder.button(text=option)
    keyboard = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(
        poll["question"],
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text in [option for poll in polls for option in poll["options"]])
async def handle_regular_answer(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["regular_step"]
    user_data[user_id].setdefault("regular_answers", []).append(message.text)

    if step + 1 < len(polls):
        user_data[user_id]["regular_step"] += 1
        await regular_question(message)
    else:
        await message.answer("Ваш ответ записан. Спасибо за участие в опросе! :)", reply_markup=keyboard)

# Обработчик кнопки "Пройти викторину"
@dp.message(lambda message: message.text == '\U0001F9E0 Пройти викторину')
async def start_quiz(message: Message):
    user_data[message.from_user.id] = {"quiz_step": 0}
    await quiz_question(message)

async def quiz_question(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["quiz_step"]
    quiz = quizzes[step]
    kb_builder = ReplyKeyboardBuilder()
    for option in quiz["options"]:
        kb_builder.button(text=option)
    keyboard = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(quiz["question"], reply_markup=keyboard)

@dp.message(lambda message: message.text in [option for quiz in quizzes for option in quiz["options"]])
async def handle_quiz_answer(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["quiz_step"]
    quiz = quizzes[step]
    correct_option = quiz["options"][quiz["correct_option_id"]]

    if message.text == correct_option:
        await message.answer("Правильно \U0001F913")
    else:
        await message.answer(f"Неправильно \U0001F644 \nПравильный ответ: {correct_option}")

    if step + 1 < len(quizzes):
        user_data[user_id]["quiz_step"] += 1
        await quiz_question(message)
    else:
        await message.answer("Викторина окончена! Надеюсь вопросы были интересные ;)", reply_markup=keyboard)


if __name__ == '__main__':
    dp.run_polling(bot)