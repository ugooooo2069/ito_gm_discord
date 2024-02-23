# ゲームクラス
# クラス名'Game'がdiscord.pyのクラス名にも存在しているため不適切
# クラス名を変更する必要あり

# 2024/01/22 itoクラスに名称変更

# 進行中のゲーム情報を格納するクラス

from logging import getLogger, StreamHandler, DEBUG
import discord
from discord import Guild, TextChannel, VoiceChannel
import random
from player import Player


# ----------
# ロガー
# ----------


logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


class Ito:
    """
    itoクラス

    Attributes
    -------------------
    __guild : discord.Guild
        サーバー
    __channel : discord.TextChannel
        ゲームが開始されたチャンネル
    __voice_channel : discord.VoiceChannel
        通話しているボイスチャンネル
    __players : dict
        プレイヤーのdict
        キー : discord.Member.id
        値 : Player
    __life : int = 3
        ライフ
    __level : int = 1
        レベル (各プレイヤーに配るカードの枚数)
    __deck : dict
        キー : カード番号
        場札フラグ : bool (True : 場に出されている)
    __theme : str
        トークテーマ
    __ongoing : bool
        ゲーム中フラグ (True : ゲーム中)
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self.__guild: Guild = None
        self.__channel: TextChannel = None
        self.__voice_channel: VoiceChannel = None
        self.__players: dict[int:Player] = dict()
        self.__life: int = 3
        self.__level: int = 1
        self.__deck: dict[int, bool] = dict()
        self.__theme: str = "トークテーマを設定してください"
        self.__ongoing: bool = False

    # ----------
    # setter
    # ----------

    def set_guild(self, guild: Guild):
        """
        サーバーIDを設定する

        Parameters
        ----------
        guild_id: int
            サーバーID
        """
        self.__guild = guild

    def set_channel(self, channel: TextChannel):
        """
        チャンネルを設定する

        Parameters
        ----------
        channel: TextChannel
            チャンネル
        """
        self.__channel = channel

    def set_voice_channel(self, voice_channel: VoiceChannel):
        """
        ボイスチャンネルを設定する

        Parameters
        ----------
        voice_channel: VoiceChannel
            ボイスチャンネル
        """
        self.__voice_channel = voice_channel

    def set_life(self, life: int):
        """
        ライフを設定する

        Parameters
        ----------
        life: int
            ライフ
        """
        self.__life = life

    def set_level(self, level: int):
        """
        レベルを設定する

        Parameters
        ----------
        level: int
            レベル
        """
        self.__level = level

    def set_theme(self, theme: str):
        """
        トークテーマを設定する

        Parameters
        ----------
        theme: str
            トークテーマ
        """
        self.__theme = theme

    def start_game(self):
        """
        ゲームを開始する
        """
        self.__ongoing = True

    def end_game(self):
        """
        ゲームを終了する
        """
        self.__ongoing = False

    # ----------
    # getter
    # ----------

    def get_guild(self) -> Guild | None:
        """
        サーバーを取得する

        Returns
        -------
        guild: Guild
        """
        return self.__guild

    def get_guild_id(self) -> int:
        """
        サーバーIDを取得する

        Returns
        -------
        guild_id: int
        """
        return self.__guild.id

    def get_guild_name(self) -> str:
        """
        サーバー名を取得する

        Returns
        -------
        guild_name: str
        """
        return self.__guild.name

    def get_channel(self) -> TextChannel | None:
        """
        チャンネルを取得する

        Returns
        -------
        channel: TextChannel
        """
        return self.__channel

    def get_channel_id(self) -> int:
        """
        チャンネルIDを取得する

        Returns
        -------
        channel_id: int
        """
        return self.__channel.id

    def get_channel_name(self) -> str:
        """
        チャンネル名を取得する

        Returns
        -------
        channel_name: str
        """
        return self.__channel.name

    def get_voice_channel(self) -> VoiceChannel | None:
        """
        ボイスチャンネルを取得する

        Returns
        -------
        voice_channel: VoiceChannel
        """
        return self.__voice_channel

    def get_voice_channel_id(self) -> int:
        """
        ボイスチャンネルIDを取得する

        Returns
        -------
        voice_channel_id: int
        """
        return self.__voice_channel.id

    def get_voice_channel_name(self) -> str:
        """
        ボイスチャンネル名を取得する

        Returns
        -------
        voice_channel_name: str
        """
        return self.__voice_channel.name

    def get_players(self) -> dict[int:Player]:
        """
        プレイヤーを取得する

        Returns
        -------
        players: dict[int: Player]
        """
        return self.__players

    def get_player(self, id: discord.Member.id) -> Player:
        """
        プレイヤーを取得する

        Returns
        -------
        player: Player
        """
        return self.__players[id]

    def get_player_id_list(self) -> list[discord.Member.id]:
        """
        プレイヤーIDのリストを取得する

        Returns
        -------
        player_id_list: dict_keys
        """
        return list(self.__players.keys())

    def get_player_name_list(self) -> list[discord.Member.name]:
        """
        プレイヤー名のリストを取得する

        Returns
        -------
        player_name_list: discord.Member.name
        """
        players: list[Player] = list(self.__players.values())
        return [player.get_name() for player in players]

    def get_life(self) -> int:
        """
        ライフを取得する

        Returns
        -------
        life: int
        """
        return self.__life

    def get_level(self) -> int:
        """
        レベルを取得する

        Returns
        -------
        level: int
        """
        return self.__level

    def get_theme(self) -> str:
        """
        トークテーマを取得する

        Returns
        -------
        theme: str
        """
        return self.__theme

    def get_deck(self) -> dict:
        """
        カードを取得する

        Returns
        -------
        deck: dict
        """
        return self.__deck

    def is_ongoing(self) -> bool:
        """
        ゲーム中か判定する

        Returns
        -------
        boolean
            True: ゲーム中
            False: ゲーム中ではない
        """
        return self.__ongoing

    # ----------
    # ito関連
    # ----------

    # プレイヤーを登録する
    def regist_player(self, member: discord.Member):
        """
        プレイヤーを登録する

        Parameters
        ----------
        player: Player
            プレイヤー
        """
        # discord.Member.idをキーとして要素を追加
        self.__players[member.id] = Player(member)

    def delete_player(self, player: discord.Member):
        """
        プレイヤーを削除する

        Parameters
        ----------
        player: Player
            プレイヤー
        """

        try:
            del self.__players[player.id]
        except KeyError:
            raise KeyError("Player not found: " + player.name)

    # カードを生成してプレイヤーに配る
    def deal_cards(self):
        """
        カードを生成してプレイヤーに配る
        場を生成する
        """

        # 仮のセットを生成する
        temporary_deck = set()

        # プレイヤー数分の乱数を追加する
        number_of_cards: int = len(self.__players) * self.__level
        while len(temporary_deck) <= number_of_cards:
            temporary_deck.add(random.randint(1, 100))
        temporary_list = list(temporary_deck)

        # deckをプレイヤーに配る
        players: list[Player] = list(self.__players.values())
        # レベル数分繰り返す
        for turn in range(self.__level):
            # 各プレイヤーにカードを配る
            for player in players:
                number = temporary_list.pop()
                player.receive_card(number)

                # deckに追加
                self.__deck[number] = False

        # ログ出力
        logger.debug("Cards dealt")
        for player in players:
            logger.debug(f"{player.get_name()}: {player.hand_to_string_open()}")

    def receive_card(self, card: int):
        """
        カードを受け取る

        Parameters
        ----------
        card: int
            カード
        """
        self.__deck[card] = True

    def is_minimun(self, card_put: int) -> bool:
        """
        場に出されたカードが
        場に出ていないカードの中で
        最小か判定する

        Parameters
        ----------
        card: int
            カード

        Returns
        -------
        boolean
            True: 最小 False: 最小ではない
        """
        temporary_list = list()

        # deckの中で捨てられていないカードを抽出
        # deckでfor文
        for card_deck in self.__deck.keys():
            # カードが捨てられていない場合
            if self.__deck[card_deck] == False:
                temporary_list.append(card_deck)

        deck_minimun = min(temporary_list)

        if card_put == deck_minimun:
            return True
        else:
            return False

    def decrease_life(self):
        """
        ライフを減らす
        """
        self.__life -= 1

    def is_gameover(self) -> bool:
        """
        ゲームオーバーになっているか判定する

        Returns
        -------
        boolean
            True: ゲームオーバー
            False: ゲームオーバーしていない
        """
        if self.__life > 0:
            return False
        else:
            return True

    def is_cleared(self) -> bool:
        """
        ゲームクリアになっているか判定する

        Returns
        -------
        boolean
            True: ゲームがクリアしている
            False: ゲームがクリアしていない
        """
        # deckの中でFalseになっているカードの数を数える
        deck: dict[int:bool] = self.__deck
        deck_put = list(deck.values())
        false_count = deck_put.count(False)

        if false_count == 0:
            return True
        else:
            return False

    def initialize_game(self):
        """
        ゲームをリセットする
        """
        self.__life = 3
        self.__deck.clear()
        self.__ongoing = False
        players: list[Player] = list(self.__players.values())
        for player in players:
            player.reset_hand()
