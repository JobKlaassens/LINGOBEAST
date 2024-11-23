import csv
import os
import string
from collections import Counter
import math


# Function to read words and categorize them by starting character (a-z, 1)
def categorize_words_by_start(file_path):
    # Create categories for each letter (a-z) and '1'
    categorized_words = {char: [] for char in string.ascii_lowercase + "1"}

    with open(file_path) as f:
        lines = [line.strip() for line in f if line.strip()]

    for word in lines:
        first_char = word[0].lower()
        if first_char in categorized_words:
            categorized_words[first_char].append(word)

    return categorized_words


# Categorize six-letter solutions and guesses
six_letter_solutions_by_start = categorize_words_by_start('possible_six_letter_solutions.txt')
six_letter_guesses_by_start = categorize_words_by_start('possible_six_letter_guesses.txt')

# Process and write CSV for each starting character
for char in string.ascii_lowercase + "1":
    solutions = six_letter_solutions_by_start[char]
    guesses = six_letter_guesses_by_start[char]

    if not solutions or not guesses:
        continue  # Skip if there are no words for this starting character

    # Initialize results dictionary for this starting character
    results = {solution: [] for solution in solutions}

    # Process each guess against each solution
    for solution in solutions:
        for guess in guesses:
            # Create mutable list of solution letters
            solution_list = list(solution)
            score = ""

            # First pass: Mark exact matches
            for i in range(len(guess)):
                if guess[i] == solution_list[i]:
                    score += "2"  # Correct position
                    solution_list[i] = None  # Mark letter as used
                else:
                    score += "0"

            # Second pass: Mark letters in the wrong position
            score = list(score)  # Convert to list for modification
            for i in range(len(guess)):
                if score[i] == "0" and guess[i] in solution_list:
                    score[i] = "1"  # Wrong position
                    solution_list[solution_list.index(guess[i])] = None  # Remove letter from available pool

            # Join and save result
            results[solution].append("".join(score))

    # Write results to a CSV for this starting character
    csv_file_name = f"six_letter_results_{char}.csv"
    with open(csv_file_name, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header: solutions as columns
        writer.writerow(["Guess"] + solutions)
        # Write each guess and its results
        for i, guess in enumerate(guesses):
            row = [guess] + [results[solution][i] for solution in solutions]
            writer.writerow(row)


# Function to analyze CSV and calculate weighted averages
def analyze_csv_weighted_avg_log(file_path, output_csv):
    guess_analysis = {}

    # Read the CSV file
    with open(file_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header row

        # Process each row in the CSV
        for row in reader:
            guess = row[0]  # The guessed word
            results = row[1:]  # The result strings for this guess

            # Count occurrences of each string for this guess
            if guess not in guess_analysis:
                guess_analysis[guess] = Counter()

            guess_analysis[guess].update(results)

    # Compute weighted averages of logs
    guess_weighted_logs = {}
    for guess, counts in guess_analysis.items():
        total = sum(counts.values())
        fractions = {result: count / total for result, count in counts.items()}
        logs = {result: math.log2(1 / fraction) for result, fraction in fractions.items()}

        # Weighted average of logs
        weighted_avg_log = sum(fraction * logs[result] for result, fraction in fractions.items())
        guess_weighted_logs[guess] = weighted_avg_log

    # Sort guesses by weighted average log in descending order
    sorted_guesses = sorted(guess_weighted_logs.items(), key=lambda x: x[1], reverse=True)

    # Save the weighted average logs to a CSV
    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Guess", "Weighted Avg Log"])

        for guess, weighted_log in sorted_guesses:
            writer.writerow([guess, weighted_log])


# Analyze each CSV file for each starting character
for char in string.ascii_lowercase + "1":
    csv_file_name = f"six_letter_results_{char}.csv"
    output_csv_name = f"six_letter_logs_{char}.csv"


    analyze_csv_weighted_avg_log(csv_file_name, output_csv_name)
    print(f"Analysis complete for starting character '{char}', saved to {output_csv_name}")