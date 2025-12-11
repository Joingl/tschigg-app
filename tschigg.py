import random
import json
from tabulate import tabulate

# Import the ranking JSONs
with open('values_low.json', 'r') as file:
    values_low = json.load(file)

with open('values_high_standard.json', 'r') as file:
    values_high_standard = json.load(file)

with open('values_high_special.json', 'r') as file:
    values_high_special = json.load(file)



def roll_dice(num_dice):
    """Simulates rolling a specific number of d6 dice."""
    return [random.randint(1, 6) for r in range(num_dice)]


def get_score(roll, mode):
    """Reads the score for the roll from a dictionary, depending on the mode."""
    key = ''
    for d in roll:
        key += str(d)

    if mode == 'low':
        score = values_low[key]
    elif mode == 'high_std':
        score = values_high_standard[key]
    elif mode == 'high_sp':
        score = values_high_special[key]

    return score


def player_turn_low(target_to_beat=None, num_rolls=3):
    """
    Simulates a turn in low mode:
    - 3 dice, max as many rolls as Player 1 used (num_rolls).
    - Bank ones and remove them from the pool.
    - If target_to_beat is set, stop if the current total is lower.
    """
    dice_pool = 3
    banked_ones = 0
    current_score = 18  # Initialize with max possible

    for roll_num in range(num_rolls):
        roll = roll_dice(dice_pool)

        # Check if there are 2 or more 6s in roll
        if roll.count(6) == 2:
            idx = roll.index(6)
            roll[idx] = 1
        elif roll.count(6) == 3:
            roll = [6, 1, 1]
        # Count ones to remove them from future rolls
        ones_in_roll = roll.count(1)
        banked_ones += ones_in_roll
        dice_pool -= ones_in_roll

        # Calculate current total score
        # (The banked ones are 1s, the others are from the last roll)
        remaining_dice_sum = sum([d for d in roll if d != 1])
        current_score = banked_ones + remaining_dice_sum

        # STOPPING CONDITIONS:
        # 1. Tschigg!
        if banked_ones == 3:
            return 3
        # 2. Strategic stop: We beat the target
        if target_to_beat and current_score < target_to_beat:
            return current_score

    return current_score


def player_turn_high_std(target_to_beat=None, num_rolls=3):
    """
    Simulates a turn in high standard mode:
    - 3 dice, max as many rolls as Player 1 used (num_rolls).
    - No banking of ones
    - If target_to_beat is set, stop if the current total is higher.
    """
    dice_pool = 3
    current_score = 0  # Initialize with min possible

    for roll_num in range(num_rolls):
        roll = roll_dice(dice_pool)

        # Calculate current total score
        current_score = sum(roll)

        # STOPPING CONDITIONS:
        # 1. Tschigg!
        if current_score == 3:
            return 999
        # 2. Strategic stop: We beat the target
        if target_to_beat and current_score > target_to_beat:
            return current_score

    return current_score


def player_turn_high_sp(target_to_beat=None, num_rolls=3):
    """
    Simulates a turn in high special mode:
    - 3 dice, max as many rolls as Player 1 used (num_rolls).
    - Bank ones and remove them from the pool.
    - If target_to_beat is set, stop if the current total is higher.
    """
    dice_pool = 3
    banked_ones = 0
    current_score = 0  # Initialize with min possible

    for roll_num in range(num_rolls):
        roll = roll_dice(dice_pool)

        # Check if there are 2 or more 6s in roll
        if roll.count(6) == 2:
            idx = roll.index(6)
            roll[idx] = 1
        elif roll.count(6) == 3:
            roll = [6, 1, 1]

        # Count ones to remove them from future rolls
        ones_in_roll = roll.count(1)
        banked_ones += ones_in_roll
        dice_pool -= ones_in_roll

        # Calculate current total score depending on number of 1s
        # (The banked ones are 100s and 10s, the others are from the last roll)
        if banked_ones == 0:
            current_score = sum(roll)
        if banked_ones == 1:
            remaining_dice = sorted([d for d in roll if d != 1], reverse=True)
            current_score = 100 + 10 * remaining_dice[0] + remaining_dice[1]
        if banked_ones == 2:
            remaining_dice = [d for d in roll if d != 1]
            current_score = 200 + 10 * remaining_dice[0]

        # STOPPING CONDITIONS:
        # 1. Tschigg!
        if banked_ones == 3:
            return 999
        # 2. Strategic stop: We beat the target
        if target_to_beat and current_score > target_to_beat:
            return current_score

    return current_score


