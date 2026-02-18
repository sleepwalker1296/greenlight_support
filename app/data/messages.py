"""
Сценарий сообщений для тренировки.
ВАЖНО: Не менять порядок во время активной тренировки!
Индексы начинаются с 1.
"""

MESSAGES = [
    {
        "index": 1,
        "text": "Как ты узнал о GreenLight?",
        "category": "Продажи",
        "difficulty": "easy"
    },
    {
        "index": 2,
        "text": "Можно ли заключить договор на физическое лицо или только на юрлицо?",
        "category": "Договор",
        "difficulty": "easy"
    },
    {
        "index": 3,
        "text": "Действителен ли электронный договор без печати?",
        "category": "Договор",
        "difficulty": "medium"
    },
    {
        "index": 4,
        "text": "Как проверить полномочия вашей компании и подписанта?",
        "category": "Договор",
        "difficulty": "medium"
    },
    {
        "index": 5,
        "text": "Можно ли изменить условия договора после подписания?",
        "category": "Договор",
        "difficulty": "medium"
    },
    {
        "index": 6,
        "text": "Работаете ли вы официально, есть ли договор?",
        "category": "Доверие",
        "difficulty": "medium"
    },
    {
        "index": 7,
        "text": "Как быть уверенным, что ваша компания надежная и официальная?",
        "category": "Доверие",
        "difficulty": "medium"
    },
    {
        "index": 8,
        "text": "Как вы защищаете мои данные и доход?",
        "category": "Доверие",
        "difficulty": "medium"
    },
    {
        "index": 9,
        "text": "Как быстро менеджер отвечает на мои вопросы?",
        "category": "Поддержка",
        "difficulty": "easy"
    },
    {
        "index": 10,
        "text": "Есть ли поддержка после подключения?",
        "category": "Поддержка",
        "difficulty": "easy"
    },
    {
        "index": 11,
        "text": "Что делать, если мой канал не подходит после проверки?",
        "category": "Требования",
        "difficulty": "medium"
    },
    {
        "index": 12,
        "text": "Как проходит проверка канала перед подключением монетизации?",
        "category": "Подключение",
        "difficulty": "easy"
    },
    {
        "index": 13,
        "text": "Нужно ли использовать только авторский контент?",
        "category": "Требования",
        "difficulty": "easy"
    },
    {
        "index": 14,
        "text": "Можно ли начать с нового канала и сразу на личный тариф?",
        "category": "Тарифы",
        "difficulty": "medium"
    },
    {
        "index": 15,
        "text": "Можно ли масштабировать и подключить дополнительные каналы позже?",
        "category": "Тарифы",
        "difficulty": "easy"
    },
    {
        "index": 16,
        "text": "Можно ли подключить несколько каналов к одному AdSense — это разрешено?",
        "category": "Подключение",
        "difficulty": "medium"
    },
    {
        "index": 17,
        "text": "Как у вас сейчас с демонетами? Много адиков отлетело?",
        "category": "Риски",
        "difficulty": "medium"
    },
    {
        "index": 18,
        "text": "Если Google снова изменит правила, что будет?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 19,
        "text": "Какие риски при подключении без паспортных данных?",
        "category": "Риски",
        "difficulty": "medium"
    },
    {
        "index": 20,
        "text": "А зачем вам доступ менеджера к каналу, я не хочу выдавать?",
        "category": "Доверие",
        "difficulty": "hard"
    },
    {
        "index": 21,
        "text": "Что будет, если один канал отлетит на групповом AdSense?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 22,
        "text": "Что делать, если доход меньше минимального оборота?",
        "category": "Выплаты",
        "difficulty": "medium"
    },
    {
        "index": 23,
        "text": "Если доход меньше $200, есть ли смысл подключаться?",
        "category": "Выплаты",
        "difficulty": "medium"
    },
    {
        "index": 24,
        "text": "Почему при маленьком доходе комиссия выше?",
        "category": "Выплаты",
        "difficulty": "medium"
    },
    {
        "index": 25,
        "text": "Можно ли оплатить подключение позже или списать с дохода?",
        "category": "Выплаты",
        "difficulty": "medium"
    },
    {
        "index": 26,
        "text": "Можно ли вернуть депозит, если что-то пойдёт не так?",
        "category": "Выплаты",
        "difficulty": "hard"
    },
    {
        "index": 27,
        "text": "Как быстро вы реагируете, если выплаты задерживаются?",
        "category": "Выплаты",
        "difficulty": "medium"
    },
    {
        "index": 28,
        "text": "А если возникнут задержки, кто отвечает и можно ли получить компенсацию?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 29,
        "text": "Можно ли сэкономить на комиссии, если привожу других клиентов?",
        "category": "Условия",
        "difficulty": "easy"
    },
    {
        "index": 30,
        "text": "Есть ли партнёрская программа или кешбек за друзей?",
        "category": "Условия",
        "difficulty": "easy"
    },
    {
        "index": 31,
        "text": "Если я привожу друзей — есть ли скидка или партнёрка?",
        "category": "Условия",
        "difficulty": "easy"
    },
    {
        "index": 32,
        "text": "Чем вы отличаетесь от других похожих сервисов?",
        "category": "Доверие",
        "difficulty": "medium"
    },
    {
        "index": 33,
        "text": "Сравнивал ли ты нас с другими?",
        "category": "Доверие",
        "difficulty": "medium"
    },
    {
        "index": 34,
        "text": "Почему условия менялись несколько раз?",
        "category": "Жалоба",
        "difficulty": "hard"
    },
    {
        "index": 35,
        "text": "Мне нужно подключение без риска вообще. Это возможно?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 36,
        "text": "Что будет, если AdSense заблокируют после подключения?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 37,
        "text": "Кто несёт ответственность в случае проблем с YouTube?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 38,
        "text": "Можно ли перейти на премиум без проблем после стандарта?",
        "category": "Тарифы",
        "difficulty": "easy"
    },
    {
        "index": 39,
        "text": "Можно ли заключить договор SLA / условия VIP?",
        "category": "Договор",
        "difficulty": "medium"
    },
    {
        "index": 40,
        "text": "VIP тариф — что это и кому подходит?",
        "category": "Тарифы",
        "difficulty": "easy"
    },
    {
        "index": 41,
        "text": "Какие страны лучше подходят для регистрации AdSense сейчас?",
        "category": "Требования",
        "difficulty": "medium"
    },
    {
        "index": 42,
        "text": "Подскажите: можно ли начать работать с вами прямо сегодня?",
        "category": "Подключение",
        "difficulty": "easy"
    },
    {
        "index": 43,
        "text": "Что будет, если появятся страйки/жалобы — ваши действия и мои?",
        "category": "Риски",
        "difficulty": "hard"
    },
    {
        "index": 44,
        "text": "Дайте финальный статус по кейсу: что сделано / что дальше / когда следующий апдейт?",
        "category": "Статус",
        "difficulty": "hard"
    },
    {
        "index": 45,
        "text": "Если я откажусь — что с моими деньгами/депозитом?",
        "category": "Выплаты",
        "difficulty": "hard"
    },
]

def get_all_messages():
    """Возвращает все сообщения сценария"""
    return MESSAGES

def get_message_by_index(index: int):
    """Возвращает сообщение по индексу"""
    for msg in MESSAGES:
        if msg["index"] == index:
            return msg
    return None

def get_total_messages_count():
    """Возвращает общее количество сообщений"""
    return len(MESSAGES)
