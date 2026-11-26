# -*- coding: utf-8 -*-
"""ASCII七並べ：初学者向けの関数中心サンプルゲーム（カラー表示・ジョーカー対応版）。

起動：python w14_ascii_seven_cards.py
外部ライブラリ不要。1人（人間）＋3人（CPU）で遊びます。
"""

import os
import random

# WindowsのターミナルでANSIカラーを有効にするおまじない
os.system("")

SUITS = ["S", "H", "D", "C"]
JOKER = ("JK", 0)  # ジョーカーを表すタプル

# ANSIカラーコード定義
RED = "\033[91m"     # 明るい赤（ハート・ダイヤ用）
CYAN = "\033[96m"    # 明るいシアン（スペード・クラブ用）
YELLOW = "\033[93m"  # 明るい黄色（ジョーカー用）
RESET = "\033[0m"    # 色を元に戻す


def colorize(text, suit):
    """マークに応じて文字に色を付ける。"""
    if suit in ("H", "D"):
        return f"{RED}{text}{RESET}"
    if suit == "JK":
        return f"{YELLOW}{text}{RESET}"
    return f"{CYAN}{text}{RESET}"


def rank_name(rank):
    """1, 11, 12, 13 を A, J, Q, K として表示する。"""
    if rank == 1:
        return "A"
    if rank == 11:
        return "J"
    if rank == 12:
        return "Q"
    if rank == 13:
        return "K"
    return str(rank)


def card_name(card):
    """('S', 6) を色付きの 'S6'、('JK', 0) を 'JK' にする。"""
    suit, rank = card
    if suit == "JK":
        return colorize("JK", "JK")
    return colorize(suit + rank_name(rank), suit)


def create_deck():
    """7を除いた48枚＋ジョーカー2枚＝計50枚の山札を作り、シャッフルする。"""
    deck = []
    for suit in SUITS:
        for rank in range(1, 14):
            if rank != 7:
                deck.append((suit, rank))
    # ジョーカーを2枚追加
    deck.append(JOKER)
    deck.append(JOKER)
    random.shuffle(deck)
    return deck


def deal_cards(deck):
    """50枚を4人に配る（13枚, 13枚, 12枚, 12枚）。"""
    hands = [[], [], [], []]
    for i in range(len(deck)):
        player = i % 4
        hands[player].append(deck[i])
    for hand in hands:
        # ジョーカーが末尾に並ぶようにソート
        hand.sort(key=lambda c: (1 if c == JOKER else 0, c[0], c[1]))
    return hands


def create_board():
    """4種類の7が最初から置かれた場を作る。jokersにジョーカーの配置場所を記録する。"""
    board = {}
    for suit in SUITS:
        board[suit] = [7]
    board["jokers"] = set()  # 例: {('S', 6), ('H', 8)}
    return board


def can_play(card, board):
    """そのカード（またはジョーカーの代用先）を場に出せるか判定する。"""
    suit, rank = card
    if suit == "JK":
        # 場のどこか1箇所でも出せる空き場所があればジョーカーを出せる
        for s in SUITS:
            for r in range(1, 14):
                if r not in board[s] and can_play((s, r), board):
                    return True
        return False

    # すでにジョーカーが置かれている場所なら、本来のカードを出して回収できる
    if (suit, rank) in board["jokers"]:
        return True

    # まだ置かれていない場所で、隣の数字が場にあれば出せる
    if rank not in board[suit]:
        if (rank - 1 in board[suit]) or (rank + 1 in board[suit]):
            return True
    return False


def get_valid_joker_targets(board):
    """現在ジョーカーを置ける全候補（例: [('S', 6), ('S', 8), ...]）を返す。"""
    targets = []
    for s in SUITS:
        for r in range(1, 14):
            if r not in board[s] and can_play((s, r), board):
                targets.append((s, r))
    return targets


def put_card(card, hand, board, target=None):
    """手札から1枚取り除き、場へ置く。ジョーカーの回収や代用配置も処理する。"""
    if card == JOKER:
        suit, rank = target
        hand.remove(JOKER)
        board[suit].append(rank)
        board["jokers"].add((suit, rank))
        return False  # 回収は発生しない

    suit, rank = card
    hand.remove(card)

    # 場にジョーカーが置かれていた場所なら、入れ替えてジョーカーを手札に回収！
    if (suit, rank) in board["jokers"]:
        board["jokers"].remove((suit, rank))
        hand.append(JOKER)
        hand.sort(key=lambda c: (1 if c == JOKER else 0, c[0], c[1]))
        return True  # 回収したことを通知

    board[suit].append(rank)
    return False


