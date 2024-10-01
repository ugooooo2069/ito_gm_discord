# スラッシュコマンド


from functools import wraps
from datetime import datetime
from discord.ext import commands
from discord import Embed, Colour
from ito import Ito
from player import Player


# ----------
# ロガー
# ----------

from loguru import logger


# --------
# Cog
# --------


class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ito = Ito()

    # --------
    # Decorator
    # --------

    # 標準出力にログを出力
    def log_wrapper(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            now = datetime.now().strftime("%Y/%m/%d %H:%M")
            logger.debug(now)
            ctx: commands.Context = args[1]
            logger.debug(f"{func.__name__} command from {ctx.author}")
            return_value = await func(*args, **kwargs)
            print("--------")
            return return_value

        return decorator

    # ゲーム中のみ実行できるコマンド
    def only_in_game(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            self: MyCog = args[0]
            ito = self.ito

            # ゲームが開始されていない場合はエラーメッセージを送信
            if not ito.is_ongoing():
                embed = Embed(
                    title=f"{func.__name__} command",
                    description="ゲームが開始されていません",
                    color=Colour.gold(),
                )
                now = datetime.now().strftime("%Y/%m/%d %H:%M")
                embed.set_footer(text=now)
                ctx: commands.Context = args[1]
                await ctx.send(embed=embed)
                return

            # ゲームが開始されている場合はコマンドを実行
            return await func(*args, **kwargs)

        return decorator

    # ゲーム外のみ実行できるコマンド
    def only_off_game(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            self: MyCog = args[0]
            ito = self.ito

            # ゲームが開始されている場合はエラーメッセージを送信
            if ito.is_ongoing():
                embed = Embed(
                    title=f"{func.__name__} command",
                    description="ゲームが開始されています",
                    color=Colour.gold(),
                )
                now = datetime.now().strftime("%Y/%m/%d %H:%M")
                embed.set_footer(text=now)
                ctx: commands.Context = args[1]
                await ctx.send(embed=embed)
                return

            # ゲームが開始されていない場合はコマンドを実行
            return await func(*args, **kwargs)

        return decorator

    # プレイヤーのみ実行できるコマンド
    def only_for_player(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            self: MyCog = args[0]
            ito = self.ito
            ctx: commands.Context = args[1]

            # コマンド実行者がゲームに参加していない場合はエラーメッセージを送信
            if ctx.author.id not in ito.get_players():
                embed = Embed(
                    title=f"{func.__name__} command",
                    description="ゲームに参加してね！",
                    color=Colour.gold(),
                )
                player_list = ito.get_player_name_list()
                if len(player_list) == 0:
                    players = "プレイヤーがまだいません"
                else:
                    players = "\n".join(player_list)
                embed.add_field(name="参加者", value=players, inline=False)
                now = datetime.now().strftime("%Y/%m/%d %H:%M")
                embed.set_footer(text=now)
                await ctx.send(embed=embed)
                return

            # コマンド実行者がゲームに参加している場合はコマンドを実行
            return await func(*args, **kwargs)

        return decorator

    # 登録されているチャンネルでのみ実行できるコマンド
    def only_in_channel(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            self: MyCog = args[0]
            ito = self.ito
            ctx: commands.Context = args[1]

            # 登録されているチャンネル以外の場合はエラーメッセージを送信
            if ctx.channel.id != ito.get_channel().id:
                embed = Embed(
                    title=f"{func.__name__} command",
                    description="以下のチャンネルが選択されています",
                    color=Colour.gold(),
                )
                embed.add_field(
                    name="チャンネル", value=ito.get_channel().name, inline=False
                )
                now = datetime.now().strftime("%Y/%m/%d %H:%M")
                embed.set_footer(text=now)
                await ctx.send(embed=embed)
                return

            # 登録されているチャンネルの場合はコマンドを実行
            return await func(*args, **kwargs)

        return decorator

    # チャンネルが登録されていない場合はチャンネルを登録するコマンド
    def channel_registerd_check(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            self: MyCog = args[0]
            ito = self.ito
            ctx: commands.Context = args[1]

            if ito.get_channel() == None:
                ito.set_channel(ctx.channel)
                logger.debug(f"{ctx.author} set channel: {ctx.channel.name}")

            return await func(*args, **kwargs)

        return decorator

    # --------
    # スラッシュコマンド
    # --------

    @commands.hybrid_command(name="entry", description="ゲームに参加する")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_off_game
    async def entry(self, ctx: commands.Context):
        """
        entry command

        サーバーIDを登録する
        コマンド実行者がすでに登録されている場合はエラーメッセージを送信する
        コマンド実行者をプレイヤーに登録する
        """

        ito = self.ito

        now = datetime.now().strftime("%Y/%m/%d %H:%M")

        if ctx.author.id in ito.get_players():
            embed = Embed(
                title="Entry command",
                description="すでに登録されています",
                color=Colour.gold(),
            )
            players = "\n".join(ito.get_player_name_list())
            embed.add_field(name="参加者", value=players, inline=False)
            embed.set_footer(text=now)
            await ctx.send(embed=embed)

            logger.debug(f"{ctx.author} is already registered")
            return

        ito.regist_player(ctx.author)

        embed = Embed(
            title="Entry command",
            description="新しいプレイヤーが参加しました！",
            color=Colour.dark_blue(),
        )
        players = "\n".join(ito.get_player_name_list())
        embed.add_field(name="参加者", value=players, inline=False)
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="exit", description="ゲームから退出します")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_off_game
    @only_for_player
    async def exit(self, ctx: commands.Context):
        """
        exit command

        プレイヤーを退出
        """

        ito = self.ito
        ito.delete_player(ctx.author)

        embed = Embed(
            title="Exit command",
            description="プレイヤーが退出しました",
            color=Colour.dark_blue(),
        )
        players = "\n".join(ito.get_player_name_list())
        embed.add_field(name="参加者", value=players, inline=False)
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="start", description="ゲームを開始します")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_off_game
    @only_for_player
    async def start(self, ctx: commands.Context):
        """
        start command

        ゲームを開始
        """

        ito = self.ito

        # プレイヤーが2人未満の場合はエラーメッセージを送信
        if len(ito.get_players()) < 2:
            embed = Embed(
                title="Start command",
                description="2人以上でプレイしてね！",
                color=Colour.gold(),
            )
            if len(ito.get_players()) == 0:
                players = "プレイヤーがまだ参加していません"
            else:
                players = "\n".join(ito.get_player_name_list())
            embed.add_field(name="参加者", value=players, inline=False)
            now = datetime.now().strftime("%Y/%m/%d %H:%M")
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return

        await ctx.defer()

        logger.debug("Game start")

        ito.deal_cards()
        ito.start_game()

        embed_channel = Embed(
            title="Game start!!!",
            description="ゲーム情報",
            color=Colour.dark_blue(),
        )
        embed_channel.add_field(
            name="チャンネル",
            value=ito.get_channel_name(),
            inline=False,
        )
        embed_channel.add_field(
            name="ライフ",
            value=str(ito.get_life()),
            inline=True,
        )
        embed_channel.add_field(
            name="レベル",
            value=str(ito.get_level()),
            inline=True,
        )
        embed_channel.add_field(
            name="トークテーマ",
            value=ito.get_theme(),
            inline=False,
        )

        embed_dm = Embed(
            title="Game start!!!",
            description="ゲーム情報",
            color=Colour.dark_blue(),
        )

        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        embed_channel.set_footer(text=now)
        embed_dm.set_footer(text=now)

        players: list[Player] = list(ito.get_players().values())
        for player in players:
            embed_channel.add_field(
                name=player.get_name(),
                value=player.hand_to_string_close(),
                inline=True,
            )

            embed_dm.clear_fields()

            embed_dm.add_field(
                name="チャンネル",
                value=ito.get_channel_name(),
                inline=False,
            )
            embed_dm.add_field(
                name="ライフ",
                value=str(ito.get_life()),
                inline=True,
            )
            embed_dm.add_field(
                name="レベル",
                value=str(ito.get_level()),
                inline=True,
            )
            embed_dm.add_field(
                name="トークテーマ",
                value=ito.get_theme(),
                inline=False,
            )

            embed_dm.add_field(
                name="カード (他の人に教えないように！)",
                value=player.hand_to_string_open(),
                inline=False,
            )
            await player.get_member().send(embed=embed_dm)

        await ctx.send(embed=embed_channel)

    @commands.hybrid_command(name="stop", description="ゲームを終了します")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_in_game
    @only_for_player
    async def stop(self, ctx: commands.Context):
        """
        stop command

        ゲームを終了
        """

        ito = self.ito
        ito.initialize_game()

        embed = Embed(
            title="Stop command",
            description="ゲームを終了しました",
            color=Colour.dark_blue(),
        )
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="put", description="手札の中で最小のカードを場に出します"
    )
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_in_game
    @only_for_player
    async def put(self, ctx: commands.Context):
        """
        put command

        手札の中で最小のカードを場に出す
        """

        ito = self.ito
        current_player = ito.get_player(ctx.author.id)
        card_put = current_player.put_card()
        players: list[Player] = list(ito.get_players().values())
        now = datetime.now().strftime("%Y/%m/%d %H:%M")

        if card_put == None:
            embed = Embed(
                title="Put command",
                description="手札がありません",
                color=Colour.gold(),
            )
            embed.add_field(name="ライフ", value=str(ito.get_life()), inline=True)
            embed.add_field(name="レベル", value=str(ito.get_level()), inline=True)
            embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
            for player in players:
                embed.add_field(
                    name=player.get_name(),
                    value=player.hand_to_string_close(),
                    inline=True,
                )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return

        ito.receive_card(card_put)
        count_penalty = 0

        for player in players:
            while player.has_smaller_card(card_put):
                penalty = player.put_card()
                ito.receive_card(penalty)
                ito.decrease_life()
                count_penalty += 1

        if ito.is_gameover():
            logger.debug("Game over")
            embed = Embed(
                title="Game over",
                description="小さいカードを場に出しました\nライフが0になりました\nゲームを終了します",
                color=Colour.magenta(),
            )
            embed.add_field(name="ライフ", value="0", inline=True)
            embed.add_field(name="レベル", value=str(ito.get_level()), inline=True)
            for player in players:
                embed.add_field(
                    name=player.get_name(),
                    value=player.hand_to_string_open(),
                    inline=True,
                )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)

            ito.initialize_game()
            return

        if ito.is_cleared():
            logger.debug("Game clear")
            embed = Embed(
                title="Game clear",
                description="ゲームをクリアしました！\nゲームを終了します",
                color=Colour.green(),
            )
            embed.add_field(name="ライフ", value=str(ito.get_life()), inline=True)
            embed.add_field(name="レベル", value=str(ito.get_level()), inline=True)
            for player in players:
                embed.add_field(
                    name=player.get_name(),
                    value=player.hand_to_string_open(),
                    inline=True,
                )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)

            ito.initialize_game()
            return

        if not ito.is_gameover() and 0 < count_penalty:
            logger.debug("Failure")
            embed = Embed(
                title="Failure",
                description="失敗しました...\n小さいカードを場に出しました\n場に出された枚数分のライフを減らします\n次に小さいカードを場に出してください",
                color=Colour.gold(),
            )
            embed.add_field(name="ライフ", value=str(ito.get_life()), inline=True)
            embed.add_field(name="レベル", value=str(ito.get_level()), inline=True)
            embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
            for player in players:
                embed.add_field(
                    name=player.get_name(),
                    value=player.hand_to_string_close(),
                    inline=True,
                )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return

        if count_penalty == 0:
            logger.debug("Success")
            embed = Embed(
                title="Success",
                description="成功しました！\n次に小さいカードを場に出してください",
                color=Colour.green(),
            )
            embed.add_field(name="ライフ", value=str(ito.get_life()), inline=True)
            embed.add_field(name="レベル", value=str(ito.get_level()), inline=True)
            embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
            for player in players:
                embed.add_field(
                    name=player.get_name(),
                    value=player.hand_to_string_close(),
                    inline=True,
                )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return

    @commands.hybrid_group(
        name="setting",
        description="Setting commands",
        invoke_without_command=True,
    )
    async def setting(self, ctx: commands.Context):
        cmds: set[commands.Command] = self.bot.commands
        description = ""
        for cmd in cmds:
            description += f"`{cmd.name}` : {cmd.description}\n"
        embed = Embed(
            title="Settings",
            description=description,
            color=Colour.dark_blue(),
        )
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @setting.command(name="theme", description="テーマを設定します")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_off_game
    @only_for_player
    async def set_theme(self, ctx: commands.Context, *, theme: str):
        ito = self.ito
        ito.set_theme(theme)
        embed = Embed(
            title="Set theme command",
            description=f"トークテーマを設定しました",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="トークテーマ", value=ito.get_theme(), inline=False)
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @setting.command(name="channel", description="チャンネルを設定します")
    @log_wrapper
    @only_off_game
    async def set_channel(self, ctx: commands.Context):
        ito = self.ito
        ito.set_guild(ctx.guild)
        ito.set_channel(ctx.channel)
        embed = Embed(
            title="Set channel command",
            description=f"チャンネルを設定しました",
            color=Colour.dark_blue(),
        )
        embed.add_field(name="チャンネル", value=ito.get_channel(), inline=False)
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @setting.command(name="life", description="ライフを設定します")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_off_game
    @only_for_player
    async def set_life(self, ctx: commands.Context, *, life: int):
        ito = self.ito
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        if life < 1 or 3 < life:
            embed = Embed(
                title="Set life command",
                description="ライフは1~3の間で指定してね！",
                color=Colour.gold(),
            )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return

        ito.set_life(life)
        embed = Embed(
            title="Set life command",
            description=f"ライフを{life}に設定しました",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await ctx.send(embed=embed)

    @setting.command(name="level", description="レベルを設定します")
    @log_wrapper
    @channel_registerd_check
    @only_in_channel
    @only_off_game
    @only_for_player
    async def set_level(self, ctx: commands.Context, *, level: int):
        ito = self.ito
        now = datetime.now().strftime("%Y/%m/%d %H:%M")
        if level < 1 or 3 < level:
            embed = Embed(
                title="Set level command",
                description="レベルは1~3の間で指定してね！",
                color=Colour.gold(),
            )
            embed.set_footer(text=now)
            await ctx.send(embed=embed)
            return

        ito.set_level(level)
        embed = Embed(
            title="Set level command",
            description=f"レベルを{level}に設定しました",
            color=Colour.dark_blue(),
        )
        embed.set_footer(text=now)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))
