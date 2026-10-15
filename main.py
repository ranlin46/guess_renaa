import random
import itertools


class GuessRenaaGame:
    def __init__(self):
        self.characters = ["ほのす", "ひかる", "れなぁ"]
        self.numbers = ["1", "2", "3"]
        self.identity_by_number = {}
        self.claims = {}
        self.evidence = None

    def new_round(self):
        shuffled = self.characters.copy()
        random.shuffle(shuffled)

        self.identity_by_number = dict(
            zip(self.numbers, shuffled)
        )

    def allowed_claims(self, num):
        real = self.identity_by_number[num]

        if real == "れなぁ":
            return self.characters.copy()

        return [
            character for character in self.characters
            if character != real
        ]

    def generate_claims(self):
        self.claims = {}

        for num in self.numbers:
            options = self.allowed_claims(num)
            claim = random.choice(options)

            self.claims[num] = claim

    def possible_assignments(self):
        possibilities = []

        for arrangement in itertools.permutations(self.characters):
            candidate = dict(zip(self.numbers, arrangement))

            # 第一关检查：发言是否合法
            if any(
                    candidate[num] != "れなぁ"
                    and candidate[num] == self.claims[num]
                    for num in self.numbers
            ):
                continue

            # 第二关检查：是否符合客观证据
            if self.evidence is not None:
                left, right = self.evidence

                candidate_positions = {}

                for num, character in candidate.items():
                    candidate_positions[character] = int(num)

                if candidate_positions[left] >= candidate_positions[right]:
                    continue

            possibilities.append(candidate)

        return possibilities

    def generate_evidence(self):
        positions = {}

        for num, character in self.identity_by_number.items():
            positions[character] = int(num)

        if positions["ひかる"] < positions["れなぁ"]:
            self.evidence = ("ひかる", "れなぁ")
        else:
            self.evidence = ("れなぁ", "ひかる")

    def is_renaa_provable(self, possibilities):
        possible_numbers = set()

        for candidate in possibilities:
            for num in self.numbers:
                if candidate[num] == "れなぁ":
                    possible_numbers.add(num)

        return len(possible_numbers) == 1

    def possible_followup_claims(self, candidate, num):
        real = candidate[num]
        first = self.claims[num]

        options = []

        for character in self.characters:
            if character == first:
                continue

            if real != "れなぁ" and character == real:
                continue

            options.append(character)

        return options

    def guaranteed_followups(self, possibilities):
        safe_numbers = []

        for num in self.numbers:
            results = {}

            for candidate in possibilities:
                renaa_num = next(
                    n for n in self.numbers
                    if candidate[n] == "れなぁ"
                )

                options = self.possible_followup_claims(candidate, num)

                for answer in options:
                    if answer not in results:
                        results[answer] = set()

                    results[answer].add(renaa_num)

            if results and all(
                    len(positions) == 1
                    for positions in results.values()
            ):
                safe_numbers.append(num)

        return safe_numbers

    def new_playable_round(self):
        for attempt in range(1000):
            self.new_round()
            self.generate_claims()
            self.generate_evidence()

            possibilities = self.possible_assignments()

            if (
                    not self.is_renaa_provable(possibilities)
                    and self.guaranteed_followups(possibilities)
            ):
                return possibilities

        raise RuntimeError("没有找到符合要求的题目")

    def ask_again(self, num):
        options = self.possible_followup_claims(
            self.identity_by_number, num
        )

        answer = random.choice(options)

        return answer

    def filter_after_followup(self, possibilities, num, answer):
        remaining = []

        for candidate in possibilities:
            options = self.possible_followup_claims(candidate, num)

            if answer in options:
                remaining.append(candidate)

        return remaining

    def show_debug(self):
        print("===== 本局身份与发言 =====")

        for num, character in self.identity_by_number.items():
            options = self.allowed_claims(num)

            print(f"{num}号真实身份：{character}")
            print(f"  可以说：{'、'.join(options)}")
            print(f"  实际说：{self.claims[num]}")


if __name__ == "__main__":
    game = GuessRenaaGame()

    # 生成一局保证存在必胜追问的题目
    possibilities = game.new_playable_round()

    print("===== 猜猜谁是れなぁ =====")
    print("ほのす和ひかる一定说假话。")
    print("れなぁ可以说真话，也可以说假话。")
    print("每局只能追问一个人一次。")
    print("第二次回答不能与第一次相同。")

    print("\n===== 三个人的发言 =====")

    for num in game.numbers:
        print(f"{num}号说：{game.claims[num]}")

    left, right = game.evidence

    print("\n===== 客观证据 =====")
    print(f"{left}在{right}的左边。")

    # 由玩家决定追问谁
    print("\n===== 追问阶段 =====")

    while True:
        chosen = input("你想追问几号？(1/2/3)：").strip()

        if chosen in game.numbers:
            break

        print("请输入1、2或3。")

    answer = game.ask_again(chosen)

    print(f"\n{chosen}号第二次回答：{answer}")

    # 根据第二次回答重新筛选可能性
    remaining = game.filter_after_followup(
        possibilities, chosen, answer
    )

    # 玩家自己选择答案
    print("\n===== 最终回答 =====")

    while True:
        guess = input("你认为れなぁ是几号？(1/2/3)：").strip()

        if guess in game.numbers:
            break

        print("请输入1、2或3。")

    # 找到真正的れなぁ
    real_number = next(
        num for num in game.numbers
        if game.identity_by_number[num] == "れなぁ"
    )

    # 判断玩家得到的信息是否足够
    provable = game.is_renaa_provable(remaining)

    print("\n===== 游戏结果 =====")

    if guess == real_number and provable:
        print("恭喜！你通过推理找到了れなぁ！")

    elif guess == real_number:
        print("你猜对了！")
        print("但现有线索还不能唯一确定答案。")
        print("所以这次不算推理通关。")

    else:
        print("很遗憾，回答错误！")

        if not provable:
            print("而且这次追问后，线索仍然不足。")

    print(f"\n真正的れなぁ是{real_number}号。")

    print("\n===== 真实身份 =====")

    for num, character in game.identity_by_number.items():
        print(f"{num}号是{character}")
