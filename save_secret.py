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

class CustomMarkdown:
    @staticmethod
    def parse(text):
        """
        A static method to parse the given text and return the parsed text with entities.
        :param text: The text to be parsed.
        :return: The parsed text and entities.
        """
        text, entities = markdown.parse(text)
        for i, e in enumerate(entities):
            if isinstance(e, types.MessageEntityTextUrl):
                if e.url == 'spoiler':
                    entities[i] = types.MessageEntitySpoiler(e.offset, e.length)
                elif e.url.startswith('emoji/'):
                    entities[i] = types.MessageEntityCustomEmoji(e.offset, e.length, int(e.url.split('/')[1]))
        return text, entities
    @staticmethod
    def unparse(text, entities):
        """
        Returns the unparsed text with updated entities. 

        Args:
            text: The input text to be unparsed.
            entities: List of entities to be updated.

        Returns:
            The unparsed text with updated entities.
        """
        for i, e in enumerate(entities or []):
            if isinstance(e, types.MessageEntityCustomEmoji):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, f'emoji/{e.document_id}')
            if isinstance(e, types.MessageEntitySpoiler):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, 'spoiler')
        return markdown.unparse(text, entities)

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
                f"[🤫](emoji/5345809986465309859)**Новое секретное сообщение**\n"
                f"**От** {sender.first_name} -"
                f" [{sender.id}](tg://user?id={sender.id}) \n\n"
                f"[Посмотреть сообщение](tg://openmessage?user_id={str(event.chat_id)}"
                f"&message_id={message.id})\n"
            )

            # Download media into bytes
            media_bytes = await client.download_file(message.media, bytes)
            
            # Get the file extension
            file_extension = mimetypes.guess_extension(message.media.document.mime_type) if hasattr(message.media, 'document') else '.jpg'

            # Handle the media bytes as needed (example: sending to "Saved Messages")
            print('-> [save_secret] - Сохранил секретное сообщение')
            await client.send_file(entity='me', file=await client.upload_file(file=media_bytes, file_name=f"secret{file_extension}"), caption=text, video_note=True if hasattr(message.media, 'document') else False, parse_mode=CustomMarkdown())
