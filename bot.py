bot.py
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8345436392:AAGWujYDS4nBJ74gYsKmq85Jpb4SxS7BdbA"


# -------------------------------
# Identifica a loja pelo link enviado
# -------------------------------
def detectar_loja(url: str):
    if "shopee" in url:
        return "shopee"
    if "amazon" in url:
        return "amazon"
    if "aliexpress" in url:
        return "aliexpress"
    if "mercadolivre" in url:
        return "mercadolivre"
    if "shein" in url or "shein.com" in url:
        return "shein"
    return None


# -------------------------------
# Scraping simples de cupons de sites públicos
# -------------------------------
def buscar_cupons(nome_loja: str):
    fontes = [
        f"https://www.cuponomia.com.br/{nome_loja}",
        f"https://www.cuponsdesconto.com.br/{nome_loja}",
        f"https://www.cupomvalido.com.br/{nome_loja}",
    ]

    cupons = []

    for site in fontes:
        try:
            r = requests.get(site, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            botoes = soup.find_all("button")

            for b in botoes:
                txt = b.get_text(strip=True)
                if len(txt) >= 4 and len(txt) <= 12 and txt.isalnum():  # cupom provável
                    cupons.append(txt)
        except:
            pass

    cupons = list(set(cupons))

    return cupons if cupons else ["⚠️ Não encontrei cupons ativos para essa loja no momento."]


# -------------------------------
# Mensagem /start
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *Bem-vindo ao CuponsTopBot!*\n\n"
        "Me envie *qualquer link* da Shopee, Amazon, AliExpress, Mercado Livre ou Shein.\n"
        "Eu vou procurar *os melhores cupons* pra você! 🏷️💸",
        parse_mode="Markdown",
    )


# -------------------------------
# Processa qualquer link enviado
# -------------------------------
async def processar_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text
    urls = re.findall(r"(https?://[^\s]+)", mensagem)

    if not urls:
        await update.message.reply_text("Envie um *link válido* da loja 😊")
        return

    url = urls[0]
    loja = detectar_loja(url)

    if not loja:
        await update.message.reply_text("❌ Loja não reconhecida. Suporto apenas:\nShopee, Amazon, AliExpress, Mercado Livre e Shein.")
        return

    await update.message.reply_text(f"🔍 Buscando cupons para *{loja.capitalize()}*...\nAguarde alguns segundos...")

    cupons = buscar_cupons(loja)

    resposta = f"🏷️ *Cupons encontrados para {loja.capitalize()}:*\n\n"
    for c in cupons:
        resposta += f"• `{c}`\n"

    resposta += "\n💡 Dica: Teste todos — alguns são exclusivos por categoria!"

    await update.message.reply_text(resposta, parse_mode="Markdown")


# -------------------------------
# Inicializa o bot
# -------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_link))

    print("BOT RODANDO... CuponsTopBot online!")
    app.run_polling()


if __name__ == "__main__":
    main()
