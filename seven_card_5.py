# -*- coding: utf-8 -*-
"""ASCII七並べ：初学者向けの関数中心サンプルゲーム
（カラー・ジョーカー・7出し・パス制限＆ドボン・連戦対応版）

起動：python seven_card_5.py
外部ライブラリ不要。1人（人間）＋3人（CPU）で遊びます。
"""

import os
import random

# WindowsのターミナルでANSIカラーを有効にするおまじない
os.system("")

SUITS = ["S", "H", "D", "C"]
JOKER = ("JK", 0)  # ジョーカーを表すタプル
MAX_PASSES = 3     # パス上限（3回までOK、4回目でドボン）

# ANSIカラーコード定義
RED = "\033[91m"     # 明るい赤（ハート・ダイヤ用）
CYAN = "\033[96m"    # 明るいシアン（スペード・クラブ用）
YELLOW = "\033[93m"  # 明るい黄色（ジョーカー用）
GRAY = "\033[90m"    # グレー（脱落表示用）
RESET = "\033[0m"    # 色を元に戻す


def colorize(text, suit):
    """マークに応じて文字に色を付ける。"""
    if suit in ("H", "D"):
        return f"{RED}{text}{RESET}"
    if suit == "JK":
        return f"{YELLOW}{text}{RESET}"
    if suit == "GRAY":
        return f"{GRAY}{text}{RESET}"
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
    """全52枚＋ジョーカー2枚＝計54枚の山札を作り、シャッフルする。"""
    deck = []
    for suit in SUITS:
        for rank in range(1, 14):
            deck.append((suit, rank))
    deck.append(JOKER)
    deck.append(JOKER)
    random.shuffle(deck)
    return deck


def deal_cards(deck):
    """54枚を4人に配る（14枚, 14枚, 13枚, 13枚）。"""
    hands = [[], [], [], []]
    for i in range(len(deck)):
        player = i % 4
        hands[player].append(deck[i])
    for hand in hands:
        hand.sort(key=lambda c: (1 if c == JOKER else 0, c[0], c[1]))
    return hands


def create_board():
    """最初は空の場を作る（7は手札から出すため）。"""
    board = {}
    for suit in SUITS:
        board[suit] = []
    board["jokers"] = set()
    return board


def setup_sevens(hands, board):
    """配布された手札からすべての7を場に出し、D7を持っていたプレイヤー番号を返す。"""
    start_player = 0
    player_names = ["あなた", "CPU1", "CPU2", "CPU3"]

    print("\n===== 7の配置 =====")
    for i in range(4):
        sevens = [card for card in hands[i] if card[1] == 7]
        if sevens:
            names = ", ".join(card_name(c) for c in sevens)
            print(f"{player_names[i]} が {names} を場に出しました。")
            for card in sevens:
                if card == ("D", 7):
                    start_player = i
                put_card(card, hands[i], board)
        else:
            print(f"{player_names[i]} は7を持っていませんでした。")

    print(f"★ {card_name(('D', 7))} を出した {player_names[start_player]} からスタートします！")
    return start_player


def can_play(card, board):
    """そのカード（またはジョーカーの代用先）を場に出せるか判定する。"""
    suit, rank = card
    if suit == "JK":
        for s in SUITS:
            for r in range(1, 14):
                if r not in board[s] and can_play((s, r), board):
                    return True
        return False

    if (suit, rank) in board["jokers"]:
        return True

    if rank not in board[suit]:
        if rank == 7:
            return True
        if (rank - 1 in board[suit]) or (rank + 1 in board[suit]):
            return True
    return False


def get_valid_joker_targets(board):
    """現在ジョーカーを置ける全候補を返す。"""
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
        return False

    suit, rank = card
    hand.remove(card)

    if (suit, rank) in board["jokers"]:
        board["jokers"].remove((suit, rank))
        hand.append(JOKER)
        hand.sort(key=lambda c: (1 if c == JOKER else 0, c[0], c[1]))
        return True

    board[suit].append(rank)
    return False


def eliminate_player(player_idx, hands, board, eliminated):
    """ドボン（脱落）処理：手札の通常カードをすべて場に並べ、ジョーカーは除外する。"""
    player_names = ["あなた", "CPU1", "CPU2", "CPU3"]
    eliminated[player_idx] = True

    remaining = list(hands[player_idx])
    hands[player_idx].clear()

    opened_cards = []
    joker_count = 0

    for card in remaining:
        if card == JOKER:
            joker_count += 1
        else:
            suit, rank = card
            if (suit, rank) in board["jokers"]:
                board["jokers"].remove((suit, rank))
            if rank not in board[suit]:
                board[suit].append(rank)
            opened_cards.append(card_name(card))

    print(f"💥 ドボン！ {player_names[player_idx]} は {MAX_PASSES + 1}回目のパスで脱落しました！")
    if opened_cards:
        print(f"   手札の {' '.join(opened_cards)} がすべて場に並べられました！")
    if joker_count > 0:
        print(f"   持っていた {card_name(JOKER)} ({joker_count}枚) はゲームから除外されました。")


def show_status(hands, passes, eliminated):
    """全員の残り手札枚数とパス回数を表示する。"""
    player_names = ["あなた", "CPU1", "CPU2", "CPU3"]
    status_parts = []
    for i in range(4):
        if eliminated[i]:
            status_parts.append(colorize(f"{player_names[i]}:脱落", "GRAY"))
        else:
            p_str = f"{passes[i]}/{MAX_PASSES}"
            if passes[i] == MAX_PASSES:
                p_str = colorize(p_str + "!", "H")
            status_parts.append(f"{player_names[i]}:{len(hands[i])}枚(パス{p_str})")
    print("【状況】 " + " | ".join(status_parts))


