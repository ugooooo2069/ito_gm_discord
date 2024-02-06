# 本体

# 外部モジュールの読込み
from os import environ
from dotenv import load_dotenv
from logging import getLogger, StreamHandler, DEBUG
from datetime import datetime
import discord
from discord import Intents, Client, app_commands, Embed, Colour, Interaction, Guild
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
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

# ----------
# 起動時に動作する処理
# ----------


@client.event
async def on_ready():
    # チャンネルを取得
    initial_channnel = client.get_channel(CHANNEL_ID)

    # スラッシュコマンドを同期
    await tree.sync()

    # "ito-bot-test"にログイン通知
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed = Embed(title="Logged in!", description="にゃ～ん", color=Colour.dark_blue())
    embed.set_footer(text=now)
    await initial_channnel.send(embed=embed)

    # 起動したらターミナルにログイン通知が表示される
    logger.debug("Login succeeded!")
    print("--------")


# ----------
# スラッシュコマンド
# ----------


@tree.command(name="neko", description="鳴きます")
@app_commands.guild_only()
async def neko(interaction: Interaction):
    logger.debug("Neko command")
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed = Embed(title="Neko", description="にゃ～ん", color=Colour.dark_blue())
    embed.set_footer(text=now)
    await interaction.response.send_message(embed=embed)
    print("--------")


