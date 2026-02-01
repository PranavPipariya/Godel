"""Telegram bot integration for Godel AI Agent."""

import os
import asyncio
import logging
from typing import Optional
from pathlib import Path

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False

from agent.orchestrator import Agent
from agent.event_types import AgentEventType
from config.configuration import Config


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for remote access to Godel AI Agent."""
    
    def __init__(self, token: str, allowed_users: list[int], config: Config):
        if not HAS_TELEGRAM:
            raise ImportError("python-telegram-bot not installed. Run: pip install python-telegram-bot")
        
        self.token = token
        self.allowed_users = set(allowed_users)
        self.config = config
        self.sessions = {}  # user_id -> (orchestrator, context_manager)
        
    def _check_auth(self, user_id: int) -> bool:
        """Check if user is authorized."""
        if not self.allowed_users:
            return True  # No restrictions if list is empty
        return user_id in self.allowed_users
    
    async def _get_or_create_session(self, user_id: int):
        """Get or create a session for a user."""
        if user_id not in self.sessions:
            config = Config()
            agent = Agent(config)
            await agent.__aenter__()
            self.sessions[user_id] = agent
        return self.sessions[user_id]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if not self._check_auth(user_id):
            await update.message.reply_text(
                f"Unauthorized. Your user ID is not in the allowed list.\nYour ID: {user_id}"
            )
            return

        await update.message.reply_text(
            "Godel AI Agent\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/clear - Clear conversation history\n"
            "/status - Show session status\n\n"
            "Send any message to interact with the agent."
        )
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if not self._check_auth(user_id):
            await update.message.reply_text("Unauthorized")
            return

        if user_id in self.sessions:
            agent = self.sessions[user_id]
            agent.session.context_manager.clear()
            await update.message.reply_text("Conversation history cleared")
        else:
            await update.message.reply_text("No active session")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if not self._check_auth(user_id):
            await update.message.reply_text("Unauthorized")
            return

        if user_id in self.sessions:
            agent = self.sessions[user_id]
            msg_count = len(agent.session.context_manager._messages)
            await update.message.reply_text(
                f"Session Active\nMessages: {msg_count}\nModel: {self.config.model_name}"
            )
        else:
            await update.message.reply_text("No active session")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if not self._check_auth(user_id):
            await update.message.reply_text("Unauthorized")
            return

        message_text = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        agent = await self._get_or_create_session(user_id)

        try:
            status_msg = await update.message.reply_text("Processing...")

            # Collect response from agent events
            response_text = ""
            async for event in agent.run(message_text):
                if event.type == AgentEventType.TEXT_DELTA:
                    response_text += event.data.get("content", "")
                elif event.type == AgentEventType.TEXT_COMPLETE:
                    response_text = event.data.get("content", response_text)

            await status_msg.edit_text(response_text or "Done")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.message:
            await update.message.reply_text("An error occurred. Please try again.")
    
    def run(self):
        logger.info("Starting Telegram bot...")
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_error_handler(self.error_handler)
        logger.info("Bot started successfully!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env file")
        return

    allowed_users_str = os.getenv("TELEGRAM_ALLOWED_USERS", "")
    allowed_users = []
    if allowed_users_str:
        try:
            allowed_users = [int(uid.strip()) for uid in allowed_users_str.split(",") if uid.strip()]
        except ValueError:
            print("Error: Invalid TELEGRAM_ALLOWED_USERS format")
            return

    if not allowed_users:
        print("Warning: No allowed users configured")

    config = Config()
    bot = TelegramBot(token, allowed_users, config)
    bot.run()


if __name__ == "__main__":
    main()