def show_board(board):
    """4種類×13列の並びを色付き文字で表示する。"""
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

    if rank < 1 or rank > 13:
        return None
    return (suit, rank)


def human_turn(hands, board, passes, eliminated):
    """人間の番。戻り値: 'PLAYED'（出した）, 'PASS'（パスした）, 'QUIT'（終了）"""
    hand = hands[0]
    show_board(board)
    show_status(hands, passes, eliminated)
    show_hand(hand, board)

    rem_passes = MAX_PASSES - passes[0]
    if rem_passes > 0:
        pass_guide = f"P=パス（残り{rem_passes}回可能）"
    else:
        pass_guide = colorize("P=パス（注意：次はドボン！）", "H")

    while True:
        command = input(f"出す札（例 S6 / JK S6）、{pass_guide}、Q=終了 > ")
        command = command.strip().upper()

        if command == "Q":
            return "QUIT"
        if command == "P" or command == "PASS":
            if passes[0] >= MAX_PASSES:
                ans = input("パス上限を超えるとドボン（脱落）になります。本当にパスしますか？(Y/N) > ").strip().upper()
                if ans != "Y":
                    continue
            passes[0] += 1
            print(f"あなたはパスしました。（累計パス: {passes[0]}/{MAX_PASSES}）")
            return "PASS"

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
                return "PLAYED"

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
            return "PLAYED"


def cpu_turn(hand, board, cpu_number, passes):
    """CPUの思考：通常札があれば出し、なければジョーカーを使う。"""
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
        return "PLAYED"
    elif JOKER in hand and can_play(JOKER, board):
        targets = get_valid_joker_targets(board)
        target = random.choice(targets)
        put_card(JOKER, hand, board, target)
        print(f"CPU{cpu_number}：{card_name(JOKER)} を {card_name(target)} の場所に出した")
        return "PLAYED"
    else:
        passes[cpu_number] += 1
        print(f"CPU{cpu_number}：パス（累計パス: {passes[cpu_number]}/{MAX_PASSES}）")
        return "PASS"


def show_score(game_count, wins, dobon_counts):
    """通算成績を表示する。"""
    player_names = ["あなた", "CPU1", "CPU2", "CPU3"]
    print(f"\n===== 通算成績（全 {game_count} 戦） =====")
    for i in range(4):
        print(f"  {player_names[i]:<6}: {wins[i]} 勝 （ドボン {dobon_counts[i]} 回）")


def play_one_game(game_count, wins, dobon_counts):
    """1試合分のゲーム進行を行う。途中でQが押された場合は False を返す。"""
    print(f"\n==========================================")
    print(f"           ★ 第 {game_count} 戦 開始！ ★")
    print(f"==========================================")
    print("カードをシャッフルして配りました！")

    deck = create_deck()
    hands = deal_cards(deck)
    board = create_board()
    passes = [0, 0, 0, 0]
    eliminated = [False, False, False, False]

    turn = setup_sevens(hands, board)

    while True:
        if eliminated[turn]:
            turn = (turn + 1) % 4
            continue

        print("\n------------------------------")
        if turn == 0:
            print("あなたの番です。")
            result = human_turn(hands, board, passes, eliminated)
            if result == "QUIT":
                print("ゲームを中断しました。")
                return False
        else:
            result = cpu_turn(hands[turn], board, turn, passes)

        # パス回数が上限を超えたらドボン処理
        if result == "PASS" and passes[turn] > MAX_PASSES:
            eliminate_player(turn, hands, board, eliminated)
            dobon_counts[turn] += 1

            # 自分がドボンしたら即終了
            if turn == 0:
                show_board(board)
                print("残念！ あなたはドボンしてしまいました。敗北です。")
                return True

            # 自分以外のCPUが全員ドボンしたら自分の勝利
            if eliminated[1] and eliminated[2] and eliminated[3]:
                show_board(board)
                print("おめでとう！ 他のプレイヤーが全員ドボンしたため、あなたの勝ちです！")
                wins[0] += 1
                return True

        # 脱落せずに手札が0枚になったら上がり（勝利）
        if not eliminated[turn] and len(hands[turn]) == 0:
            show_board(board)
            if turn == 0:
                print("おめでとう！ あなたの勝ちです！")
            else:
                print(f"CPU{turn} の勝ちです！")
            wins[turn] += 1
            return True

        turn = (turn + 1) % 4


def main():
    print("ASCII 七並べ － あなた VS CPU 3人（完全版）")
    print(f"・パスは {MAX_PASSES} 回まで。{MAX_PASSES + 1} 回目のパスでドボン（脱落・手札全出し）！")
    print("・最初に手札の7をすべて場に出し、D7を出した人からスタートします。")
    print("・ジョーカー(JK)は出せる場所のどこにでも置けます（例: JK S6）。")

    game_count = 0
    wins = [0, 0, 0, 0]
    dobon_counts = [0, 0, 0, 0]

    while True:
        game_count += 1
        finished_normally = play_one_game(game_count, wins, dobon_counts)

        # 途中で Q による終了が選ばれた場合
        if not finished_normally:
            show_score(game_count - 1, wins, dobon_counts)
            break

        # 1戦終了ごとに成績を表示し、ニュースタートするか確認
        show_score(game_count, wins, dobon_counts)
        while True:
            again = input("\nカードをシャッフルして次の試合を始めますか？ (Y=ニュースタート / N=終了) > ").strip().upper()
            if again in ("Y", "YES"):
                break
            elif again in ("N", "NO", "Q"):
                print("お疲れさまでした！ゲームを終了します。")
                return
            else:
                print("Y または N を入力してください。")


if __name__ == "__main__":
    main()