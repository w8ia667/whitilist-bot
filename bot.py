import discord
from discord.ext import commands
import json
import datetime
import os

# Configurações
TOKEN = 'SEU_TOKEN_AQUI'  # Você vai mudar isso depois
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='*', intents=intents)

# Planos em dias
PLANOS = {
    "vitalicio": 9999,
    "4meses": 120,
    "2meses": 60,
    "1mes": 30,
    "1semana": 7,
    "3dias": 3
}

# Arquivo da whitelist
WHITELIST_FILE = "whitelist.json"

def carregar_whitelist():
    try:
        with open(WHITELIST_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def salvar_whitelist(whitelist):
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(whitelist, f, indent=4)

def calcular_data_expiracao(dias):
    data = datetime.datetime.now() + datetime.timedelta(days=dias)
    return data.strftime("%d/%m/%Y")

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} conectado!')
    print(f'📊 Whitelist: {len(carregar_whitelist())} usuários')

@bot.command()
async def liberar(ctx, plano: str, nick_roblox: str, usuario: discord.Member = None):
    """Libera whitelist: *liberar vitalicio NickRoblox @usuario"""
    
    if plano.lower() not in PLANOS:
        await ctx.send(f"❌ Plano inválido! Use: {', '.join(PLANOS.keys())}")
        return
    
    if usuario is None:
        usuario = ctx.author
    
    whitelist = carregar_whitelist()
    
    # Verificar se já existe
    if nick_roblox in whitelist:
        await ctx.send(f"❌ {nick_roblox} já está na whitelist!")
        return
    
    # Adicionar à whitelist
    dias = PLANOS[plano.lower()]
    data_expiracao = calcular_data_expiracao(dias)
    
    whitelist[nick_roblox] = {
        "data_adicao": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "data_expiracao": data_expiracao,
        "plano": plano,
        "discord_user": str(usuario.id),
        "ativo": True
    }
    
    salvar_whitelist(whitelist)
    
    # Mensagem de confirmação
    await ctx.send(f"""
✅ **WHITELIST LIBERADA!**
👤 **Nick Roblox:** {nick_roblox}
📦 **Plano:** {plano}
⏰ **Dias:** {dias}
📅 **Expira em:** {data_expiracao}
🎮 **Discord:** {usuario.mention}
🛠️ **Staff:** {ctx.author.mention}
    """)

@bot.command()
async def verificar(ctx, nick_roblox: str):
    """Verifica whitelist: *verificar NickRoblox"""
    
    whitelist = carregar_whitelist()
    usuario = whitelist.get(nick_roblox)
    
    if usuario and usuario["ativo"]:
        await ctx.send(f"✅ {nick_roblox} está na whitelist!\nPlano: {usuario['plano']}\nExpira: {usuario['data_expiracao']}")
    else:
        await ctx.send(f"❌ {nick_roblox} NÃO está na whitelist!")

@bot.command()
async def planos(ctx):
    """Mostra planos: *planos"""
    
    mensagem = "📦 **PLANOS DISPONÍVEIS:**\n"
    for plano, dias in PLANOS.items():
        if dias == 9999:
            tempo = "Vitalício"
        else:
            tempo = f"{dias} dias"
        mensagem += f"• **{plano}** - {tempo}\n"
    
    await ctx.send(mensagem)

# Iniciar bot
bot.run(TOKEN)