def show_board(board):
    """4種類×13列の並びを色付き文字で表示する。ジョーカー配置場所はJKと表示。"""
    print("\n===== 場のカード =====")
    print("      ", end="")
    for rank in range(1, 14):
        print(f"{rank_name(rank):>3}", end="")
    print()

    for suit in SUITS:
        colored_suit = colorize(suit, suit)
        print(f" {colored_suit}  | ", end="")
        for rank in range(1, 14):
            if (suit, rank) in board["jokers"]:
                # ジョーカーが代用されている場所
                formatted = f"{'JK':>3}"
                mark = colorize(formatted, "JK")
            elif rank in board[suit]:
                formatted = f"{rank_name(rank):>3}"
                mark = colorize(formatted, suit)
            else:
                mark = f"{'.':>3}"
            print(mark, end="")
        print()
    print(f"{colorize('S=スペード', 'S')}  {colorize('H=ハート', 'H')}  "
          f"{colorize('D=ダイヤ', 'D')}  {colorize('C=クラブ', 'C')}  "
          f"{colorize('JK=ジョーカー', 'JK')}")
    print(". はまだ置かれていないカードです。")


def show_hand(hand, board):
    """自分の手札を表示。今出せるカードには * を付ける。"""
    print("\n自分の手札（* は今出せる札）")
    for card in hand:
        suit, rank = card
        raw_label = "JK" if suit == "JK" else suit + rank_name(rank)
        if can_play(card, board):
            raw_label += "*"
        print(f"[{colorize(raw_label, suit)}]", end=" ")
    print()


def read_card(text):
    """入力 'S6'、'H10'、'DA' などをカードに変換する。"""
    text = text.strip().upper().replace(" ", "")
    if len(text) < 2:
        return None

    suit = text[0]
    number = text[1:]
    if suit not in SUITS:
        return None

    if number == "A":
        rank = 1
    elif number == "J":
        rank = 11
    elif number == "Q":
        rank = 12
    elif number == "K":
        rank = 13
    elif number.isdigit():
        rank = int(number)
    else:
        return None

    if rank < 1 or rank > 13 or rank == 7:
        return None
    return (suit, rank)


def human_turn(hand, board):
    """人間の番。札を置くか、パスする。Qならゲーム終了。"""
    show_board(board)
    show_hand(hand, board)

    while True:
        command = input("出す札（例 S6 / JK S6）、P=パス、Q=終了 > ")
        command = command.strip().upper()

        if command == "Q":
            return False
        if command == "P" or command == "PASS":
            print("あなたはパスしました。")
            return True

        # ジョーカーを出す場合（例: "JK S6"）
        if command.startswith("JK"):
            if JOKER not in hand:
                print("ジョーカーを手札に持っていません。")
                continue

            target_text = command[2:].strip()
            target = read_card(target_text)
            if target is None:
                print("ジョーカーを置く場所を指定してください。例：JK S6")
            elif target not in get_valid_joker_targets(board):
                print("その場所にはまだジョーカーを置けません。")
            else:
                put_card(JOKER, hand, board, target)
                print(f"{card_name(JOKER)} を {card_name(target)} の場所に出しました。")
                return True

        # 通常のカードを出す場合（ジョーカー回収も含む）
        card = read_card(command)
        if card is None:
            print("入力が正しくありません。例：S6、H10、DA、JK S6")
        elif card not in hand:
            print("そのカードは手札にありません。")
        elif not can_play(card, board):
            print("そのカードはまだ出せません。隣の数字を確認してください。")
        else:
            recovered = put_card(card, hand, board)
            print(card_name(card) + " を出しました。")
            if recovered:
                print(f"★ 場の {card_name(JOKER)} を回収しました！")
            return True


def cpu_turn(hand, board, cpu_number):
    """CPUの思考：通常札（回収含む）があれば優先して出し、なければジョーカーを使う。"""
    normal_choices = []
    for card in hand:
        if card != JOKER and can_play(card, board):
            normal_choices.append(card)

    if len(normal_choices) > 0:
        card = random.choice(normal_choices)
        recovered = put_card(card, hand, board)
        msg = f"CPU{cpu_number}：{card_name(card)} を出した"
        if recovered:
            msg += f"（{card_name(JOKER)} を回収！）"
        print(msg)
    elif JOKER in hand and can_play(JOKER, board):
        targets = get_valid_joker_targets(board)
        target = random.choice(targets)
        put_card(JOKER, hand, board, target)
        print(f"CPU{cpu_number}：{card_name(JOKER)} を {card_name(target)} の場所に出した")
    else:
        print(f"CPU{cpu_number}：パス")


def main():
    print("ASCII 七並べ － あなた VS CPU 3人（ジョーカー2枚入り）")
    print("各マークの7から左右へ、数字を順番につなげます。")
    print("ジョーカー(JK)は出せる場所のどこにでも置けます（例: JK S6）。")
    print("JKが置かれた場所の本来のカードを出すと、JKを手札に回収できます。")

    deck = create_deck()
    hands = deal_cards(deck)
    board = create_board()
    turn = 0

    while True:
        print("\n------------------------------")
        if turn == 0:
            print("あなたの番です。")
            keep_playing = human_turn(hands[0], board)
            if not keep_playing:
                print("ゲームを終了しました。")
                break
        else:
            cpu_turn(hands[turn], board, turn)

        if len(hands[turn]) == 0:
            show_board(board)
            if turn == 0:
                print("おめでとう！ あなたの勝ちです！")
            else:
                print("CPU" + str(turn) + " の勝ちです！")
            break

        turn = (turn + 1) % 4


if __name__ == "__main__":
    main()