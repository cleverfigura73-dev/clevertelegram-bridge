
import os
import asyncio
import logging
import httpx

from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

SOURCE_CHANNEL = os.environ["SOURCE_CHANNEL"]
INGEST_URL = os.environ["SYNC_INGEST_URL"]
INGEST_SECRET = os.environ["SYNC_INGEST_SECRET"]

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)

async def main():
    await client.start()

    logging.info("Telegram conectado com sucesso!")
    logging.info("Monitorizando canal: %s", SOURCE_CHANNEL)

    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handle_message(event):
        message = event.message

        payload = {
            "source": SOURCE_CHANNEL,
            "chat_id": event.chat_id,
            "message_id": message.id,
            "text": message.raw_text or "",
            "date": message.date.isoformat()
        }

        headers = {
            "x-sync-secret": INGEST_SECRET,
            "Authorization": f"Bearer {INGEST_SECRET}"
        }

        try:
            async with httpx.AsyncClient(timeout=30) as http:
                response = await http.post(
                    INGEST_URL,
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()
                logging.info("Mensagem %s enviada!", message.id)

        except Exception:
            logging.exception("Erro ao enviar mensagem")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
