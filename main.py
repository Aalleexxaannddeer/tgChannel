import os
import requests
import time

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

SYSTEM_PROMPT = """
Ты — элитный AI-аналитик. Твоя задача: выдать ОДИН глубокий, научно обоснованный инсайт, ломающий стереотипы о богатстве, власти или системах.
Строгие правила вывода (отвечай ТОЛЬКО в этом формате, без лишних слов, без markdown, без приветствий):

ЗАГОЛОВОК: [Интригующее название закона/парадокса]
СУТЬ: [Краткая выжимка феномена с указанием автора/теории. Максимум 3 предложения.]
ПРИМЕНЕНИЕ: [Прагматичное руководство для масштабирования капитала или эффективности.]
ВОПРОС: [Один провокационный вопрос к аудитории для комментариев.]

Тема: Стык дисциплин. Будь конкретен, используй факты.
"""

def get_ai_insight():
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Aalleexxaannddeer/tgChannel",
        "X-Title": "Telegram Auto Insights Bot"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Сгенерируй инсайт."}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            print(f"Попытка {attempt + 1} не удалась: {e}")
            if attempt < 2:
                time.sleep(5)
    return None

def format_for_telegram(raw_text):
    lines = raw_text.split('\n')
    formatted = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.upper().startswith("ЗАГОЛОВОК:"):
            formatted.append(f"<b>🧠 {line.replace('ЗАГОЛОВОК:', '').strip()}</b>\n")
        elif line.upper().startswith("СУТЬ:"):
            formatted.append(f"<b>📌 Суть факта:</b>\n{line.replace('СУТЬ:', '').strip()}\n")
        elif line.upper().startswith("ПРИМЕНЕНИЕ:") or line.upper().startswith("ПРИМЕНИТЬ:"):
            formatted.append(f"<b>⚡️ Как применить:</b>\n{line.replace('ПРИМЕНЕНИЕ:', '').replace('ПРИМЕНИТЬ:', '').strip()}\n")
        elif line.upper().startswith("ВОПРОС:"):
            formatted.append(f"<i>💬 {line.replace('ВОПРОС:', '').strip()}</i>")
        else:
            formatted.append(line)
    return "\n".join(formatted)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Успешно отправлено в Telegram!")
    else:
        print(f"❌ Ошибка Telegram: {response.text}")

if __name__ == "__main__":
    print("🔄 Запуск генерации инсайта...")
    raw_insight = get_ai_insight()
    if raw_insight:
        final_text = format_for_telegram(raw_insight)
        print("\n--- ГОТОВЫЙ ПОСТ ---\n")
        print(final_text)
        print("\n--------------------\n")
        send_to_telegram(final_text)
    else:
        print("⚠️ Не удалось получить инсайт.")
