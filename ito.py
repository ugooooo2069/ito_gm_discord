# ゲームクラス
# クラス名'Game'がdiscord.pyのクラス名にも存在しているため不適切
# クラス名を変更する必要あり

# 2024/01/22 itoクラスに名称変更

# 進行中のゲーム情報を格納するクラス

import discord
from discord import Guild, TextChannel
import random
from player import Player


class Ito:
    """
    itoクラス

    Attributes
    -------------------
    __guild_id : discord.Guild.id
        サーバーID
    __channel_id : discord.Message.channel.id
        ゲームが開始されたチャンネル
    __players : dict
        プレイヤーのdict
        キー : discord.Member.id
        値 : Player
    __life : int = 3
        ライフ
    __deck : dict
        キー : カード番号
        場札フラグ : bool (True : 場に出されている)
    __theme : str
        トークテーマ
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self.__guild: Guild = None
        self.__channel: TextChannel = None
        self.__players: dict[int:Player] = dict()
        self.__life: int = 3
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
        チャンネルIDを設定する

        Parameters
        ----------
        channel_id: int
            チャンネルID
        """
        self.__channel = channel

    def set_life(self, life: int):
        """
        ライフを設定する

        Parameters
        ----------
        life: int
            ライフ
        """
        self.__life = life

    def set_theme(self, theme: str):
        """
        トークテーマを設定する

        Parameters
        ----------
        theme: str
            トークテーマ
        """
        self.__theme = theme

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

    # カードを生成してプレイヤーに配る
    def deal_cards(self):
        """
        カードを生成してプレイヤーに配る
        場を生成する
        """

        # 仮のセットを生成する
        temporary_set = set()

        # プレイヤー数分の乱数を追加する
        while len(temporary_set) <= len(self.__players):
            temporary_set.add(random.randint(1, 100))

        # deckをプレイヤーに配る
        temporary_list = list(temporary_set)
        players: list[Player] = list(self.__players.values())
        for player in players:
            number = temporary_list.pop()
            player.receive_card(number)

            # deckに追加
            self.__deck[number] = False

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
        deck: dict[int: bool] = self.__deck
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
