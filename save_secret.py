from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeVideo,
    PeerUser,
)
from telethon.tl import types
from telethon.extensions import markdown
import mimetypes
from userbot import client

info = {'category': 'tools', 'pattern': "", 'description': ''}

@client.on(events.NewMessage(incoming=True))
async def save_secret(event):
    message = event.message

    # Check if the message contains media that is either a photo or a document
    if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
        
        # For Document types, we'll also check if it's a video
        if isinstance(message.media, MessageMediaDocument):
            if not any(isinstance(attr, DocumentAttributeVideo) for attr in message.media.document.attributes):
                return

        # Check if the message is from a private chat (PeerUser), is not sent by the bot, 
        # and has a TTL (meaning it's from a secret chat)
        if isinstance(message.peer_id, PeerUser) and not message.out and message.media.ttl_seconds is not None:
            sender = await event.get_sender()
            text = (
                f"<emoji id=5345809986465309859>🤫</emoji><b>Новое секретное сообщение</b>\n"
                f"<b>От</b> {sender.first_name} - "
                f'<a href="tg://user?id={sender.id}">{sender.id}</a>\n\n'
                f'<a href="tg://openmessage?user_id={str(event.chat_id)}&message_id={message.id}">Посмотреть сообщение</a>'
            )

            # Download media into bytes
            media_bytes = await client.download_file(message.media, bytes)
            
            # Get the file extension
            file_extension = mimetypes.guess_extension(message.media.document.mime_type) if hasattr(message.media, 'document') else '.jpg'

            # Handle the media bytes as needed (example: sending to "Saved Messages")
            print('-> [save_secret] - Сохранил секретное сообщение')
            await client.send_file(entity='me', file=await client.upload_file(file=media_bytes, file_name=f"secret{file_extension}"), caption=text, video_note=True if hasattr(message.media, 'document') else False)