def run_simulation(roll, num_rolls=3, num_games=100):
    wins = [0, 0, 0]
    mids = [0, 0, 0]
    losses = [0, 0, 0]
    mode = ['low', 'high_std', 'high_sp']

    for m in mode:
        for _ in range(num_games):
            # We start with our score depending on the roll
            my_score = get_score(roll, mode=m)

            if m == 'low':
                # Player 2 tries to beat our score
                p2_score = player_turn_low(target_to_beat=my_score, num_rolls=num_rolls)

                # Player 3 tries to beat the score
                current_low = min(my_score, p2_score)
                p3_score = player_turn_low(target_to_beat=current_low, num_rolls=num_rolls)

                # Check if we held the lowest score
                if my_score <= p2_score and my_score <= p3_score:
                    wins[0] += 1
                #Check if we held neither the lowest nor the highest score
                if (p2_score < my_score <= p3_score) or (p3_score < my_score <= p2_score):
                    mids[0] += 1
                #Check if we held the highest score
                if my_score > p2_score and my_score > p3_score:
                    losses[0] += 1

            elif m == 'high_std':
                # Player 2 tries to beat our score
                p2_score = player_turn_high_std(target_to_beat=my_score, num_rolls=num_rolls)

                # Player 3 tries to beat the score
                current_high = max(my_score, p2_score)
                p3_score = player_turn_high_std(target_to_beat=current_high, num_rolls=num_rolls)

                # Check if we held the highest score
                if my_score >= p2_score and my_score >= p3_score:
                    wins[1] += 1
                #Check if we held neither the highest nor the lowest score
                elif (p2_score > my_score >= p3_score) or (p3_score > my_score >= p2_score):
                    mids[1] += 1
                #Check if we held the lowest score
                elif my_score < p2_score and my_score < p3_score:
                    losses[1] += 1

            elif m == 'high_sp':
                # Player 2 tries to beat our score
                p2_score = player_turn_high_sp(target_to_beat=my_score, num_rolls=num_rolls)

                # Player 3 tries to beat the score
                current_high = max(my_score, p2_score)
                p3_score = player_turn_high_sp(target_to_beat=current_high, num_rolls=num_rolls)

                # Check if we held the highest score
                if my_score >= p2_score and my_score >= p3_score:
                    wins[2] += 1
                #Check if we held neither the highest nor the lowest score
                elif (p2_score > my_score >= p3_score) or (p3_score > my_score >= p2_score):
                    mids[2] += 1
                #Check if we held the lowest score
                elif my_score < p2_score and my_score < p3_score:
                    losses[2] += 1


    return wins, mids, losses

def display(roll, num_rolls, wins, mids, losses, num_games):
    score_low = get_score(roll, mode='low')
    score_high_std = get_score(roll, mode='high_std')
    score_high_sp = get_score(roll, mode='high_sp')

    headers = ['*', 'Low          ', 'High Standard', 'High Special']
    row1 = ['Score', score_low, score_high_std, score_high_sp]
    row2 = ['Win', f'{round(wins[0]/num_games * 100, 2)}%', f'{round(wins[1]/num_games * 100, 2)}%', f'{round(wins[2]/num_games * 100, 2)}%']
    row3 = ['Mid', f'{round(mids[0]/num_games * 100, 2)}%', f'{round(mids[1]/num_games * 100, 2)}%', f'{round(mids[2]/num_games * 100, 2)}%']
    row4 = ['Loss', f'{round(losses[0]/num_games * 100, 2)}%', f'{round(losses[1]/num_games * 100, 2)}%', f'{round(losses[2]/num_games * 100, 2)}%']

    print(f'\nRoll: {roll}  |  Max. Rolls: {num_rolls}  |  Number of Games: {num_games}\n')
    print(tabulate([row1, row2, row3, row4], headers=headers))


def main():
    roll = roll_dice(3)
    #roll = [6, 4, 3]
    num_rolls = 1
    num_games = 100

    wins, mids, losses = run_simulation(roll=roll, num_rolls=num_rolls, num_games=num_games)

    display(roll, num_rolls, wins, mids, losses, num_games)

main()