@tree.command(name="quit", description="botを停止します (admin only)")
async def quit(interaction: Interaction):
    """
    quitコマンド
    """
    # 2024/01/23 ロガーを追加

    logger.debug("Quit command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # コマンド送信者が管理者の場合はログアウト
    if interaction.user.id == ADMIN_ID:
        embed = Embed(
            title="Quit bot",
            description="ばいにゃ",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        logger.debug("Logout")
        print("--------")
        await client.close()

    # コマンド送信者が管理者以外の場合はエラーメッセージを送信
    else:
        embed = Embed(
            title="Quit command",
            description="This command is only for admin",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)

        # debug
        logger.debug("Command author is not admin: " + str(interaction.user.name))
        print("--------")
        return


@tree.command(name="set_channel", description="あそぶチャンネルを設定します")
@app_commands.guild_only()
async def set_channel(interaction: Interaction):
    """
    initializeコマンド

    サーバーを登録
    チャンネルを登録
    """

    logger.debug("set_channel command")
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # ゲーム中の場合はエラーメッセージを送信
    if ito.is_ongoing():
        embed = Embed(
            title="set_channel command",
            description="ゲーム中です",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        return

    ito.set_guild(interaction.guild)
    ito.set_channel(interaction.channel)

    embed = Embed(
        title="Initialize command",
        description="以下の情報を登録しました",
        color=Colour.dark_blue(),
    )
    embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
    embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
    players_list = ito.get_player_name_list()
    if len(players_list) == 0:
        embed.add_field(
            name="Players", value="プレイヤーが参加していません", inline=False
        )
    else:
        players = "\n".join(players_list)
        embed.add_field(name="Players", value=players, inline=False)
    embed.set_footer(text=now)
    await interaction.response.send_message(embed=embed)

    # debug
    logger.debug("Guild updated: " + str(ito.get_guild_name()))
    logger.debug("Channel updated: " + str(ito.get_channel_name()))
    print("--------")


@tree.command(name="entry", description="ゲームに参加します")
@app_commands.guild_only()
async def entry(interaction: Interaction):
    """
    entryコマンド

    サーバーIDを登録
    コマンド送信者がすでに登録されている場合はエラーメッセージを送信
    コマンド送信者がまだ登録されていない場合は登録してメッセージを送信
    """
    # 2024/01/23 ロガーを追加
    # 2024/01/22 完成？

    logger.debug("Entry command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # チャンネルIDが登録されていない場合は登録
    if ito.get_channel() == None:
        ito.set_channel(interaction.channel)
        logger.debug("Channel ID set: " + str(ito.get_channel_name()))

    # 登録されているチャンネルと異なる場合はエラーメッセージを送信
    if interaction.channel_id != ito.get_channel_id():
        embed = Embed(
            title="Entry command",
            description="以下のチャンネルが選択されています",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="Channel", value=ito.get_channel_name(), inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    author = interaction.user

    # プレイヤーがすでに登録されている場合はエラーメッセージを送信
    if author.id in ito.get_player_id_list():
        players = "\n".join(ito.get_player_name_list())
        embed = Embed(
            title="Entry command",
            description="すでに参加しています",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        embed.add_field(name="Players", value=players, inline=False)
        await interaction.response.send_message(embed=embed)

        # debug
        logger.debug(str(author.name) + " has already joined to ito game!")
        print("--------")
        return

    # ゲームが開始されている場合はエラーメッセージを送信
    if ito.is_ongoing():
        embed = Embed(
            title="Entry command",
            description="ゲーム中です",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        return

    # プレイヤーがまだ登録されていない場合
    ito.regist_player(author)

    players = "\n".join(ito.get_player_name_list())
    embed = Embed(
        title="Entry command",
        description="新しいプレイヤーが参加しました！",
        color=Colour.dark_blue(),
    )
    embed.set_footer(text=now)
    embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
    embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
    embed.add_field(name="Player", value=players, inline=False)
    await interaction.response.send_message(embed=embed)

    # debug
    logger.debug("Player count: " + str(len(ito.get_player_id_list())))

    print("--------")


@tree.command(name="exit", description="ゲームから退出します")
@app_commands.guild_only()
async def exit(interaction: Interaction):
    """
    exitコマンド

    プレイヤーを退出
    """

    # 2024/01/23 ロガーを追加

    logger.debug("Exit command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # チャンネルIDが登録されていない場合は登録
    if ito.get_channel() == None:
        ito.set_channel(interaction.channel)
        logger.debug("Channel ID set: " + str(ito.get_channel_name()))

    # 登録されているチャンネルと異なる場合はエラーメッセージを送信
    if interaction.channel_id != ito.get_channel_id():
        embed = Embed(
            title="Entry command",
            description="以下のチャンネルが選択されています",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="Channel", value=ito.get_channel_name(), inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    author = interaction.user

    # プレイヤーが参加していない場合はエラーメッセージを送信
    if author.id not in ito.get_player_id_list():
        embed = Embed(
            title="Exit command",
            description="参加していません",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # ゲームが開始されている場合はエラーメッセージを送信
    if ito.is_ongoing():
        embed = Embed(
            title="Exit command",
            description="ゲームが終了してから退出してね！",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # プレイヤーを退出
    ito.delete_player(author)

    players = "\n".join(ito.get_player_name_list())
    embed = Embed(
        title="Exit command",
        description="プレイヤーが退出しました",
        color=Colour.dark_blue(),
    )
    embed.set_footer(text=now)
    embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
    embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
    embed.add_field(name="Player", value=players, inline=False)
    await interaction.response.send_message(embed=embed)

    # debug
    logger.debug("Player count: " + str(len(ito.get_player_id_list())))

    print("--------")


@tree.command(name="life", description="ライフを設定します")
@app_commands.guild_only()
async def life(interaction: discord.Interaction, life: int):
    """
    lifeコマンド

    ライフを設定する
    """

    logger.debug("Life command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # チャンネルIDが登録されていない場合は登録
    if ito.get_channel() == None:
        ito.set_channel(interaction.channel)
        logger.debug("Channel ID set: " + str(ito.get_channel_name()))

    # 登録されているチャンネルと異なる場合はエラーメッセージを送信
    if interaction.channel_id != ito.get_channel_id():
        embed = Embed(
            title="Entry command",
            description="以下のチャンネルが選択されています",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="Channel", value=ito.get_channel_name(), inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # コマンド実行者が参加していない場合はエラーメッセージを送信
    if interaction.user.id not in ito.get_player_id_list():
        embed = Embed(
            title="Life command",
            description="最初にゲームに参加してね！",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        player_list = ito.get_player_name_list()
        if len(player_list) == 0:
            players = "プレイヤーがまだ参加していません"
        else:
            players = "\n".join(player_list)
        embed.add_field(name="Player", value=players, inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # ゲームが開始されている場合はエラーメッセージを送信
    if ito.is_ongoing():
        embed = Embed(
            title="Life command",
            description="ゲーム中です",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        return

    # 数字が1~3以外の場合はエラーメッセージを送信
    if life < 1 or 3 < life:
        embed = Embed(
            title="Life command",
            description="ライフは1~3の間で指定してね！",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        return

    ito.set_life(life)
    embed = Embed(
        title="Life command",
        description="ライフを" + str(life) + "に設定しました",
        color=Colour.dark_blue(),
    )
    embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
    embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
    player_list = ito.get_player_name_list()
    players = "\n".join(player_list)
    embed.add_field(name="Player", value=players, inline=False)
    embed.set_footer(text=now)
    await interaction.response.send_message(embed=embed)
    print("--------")

    logger.debug("Set life: " + str(ito.get_life()))

    print("--------")


@tree.command(name="theme", description="トークテーマを設定します")
@app_commands.guild_only()
async def theme(interaction: discord.Interaction, theme: str):
    """
    themeコマンド

    トークテーマを設定する
    """

    # 2024/01/23 ロガーを追加

    logger.debug("Theme command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # チャンネルIDが登録されていない場合は登録
    if ito.get_channel() == None:
        ito.set_channel(interaction.channel)
        logger.debug("Channel ID set: " + str(ito.get_channel_name()))

    # 登録されているチャンネルと異なる場合はエラーメッセージを送信
    if interaction.channel_id != ito.get_channel_id():
        embed = Embed(
            title="Entry command",
            description="以下のチャンネルが選択されています",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # コマンド送信者が参加していない場合はエラーメッセージを送信
    if interaction.user.id not in ito.get_player_id_list():
        embed = Embed(
            title="Theme command",
            description="最初にゲームに参加してね！",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        players_list = ito.get_player_name_list()
        if len(players_list) == 0:
            players = "プレイヤーがまだ参加していません"
        else:
            players = "\n".join(players_list)
        embed.add_field(name="Player", value=players, inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    ito.set_theme(theme)
    embed = Embed(
        title="Theme command",
        description="トークテーマを設定しました",
        color=Colour.dark_blue(),
    )
    embed.set_footer(text=now)
    embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
    embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
    players_list = ito.get_player_name_list()
    players = "\n".join(players_list)
    embed.add_field(name="Player", value=ito.get_player_name_list(), inline=False)
    await interaction.response.send_message(embed=embed)

    # debug
    logger.debug("Theme set: " + ito.get_theme())

    print("--------")


@tree.command(name="start", description="ゲームを開始します")
@app_commands.guild_only()
async def start(interaction: discord.Interaction):
    """
    startコマンド

    チャンネルIDを登録する
    ゲームを開始する
    """

    # 2024/01/23 ロガーを追加
    # 2024/01/22 完成？

    logger.debug("Start command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # チャンネルIDが登録されていない場合はエラーメッセージを送信
    if ito.get_channel() == None:
        embed = Embed(
            title="Start command",
            description="先にどれかのコマンドを使ってね！\n/set_channel\n/entry\n/theme",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value="登録されていません", inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # 登録されているチャンネルと異なる場合はエラーメッセージを送信
    if interaction.channel_id != ito.get_channel_id():
        embed = Embed(
            title="Entry command",
            description="以下のチャンネルが選択されています",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    players_name = ito.get_player_name_list()

    # コマンド送信者が参加していない場合はエラーメッセージを送信
    if interaction.user.id not in ito.get_player_id_list():
        embed = Embed(
            title="Start command",
            description="最初にゲームに参加してね！",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        players_name = ito.get_player_name_list()
        if len(players_name) == 0:
            players = "プレイヤーがまだ参加していません"
        else:
            players = "\n".join(players_name)
        embed.add_field(name="Player", value=players, inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # プレイヤーが2人未満の場合はエラーメッセージを送信
    if len(ito.get_player_id_list()) < 2:
        embed = Embed(
            title="Start command",
            description="2人以上でプレイしてね！",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        players_name = ito.get_player_name_list()
        if len(players_name) == 0:
            players = "プレイヤーがまだ参加していません"
        else:
            players = "\n".join(players_name)
        embed.add_field(name="Player", value=players, inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # ゲーム中の場合はエラーメッセージを送信
    if ito.is_ongoing():
        embed = Embed(
            title="Start command",
            description="ゲーム中です",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        players_name = ito.get_player_name_list()
        players = "\n".join(players_name)
        embed.add_field(name="Player", value=players, inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    await interaction.response.defer()

    # debug
    logger.debug("Game start")
    print("--------")

    # カードを生成してプレイヤーに配る
    ito.deal_cards()

    # debug
    logger.debug("Cards dealt")
    print(ito.get_deck())

    # ゲーム進行フラグをTrueにする
    ito.start_game()

    # テキストチャンネル用のEmbedを生成
    embed_channel = discord.Embed(
        title="Game start!!!", description="ゲーム情報", color=discord.Color.dark_blue()
    )
    embed_channel.add_field(
        name="チャンネル", value=ito.get_channel_name(), inline=False
    )
    embed_channel.add_field(name="ライフ", value=str(ito.get_life()), inline=False)
    embed_channel.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)

    # DM用のEmbedを生成
    embed_dm = discord.Embed(
        title="Game start!!!", description="ゲーム情報", color=discord.Color.dark_blue()
    )

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    embed_channel.set_footer(text=now)
    embed_dm.set_footer(text=now)

    # プレイヤーごとにfor文
    players: list[Player] = list(ito.get_players().values())
    for player in players:
        # テキストチャンネル用のEmbedに各プレイヤー名と手札を追加
        embed_channel.add_field(
            name=player.get_name(), value=player.hand_to_string_close(), inline=True
        )

        # DM用のEmbedを初期化
        embed_dm.clear_fields()

        # DM用のEmbedに各情報を追加
        embed_dm.add_field(
            name="チャンネル", value=ito.get_channel_name(), inline=False
        )
        embed_dm.add_field(name="ライフ", value=str(ito.get_life()), inline=False)
        embed_dm.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)

        # 各プレイヤーにDMでカードを送信
        embed_dm.add_field(
            name="カード (他の人に教えないように！)",
            value=player.hand_to_string_open(),
            inline=False,
        )
        await player.get_member().send(embed=embed_dm)

    # テキストチャンネルにゲーム情報を送信
    await interaction.followup.send(embed=embed_channel)

    # dict_embed = embed_channel.to_dict()
    # print(dict_embed)
    print("--------")


@tree.command(name="put", description="手札の中で最小のカードを場に出します")
@app_commands.guild_only()
async def put(interaction: discord.Interaction):
    """
    putコマンド

    テキストチャンネルにカードを送信する
    """

    logger.debug("Put card command")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # チャンネルが設定されていない場合はエラーメッセージを送信
    if ito.get_channel() is None:
        embed = Embed(
            title="Put card",
            description="ゲームが開始していません",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # ゲームが開始していない場合はエラーメッセージを送信
    if not ito.is_ongoing():
        embed = Embed(
            title="Put card",
            description="ゲームが開始していません",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # 登録されているチャンネル以外の場合はエラーメッセージを送信
    if interaction.channel_id != ito.get_channel_id():
        embed = Embed(
            title="Put card",
            description="以下のチャンネルが選択されています",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel_name(), inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    # コマンド送信者がゲームに参加していない場合はエラーメッセージを送信
    if interaction.user.id not in ito.get_player_id_list():
        embed = Embed(
            title="Put card",
            description="ゲームに参加していません！",
            color=Colour.dark_blue(),
        )
        players_list = ito.get_player_name_list()
        players = "\n".join(players_list)
        embed.add_field(name="Player", value=players, inline=False)
        embed.set_footer(text=now)
        await interaction.response.send_message(embed=embed)
        print("--------")
        return

    await interaction.response.defer()

    # プレイヤーを取得
    current_player: Player = ito.get_player(interaction.user.id)

    # debug
    logger.debug("Detect put command from: " + current_player.get_name())

    # プレイヤーの手札の中で最小のカードを場に出す
    card_put: int = current_player.put_card()

    players: list[Player] = list(ito.get_players().values())

    # プレイヤーが手札を持っていない場合はエラーメッセージを送信
    if card_put == None:
        embed = Embed(
            title="Put card",
            description="手札にカードがありません",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        embed.add_field(name="ライフ", value=str(ito.get_life()), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)

        # playersでfor文
        for player in players:
            embed.add_field(
                name=player.get_name(),
                value=player.hand_to_string_close(),
                inline=True,
            )
        await interaction.followup.send(embed=embed)
        print("--------")
        return

    # debug
    logger.debug("Put card: " + str(card_put))

    ito.receive_card(card_put)

    # debug
    logger.debug("Deck: " + str(ito.get_deck()))

    # 失敗した枚数をカウント
    # 初期化
    count_penalty = 0

    # 場に出されたカードが最小か判定する
    # プレイヤーの中でfor文
    for player in players:
        # 各プレイヤーの手札より小さいかチェック
        while player.has_smaller_card(card_put):
            # 手札の中に場に出されたカードよりも小さいカードがある場合
            # 手札の中で最小のカードを場に出す
            penalty = player.put_card()

            ito.receive_card(penalty)

            # ライフを減らす
            ito.decrease_life()

            # 失敗した枚数をインクリメント
            count_penalty += 1

    logger.debug("Life: " + str(ito.get_life()))
    logger.debug("Deck: " + str(ito.get_deck()))
    logger.debug("Count penalty: " + str(count_penalty))
    logger.debug("Game over: " + str(ito.is_gameover()))
    logger.debug("Game clear: " + str(ito.is_cleared()))

    # 結果をチャンネルに送信
    # ゲームオーバーの場合
    if ito.is_gameover():
        logger.debug("Game over")

        embed = Embed(
            title="Game over",
            description="小さいカードを場に出しました\nライフが0になりました\nゲームを終了します",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="ライフ", value="0", inline=False)
        embed.set_footer(text=now)

        # プレイヤーごとにfor文
        for player in players:
            embed.add_field(
                name=player.get_name(), value=player.hand_to_string_open(), inline=True
            )

        # Embedを送信
        await interaction.followup.send(embed=embed)

        # ゲームを初期化する
        ito.initialize_game()

        print("--------")

        return

    # クリアの場合
    if ito.is_cleared():
        logger.debug("Game clear")

        embed = Embed(
            title="Game clear",
            description="ゲームをクリアしました！\nゲームを終了します",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="ライフ", value=str(ito.get_life()), inline=False)
        embed.set_footer(text=now)

        # プレイヤーごとにfor文
        for player in players:
            embed.add_field(
                name=player.get_name(), value=player.hand_to_string_open(), inline=True
            )

        # Embedを送信
        await interaction.followup.send(embed=embed)

        # ゲームを初期化する
        ito.initialize_game()

        print("--------")

        return

    # 失敗した場合
    if 0 < count_penalty and count_penalty < ito.get_life():
        logger.debug("Failure")

        embed = Embed(
            title="Failure",
            description="失敗しました...\n小さいカードを場に出しました\n場に出された枚数分のライフを減らします",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="ライフ", value=str(ito.get_life()), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        embed.set_footer(text=now)

        # プレイヤーごとにfor文
        for player in players:
            embed.add_field(
                name=player.get_name(), value=player.hand_to_string_close(), inline=True
            )

        # Embedを送信
        await interaction.followup.send(embed=embed)

        print("--------")

        return

    # 成功した場合
    if count_penalty == 0:
        logger.debug("Success")

        embed = Embed(
            title="Success",
            description="成功しました！\n次に小さいカードを場に出してください",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="ライフ", value=str(ito.get_life()), inline=False)
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)

        # プレイヤーごとにfor文
        for player in players:
            embed.add_field(
                name=player.get_name(), value=player.hand_to_string_close(), inline=True
            )

        # ゲーム情報を送信
        await interaction.followup.send(embed=embed)

        print("--------")

        return


# ----------
# 本文
# ----------

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
