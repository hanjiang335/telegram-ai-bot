import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== 最重要的两行 ====================
# 修改下面两行，填入你的真实密钥
TELEGRAM_TOKEN = "8098344875:AAHu-itF24-7usFZprZffBCRi-e47ksAEHE"      # 从 @BotFather 获取
DEEPSEEK_API_KEY = "sk-1f01731d3ed04a8ebdb6020af371c8ea"      # 从 platform.deepseek.com 获取
# ====================================================

# 以下代码不需要修改
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

conversations = {}

class AIClient:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
    
    def get_response(self, message, user_name="用户", chat_id=None):
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": "你是一个友好、乐于助人的助手，用中文回答。"},
                {"role": "user", "content": f"{user_name}说：{message}"}
            ]
            
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            result = response.json()
            
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            return "抱歉，AI服务暂时不可用。"
                
        except Exception as e:
            return f"抱歉，处理请求时出错：请稍后再试。"

ai_client = AIClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = "🤖 *智能助手已上线*\n\n我是基于DeepSeek AI的Telegram机器人！\n\n📱 *使用方法：*\n1. 私聊我直接发送消息\n2. 在群组中@我 + 你的问题\n\n试试问我：'你好'"
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "💡 *帮助*\n\n• 智能问答\n• 文本创作\n• 学习辅导\n\n使用 /new 开始新对话"
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 已开始新的对话！")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        chat_id = str(message.chat.id)
        user = message.from_user
        user_name = user.first_name or user.username or "用户"
        
        is_group = message.chat.type in ['group', 'supergroup']
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        
        should_reply = False
        user_text = ""
        
        if is_group:
            if message.text and f"@{bot_username}" in message.text:
                should_reply = True
                user_text = message.text.replace(f"@{bot_username}", "").strip()
        else:
            should_reply = True
            user_text = message.text
        
        if not should_reply or not user_text:
            return
        
        thinking_msg = await message.reply_text("💭 正在思考...")
        reply = ai_client.get_response(user_text, user_name, chat_id)
        await thinking_msg.edit_text(reply)
        
    except Exception as e:
        await update.message.reply_text("抱歉，处理消息时出错了。")

def main():
    if TELEGRAM_TOKEN == "在这里填入你的Telegram Token":
        print("❌ 错误：请先配置TELEGRAM_TOKEN")
        return
    
    if DEEPSEEK_API_KEY == "在这里填入你的DeepSeek密钥":
        print("❌ 错误：请先配置DEEPSEEK_API_KEY")
        return
    
    print("🤖 机器人启动中...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ 机器人启动成功！")
    print("📱 打开Telegram搜索你的机器人")
    app.run_polling()

if __name__ == '__main__':
    main()
