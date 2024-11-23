import csv
import math
from collections import Counter

def load_precomputed_logs(first_letter, word_length):
    """
    Loads the precomputed log scores for the words starting with the given letter and length.
    """
    if word_length == 5:
        log_file = f"five_letter_logs_{first_letter}.csv"
    else:
        log_file = f"six_letter_logs_{first_letter}.csv"
    word_logs = {}

    # Read precomputed logs
    with open(log_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row

        for row in reader:
            word_logs[row[0]] = float(row[1])  # {word: log_score}

    return word_logs

def filter_words(possible_words, guess, feedback):
    """
    Filters the list of possible words based on feedback from the last guess.
    Feedback is a string of 0, 1, 2 indicating correctness of each position.
    """
    filtered_words = []

    for word in possible_words:
        solution_list = list(word)
        guess_list = list(guess)
        matches = [0] * len(guess)

        # First pass: Check exact matches (2)
        for i in range(len(guess)):
            if guess_list[i] == solution_list[i]:
                matches[i] = 2
                solution_list[i] = None  # Mark as used

        # Second pass: Check partial matches (1)
        for i in range(len(guess)):
            if matches[i] == 0 and guess_list[i] in solution_list:
                matches[i] = 1
                solution_list[solution_list.index(guess_list[i])] = None  # Mark as used

        # Convert matches to string and compare with feedback
        if "".join(map(str, matches)) == feedback:
            filtered_words.append(word)

    return filtered_words

def calculate_weighted_avg_log(remaining_solutions, guesses):
    """
    Recalculates the log scores for each guess based on the remaining possible solutions.
    """
    guess_analysis = {guess: Counter() for guess in guesses}

    # Compute feedback for every guess-solution combination
    for solution in remaining_solutions:
        for guess in guesses:
            solution_list = list(solution)
            guess_list = list(guess)
            feedback = ["0"] * len(guess)

            # First pass: Check exact matches (2)
            for i in range(len(guess)):
                if guess_list[i] == solution_list[i]:
                    feedback[i] = "2"
                    solution_list[i] = None  # Mark as used

            # Second pass: Check partial matches (1)
            for i in range(len(guess)):
                if feedback[i] == "0" and guess_list[i] in solution_list:
                    feedback[i] = "1"
                    solution_list[solution_list.index(guess_list[i])] = None  # Mark as used

            feedback_str = "".join(feedback)
            guess_analysis[guess].update([feedback_str])

    # Compute weighted averages
    guess_weighted_logs = {}
    for guess, counts in guess_analysis.items():
        total = sum(counts.values())
        fractions = {result: count / total for result, count in counts.items()}
        logs = {result: math.log2(1 / fraction) for result, fraction in fractions.items()}

        # Weighted average of logs
        weighted_avg_log = sum(fraction * logs[result] for result, fraction in fractions.items())
        guess_weighted_logs[guess] = weighted_avg_log

    # Return the best guess based on the highest weighted average log
    best_guess = max(guess_weighted_logs, key=guess_weighted_logs.get)
    return best_guess, guess_weighted_logs

def get_feedback(guess, solution):
    """
    Generates feedback for a guess based on the solution.
    Feedback is a string of 0, 1, 2 indicating correctness of each position.
    """
    solution_list = list(solution)
    guess_list = list(guess)
    feedback = ["0"] * len(guess)

    # First pass: Check exact matches (2)
    for i in range(len(guess)):
        if guess_list[i] == solution_list[i]:
            feedback[i] = "2"
            solution_list[i] = None  # Mark as used

    # Second pass: Check partial matches (1)
    for i in range(len(guess)):
        if feedback[i] == "0" and guess_list[i] in solution_list:
            feedback[i] = "1"
            solution_list[solution_list.index(guess_list[i])] = None  # Mark as used

    return "".join(feedback)

def play_lingo_auto(word_length):
    results = []

    # Iterate through all possible first letters
    for first_letter in "abcdefghijklmnopqrstuvwxyz1":
        try:
            word_logs = load_precomputed_logs(first_letter, word_length)
        except FileNotFoundError:
            continue

        # List of words to use as solutions
        solutions = list(word_logs.keys())

        for solution in solutions:
            possible_words = list(word_logs.keys())
            current_guess = max(word_logs, key=word_logs.get)
            attempts = 0

            while current_guess != solution:
                attempts += 1
                feedback = get_feedback(current_guess, solution)

                # Filter remaining possible solutions based on feedback
                possible_words = filter_words(possible_words, current_guess, feedback)

                if not possible_words:
                    print(f"Error: No possible words remaining for solution {solution}")
                    break

                # Recalculate logs for remaining words
                best_guess, _ = calculate_weighted_avg_log(possible_words, possible_words)
                current_guess = best_guess

            # Log the results
            results.append({"word": solution, "attempts": attempts + 1})

    # Save results to a CSV file
    output_file = f"lingo_results_{word_length}_letters.csv"
    with open(output_file, "w", newline='') as csvfile:
        fieldnames = ["word", "attempts"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_file}.")

def run_tests():
    # Test for 5-letter words
    print("Running tests for 5-letter words...")
    play_lingo_auto(5)

    # Test for 6-letter words
    print("Running tests for 6-letter words...")
    play_lingo_auto(6)

run_tests()