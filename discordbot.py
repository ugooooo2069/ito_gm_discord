# 本体

# 外部モジュールの読込み
from os import environ
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from logging import getLogger, StreamHandler, DEBUG
from discord import Intents, Object, Embed, Colour, errors
from discord.ext import commands
from player import Player
from ito import Ito


# ----------
# ロガー
# ----------

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


# ----------
# 定数
# ----------

# 環境変数の読込み
load_dotenv()

# BOTのアクセストークン
TOKEN = environ["TOKEN"]

# 管理者のDiscord ID
ADMIN_ID = int(environ["ADMIN_ID"])

# "marmot room"のギルドID
GUILD_ID = int(environ["GUILD_ID"])

# "ito-bot-test"のチャンネルID
CHANNEL_ID = int(environ["CHANNEL_ID"])

# ----------
# インスタンス生成
# ----------

# ゲーム
ito = Ito()

# discord.py関連
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
bot.owner_ids = [ADMIN_ID]


# ----------
# 起動時に動作する処理
# ----------


@bot.event
async def setup_hook():
    try:
        await bot.load_extension("cog")
        logger.debug("Cog loaded!")
    except errors.Forbidden:
        logger.debug("Failed to load extension")


@bot.event
async def on_ready():
    GUILD = Object(GUILD_ID)

    # スラッシュコマンドを同期
    await bot.tree.sync()
    bot.tree.copy_global_to(guild=GUILD)

    # 標準出力にログを出力
    logger.debug("Login succeeded!")
    command_set: set[commands.Command] = bot.commands
    command_list: list = [command.name for command in command_set]
    description = "\n".join(command_list)
    logger.debug(description)
    print("--------")


# --------
# Decorator
# --------


# 標準出力にログを出力
def log_wrapper(func):
    @wraps(func)
    async def decorator(*args, **kwargs):
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        logger.debug(now)
        ctx: commands.Context = args[0]
        logger.debug(f"{func.__name__} command from {ctx.author}")
        return_value = await func(*args, **kwargs)
        print("--------")
        return return_value

    return decorator


# 管理者のみ実行
def only_for_admin(func):
    @wraps(func)
    async def decorator(*args, **kwargs):
        ctx: commands.Context = args[0]

        # 管理者ではない場合エラーメッセージを送信
        if not ctx.author.id in bot.owner_ids:
            logger.debug(f"{ctx.author} is not admin")
            embed = Embed(
                title=f"{func.__name__} command is only for admin!",
                description=f"Command author: {ctx.author}\nYou don't have permission to use this command.",
                color=Colour.gold(),
            )
            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return
        return await func(*args, **kwargs)

    return decorator


# --------
# スラッシュコマンド
# --------


@bot.hybrid_command(name="neko", description="鳴きます")
@commands.guild_only()
@log_wrapper
async def neko(ctx: commands.Context):
    embed = Embed(
        title="Neko command", description="にゃ～ん", color=Colour.dark_blue()
    )
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed.set_footer(text=now)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="inu", description="鳴きます")
@commands.guild_only()
@log_wrapper
async def inu(ctx: commands.Context):
    embed = Embed(
        title=f"Inu command", description="わん", color=Colour.dark_blue()
    )
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed.set_footer(text=now)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="reload", description="コマンドをリロードします (admin only)")
@log_wrapper
@only_for_admin
async def reload(ctx: commands.Context):
    GUILD = Object(GUILD_ID)
    await bot.reload_extension("cog")
    await bot.tree.sync()
    bot.tree.copy_global_to(guild=GUILD)
    embed = Embed(
        title="Reload command",
        description="コマンドをリロードしました",
        color=Colour.dark_blue(),
    )
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed.set_footer(text=now)
    await ctx.send(embed=embed)

    command_set: set[commands.Command] = bot.commands
    command_list: list = [command.name for command in command_set]
    description = "\n".join(command_list)
    logger.debug(description)


@bot.hybrid_command(name="quit", description="botを停止します (admin only)")
@log_wrapper
@only_for_admin
async def quit(ctx: commands.Context):
    embed = Embed(
        title=f"{quit.name} command", description="ばいにゃ", color=Colour.dark_blue()
    )
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed.set_footer(text=now)
    await ctx.send(embed=embed)

    logger.debug("Logout")
    print("--------")
    await bot.close()


# ----------
# 本文
# ----------

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
