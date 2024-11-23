import csv
from collections import Counter


def analyze_guess_frequencies(word_length):
    # File to read results from
    input_file = f"lingo_results_{word_length}_letters.csv"

    # Counter to store the frequency of each number of guesses
    guess_counter = Counter()

    try:
        with open(input_file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                attempts = int(row["attempts"])
                guess_counter[attempts] += 1

    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # Display the frequency of each number of guesses
    print(f"Frequency of guesses for {word_length}-letter words:")
    for attempts, frequency in sorted(guess_counter.items()):
        print(f"{attempts} guesses: {frequency} times")

    # Optionally, save results to a CSV file
    output_file = f"guess_frequencies_{word_length}_letters.csv"
    with open(output_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Number of Guesses", "Frequency"])
        for attempts, frequency in sorted(guess_counter.items()):
            writer.writerow([attempts, frequency])

    print(f"Frequency analysis saved to {output_file}.\n")


def run_analysis():
    # Analyze both 5-letter and 6-letter word data
    analyze_guess_frequencies(5)
    analyze_guess_frequencies(6)


run_analysis()