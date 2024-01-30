# プレイヤークラス

# プレイヤーのdiscord.Member情報と
# 手札情報を格納するクラス

# 2024/01/23 hand_to_string_dm()を追加
# 2024/01/23 hand_to_string_channel()を追加

import discord


class Player:
    """
    プレイヤー

    Attributes
    ----------
    __member : discord.Member
        プレイヤーのdiscord.Member
    __hand : dict
        プレイヤーの手札
        カード番号 : int
        手札フラグ : bool (True : 手札に入っている)
    """

    def __init__(self, member: discord.Member):
        """
        コンストラクタ

        Parameters
        ----------
        member: discord.Member
        """
        # discord.Member
        self.__member: discord.Member = member

        # 手札
        self.__hand = dict()

    # ----------
    # getter
    # ----------

    def get_name(self) -> str:
        """
        名前を取得

        Returns
        -------
        name: str
        """
        return self.__member.name

    def get_id(self) -> int:
        """
        IDを取得

        Returns
        -------
        id: int
        """
        return self.__member.id

    def get_member(self) -> discord.Member:
        """
        discord.Memberを取得

        Returns
        -------
        member: discord.Member
        """
        return self.__member

    def get_hand(self) -> dict[int:bool]:
        """
        手札を取得

        Returns
        -------
        hand: dict
        """
        return self.__hand

    def get_cards_in_hand(self) -> list[int]:
        """
        手札の中にあるカードを取得

        Returns
        -------
        cards_in_hand: list

        Raises
        ------
        Exception
            手札にカードが入っていない
        """

        cards: list[int] = list(self.__hand.keys())
        cards_in_hand: list[int] = list()

        for card in cards:
            if self.__hand[card] == True:
                cards_in_hand.append(card)

        return cards_in_hand

    def hand_to_string_open(self) -> str:
        """
        手札を文字列で取得
        DM用
        カードをすべて表示

        Returns
        -------
        hand: str
        """
        temporary_string = ""
        for card in self.__hand.keys():
            temporary_string += str(card)
            temporary_string += " "
        return temporary_string

    def hand_to_string_close(self) -> str:
        """
        手札を文字列で取得
        テキストチャンネル用
        場に出していないカードは?と表示

        Returns
        -------
        hand: str
        """
        temporary_string = ""
        for card in self.__hand.keys():
            if self.__hand[card] == True:
                temporary_string += "? "
            elif self.__hand[card] == False:
                temporary_string += str(card)
                temporary_string += " "
        return temporary_string

    # ----------
    # ito関連
    # ----------

    def receive_card(self, card: int):
        """
        カードを受け取る

        Parameters
        ----------
        card: int
            加えるカードの数字
        """
        # 手札を追加
        self.__hand[card] = True

    def put_card(self) -> int | None:
        """
        手札の中で最小のカードを捨てる
        手札の中にTrueのカードがなければ例外

        手札の中にあるかどうか判定していないため、
        手札が2枚以上にするときは変更が必要

        Returns
        -------
        card: int
            最小のカード

        Raises
        ------
        Exception
            手札にカードが入っていない
        """

        # 2024/01/23 例外処理を追加

        cards_hand: list[int] = self.get_cards_in_hand()
        try:
            hand_min = min(cards_hand)
            self.__hand[hand_min] = False
            return hand_min
        except ValueError:
            return None

    def has_smaller_card(self, card_put: int) -> bool:
        """
        カードが場に出された時に
        自分の手札がすべて
        場に出されたカードよりも大きいか
        チェックする

        自分のカードのほうが
        場に出されたカードよりも小さい場合は
        手札内で最小カードの数字を返す

        手札を持っていない場合はFalseを返す

        Parameters
        ----------
        card_put: int
            場に出されたカード

        Returns
        -------
        boolean
            True: 手札の中に場に出されたカードよりも小さいカードが存在する
            False: 自分の手札がすべて場に出されたカードよりも大きい or 手札が無い
        """

        try:
            cards_hand = self.get_cards_in_hand()
            hand_minimun = min(cards_hand)

            if card_put < hand_minimun:
                return False
            else:
                return True

        except ValueError:
            return False

    def reset_hand(self):
        """
        手札をリセットする
        """
        self.__hand.clear()
