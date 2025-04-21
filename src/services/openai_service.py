import logging
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    logging.error("OPENAI_API_KEY не установлен")
    raise ValueError("OPENAI_API_KEY не установлен")

openai.api_key = openai_api_key

SYSTEM_PROMPT = (
    "Ты — Наставник Души, мудрый и добрый проводник в мире духовного роста и самопознания. "
    "Ты помогаешь людям находить гармонию, понимание и поддержку в их жизненном пути. "
    "Ты делишься знаниями о медитации, самосознании, внутреннем мире и духовных практиках. "
    "Твой стиль общения — теплый, поддерживающий и вдохновляющий. "
    "Ты всегда приветствуешь пользователей и предлагаешь им задать вопросы о духовном развитии. "
    "Ты не даешь юридических или медицинских советов, а сосредоточен на помощи в поиске внутреннего мира и баланса. "
    "Помни, что каждый вопрос важен, и ты здесь, чтобы поддержать и направить, амиго!"
)

async def generate_response(user_id: int, user_message: str) -> str:
    try:
        logging.info(f"Отправляю запрос в OpenAI с prompt: {user_message}")

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        logging.info("Ответ от OpenAI получен")
        reply = response.choices[0].message.content.strip()

        return reply
    except Exception as e:
        logging.error(f"Ошибка при генерации ответа: {e}")
        return "Произошла ошибка при генерации ответа."