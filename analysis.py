import csv
from collections import Counter
import math

def analyze_csv_weighted_avg_log(file_path, output_csv):
    """
    Reads the CSV file, calculates the fraction of each result string for each guessed word,
    computes log2(1/fraction) for each fraction, and then calculates the weighted average
    of the logs for each guess. Sorts the results by the highest weighted average log and
    saves to an output CSV.

    Args:
    - file_path (str): Path to the input CSV file.
    - output_csv (str): Path to the output CSV file where weighted averages will be saved.

    Returns:
    - None
    """
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

    print(f"Weighted average logs sorted and saved to {output_csv}.")

# Example usage:
file_path = "six_letter_results.csv"
output_csv = "six_letter_logs.csv"
analyze_csv_weighted_avg_log(file_path, output_csv)