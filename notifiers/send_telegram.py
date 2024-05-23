"""
This module contains the TelegramSender class, which is used to send Telegram messages.
"""

import os
import sys

import requests

# pylint: disable=import-error,wrong-import-position
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from .loggers import LogHelper


class TelegramSender:
    """
    This class is used to send messages to a Telegram chat using the Telegram API. You
    must supply your own API token as well as your chat ID in order to use the class. It
    provides a send_message method to send a message to the chat.

    Attributes:
        token (str): The token to use for the Telegram Bot API.
        chat_id (str): The chat ID to use for the Telegram chat.
        url (str): The URL to use for sending messages via the Telegram API.
    """

    def __init__(self, token, chat_id):
        self.logger = LogHelper.setup_logger(f"{self.__class__.__name__}")
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{self.token}"
        self.timeouts = {"sendPhoto": 30, "sendAudio": 60}
        self.default_timeout = 10

    def send_message(self, message, chat_id=None, parse_mode=None):
        """
        Send a message to a Telegram chat. Uses the chat ID and token provided during
        initialization of the class.

        Args:
            message (str): The message to send.
            chat_id (str, optional): The chat ID to send the message to if you want to override what
                the class instance uses. Defaults to None.
            parse_mode (str, optional): The parse mode to use for message formatting. Supports
                "Markdown", "MarkdownV2", or "HTML". Defaults to None, in which case parse_mode
                won't be included in the payload at all.

        Returns:
            bool: True if the message was sent successfully, False if the message failed to send.
        """
        payload = {"chat_id": chat_id or self.chat_id, "text": message}

        if parse_mode:
            payload["parse_mode"] = parse_mode

        try:
            self.call_api("sendMessage", payload)
            self.logger.info("Message sent to Telegram successfully.")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to send message to Telegram: %s", str(e))
            return False

    def send_audio_file(
        self, audio_path, chat_id=None, caption=None, duration=None, title=None, performer=None
    ):
        """
        Send a local audio file to a specified chat. Supports optional message modification and
        deletion by providing a message ID and new text. Optionally remove an attached keyboard
        after modification.

        Args:
            audio_path (str): The path of the local audio file to send.
            chat_id (str, optional): The chat ID to send the message to if you want to override what
                the class instance uses. Defaults to None.
            caption (str, optional): The new text to replace the message with, if applicable.
            duration (int, optional): Duration of the audio in seconds.
            title (str, optional): Title of the audio.
            performer (str, optional): Name of the performer (displayed under the title).
        """
        try:
            with open(audio_path, "rb") as audio_file:
                payload = {
                    "chat_id": chat_id or self.chat_id,
                    "duration": duration,
                    "title": title,
                    "performer": performer,
                    "caption": caption,
                }
                self.call_api("sendAudio", payload, files={"audio": audio_file})
            return True
        except Exception as e:
            self.logger.error("Failed to send audio file: %s", str(e))
            return False

    def call_api(self, api_method, payload=None, timeout=None, files=None):
        """
        Make a POST request to the Telegram API using the specified method, payload, and timeout.

        If timeout is not specified, it's determined dynamically based on the API method if it's a
        commonly used method, or else the default timeout is used.

        If files are provided, it uses the `data` parameter to properly handle multipart/form-data.
        Otherwise, it defaults to sending the payload as JSON. The payload is filtered to remove any
        None values before sending the request.

        Args:
            api_method (str): The API method to call.
            payload (dict, optional): The payload to send to the API. Defaults to None.
            timeout (int, optional): The timeout for the request. If None, the timeout is determined
                dynamically based on the API method if it's a commonly used method, or the default
                timeout is used. Defaults to None.
            files (dict, optional): A dictionary for multipart encoding upload. Defaults to None.
                Examples: `{"param_name": file-tuple}`, `{"param_name": file-like-object}`

        Returns:
            dict: The response data in JSON if the request is successful.

        Raises:
            Exception: If the request to the Telegram API fails.
        """
        url = f"{self.url}/{api_method}"
        payload = {k: v for k, v in payload.items() if v is not None} if payload else {}
        timeout = timeout or self.timeouts.get(api_method, self.default_timeout)

        try:
            response = (
                requests.post(url, data=payload, files=files, timeout=timeout)
                if files
                else requests.post(url, json=payload, timeout=timeout)
            )
            response_data = response.json()
            if not response_data.get("ok"):
                error_msg = response_data.get("description", "Unknown error.")
                self.logger.error("Failed to call %s: %s", api_method, error_msg)
                self.logger.debug("Code %s: %s", response.status_code, response_data)
                raise Exception(f"Failed to call {api_method}: {error_msg}")
            return response_data
        except requests.RequestException as e:
            self.logger.warning("Request to Telegram API failed: %s", str(e))
            raise Exception(f"Request to Telegram API failed: {e}") from e
