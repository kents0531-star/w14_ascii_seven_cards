# -*- coding: utf-8 -*-
"""ASCII七並べ：初学者向けの関数中心サンプルゲーム。

起動：python w14_ascii_seven_cards.py
外部ライブラリ不要。1人（人間）＋3人（CPU）で遊びます。
"""

import random


SUITS = ["S", "H", "D", "C"]


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
    """('S', 6) を 'S6' のような表示にする。"""
    suit, rank = card
    return suit + rank_name(rank)


def create_deck():
    """7を除いた48枚の山札を作り、シャッフルする。"""
    deck = []
    for suit in SUITS:
        for rank in range(1, 14):
            if rank != 7:
                deck.append((suit, rank))
    random.shuffle(deck)
    return deck


def deal_cards(deck):
    """48枚を4人に12枚ずつ配る。"""
    hands = [[], [], [], []]
    for i in range(len(deck)):
        player = i % 4
        hands[player].append(deck[i])
    for hand in hands:
        hand.sort()
    return hands


def create_board():
    """4種類の7が最初から置かれた場を作る。"""
    board = {}
    for suit in SUITS:
        board[suit] = [7]
    return board


def can_play(card, board):
    """同じマークで隣の数字が場にあれば、その札を出せる。"""
    suit, rank = card
    if rank - 1 in board[suit]:
        return True
    if rank + 1 in board[suit]:
        return True
    return False


def put_card(card, hand, board):
    """手札から1枚取り除き、場へ置く。"""
    suit, rank = card
    hand.remove(card)
    board[suit].append(rank)


def show_board(board):
    """4種類×13列の並びを文字で表示する。"""
    print("\n===== 場のカード =====")
    print("      ", end="")
    for rank in range(1, 14):
        print(f"{rank_name(rank):>3}", end="")
    print()

    for suit in SUITS:
        print(f" {suit}  | ", end="")
        for rank in range(1, 14):
            if rank in board[suit]:
                mark = rank_name(rank)
            else:
                mark = "."
            print(f"{mark:>3}", end="")
        print()
    print("S=スペード  H=ハート  D=ダイヤ  C=クラブ")
    print(". はまだ置かれていないカードです。")


def show_hand(hand, board):
    """自分の手札を表示。今出せるカードには * を付ける。"""
    print("\n自分の手札（* は今出せる札）")
    for card in hand:
        label = card_name(card)
        if can_play(card, board):
            label = label + "*"
        print(f"[{label}]", end=" ")
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
        command = input("出す札（例 S6 / H10 / DA）、P=パス、Q=終了 > ")
        command = command.strip().upper()

        if command == "Q":
            return False
        if command == "P" or command == "PASS":
            print("あなたはパスしました。")
            return True

        card = read_card(command)
        if card is None:
            print("入力が正しくありません。例：S6、H10、DA")
        elif card not in hand:
            print("そのカードは手札にありません。")
        elif not can_play(card, board):
            print("そのカードはまだ出せません。隣の数字を確認してください。")
        else:
            put_card(card, hand, board)
            print(card_name(card) + " を出しました。")
            return True


def cpu_turn(hand, board, cpu_number):
    """CPUは出せる札を調べ、あればランダムに1枚出す。"""
    choices = []
    for card in hand:
        if can_play(card, board):
            choices.append(card)

    if len(choices) == 0:
        print("CPU" + str(cpu_number) + "：パス")
    else:
        card = random.choice(choices)
        put_card(card, hand, board)
        print("CPU" + str(cpu_number) + "：" + card_name(card) + " を出した")


def main():
    print("ASCII 七並べ － あなた VS CPU 3人")
    print("各マークの7から左右へ、数字を順番につなげます。")
    print("出せるカードがないときは P でパスできます。")
    print("今回は初心者向けルール：パス回数に制限なし。最初に手札0枚で勝利！")

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
