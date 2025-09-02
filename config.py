import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
REF_LINK = os.getenv('REF_LINK')
MAIN_PROMO = os.getenv('MAIN_PROMO')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

TEXTS = {
    'ru': {
        'start': "💸 Приветствуем тебя!\n\nТы попал в закрытую систему, где сливаются рабочие алгоритмы ставок на 1Win.\nВсё, что ты здесь получишь — совершенно бесплатно.\n\nСледуй инструкции ниже и получай свою прибыль!",
        'instructions': "📌 Инструкция:\n1. Перейди по ссылке и зарегистрируйся 👉 {ref_link}\n2. Введи промокод: {promo}\n3. Пополни баланс на 1000₽\n\nПосле выполнения всех шагов нажми кнопку ниже, чтобы получить алгоритм 👇",
        'not_subscribed': "❌ Вы не подписались на канал.\nПожалуйста, подпишитесь и нажмите \"Проверить подписку ✅\"",
        'help': "Ожидайте, с вами свяжется поддержка в ближайшее время.",
        'algorithm_sent': "🎰 Ваш алгоритм:"
    },
    'en': {
        'start': "💸 Welcome!\n\nYou've entered a private system where working casino algorithms are leaked.\nEverything you get here is absolutely free.\n\nFollow the instructions below and start profiting!",
        'instructions': "📌 Instructions:\n1. Click the link and register 👉 {ref_link}\n2. Enter promo code: {promo}\n3. Deposit $10\n\nAfter completing all steps, click the button below to get the algorithm 👇",
        'not_subscribed': "❌ You are not subscribed to the channel.\nPlease subscribe and click \"Check subscription ✅\"",
        'help': "Please wait, support will contact you shortly.",
        'algorithm_sent': "🎰 Your algorithm:"
    }
}