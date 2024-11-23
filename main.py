import csv

# Read and filter valid five-letter solutions
six_letter_solutions = []
with open('possible_six_letter_guesses.txt') as f:
    lines = [line.strip() for line in f if line.strip()]  # Strip whitespace and skip empty lines

for word in lines:
    six_letter_solutions.append(word)

# Read and filter valid five-letter guesses
six_letter_guesses = []
with open('possible_six_letter_guesses.txt') as f:
    lines = [line.strip() for line in f if line.strip()]

for word in lines:
    six_letter_guesses.append(word)

# Initialize results dictionary
results = {solution: [] for solution in six_letter_solutions}

# Process each guess against each solution
for solution in six_letter_solutions:
    for guess in six_letter_guesses:
        # Create mutable list of solution letters
        solution_list = list(solution)
        string = ""

        # First pass: Mark exact matches
        for i in range(len(guess)):
            if guess[i] == solution_list[i]:
                string += "2"  # Correct position
                solution_list[i] = None  # Mark letter as used
            else:
                string += "0"

        # Second pass: Mark letters in the wrong position
        string = list(string)  # Convert to list for modification
        for i in range(len(guess)):
            if string[i] == "0" and guess[i] in solution_list:
                string[i] = "1"  # Wrong position
                solution_list[solution_list.index(guess[i])] = None  # Remove letter from available pool

        # Join and save result
        results[solution].append("".join(string))

# Write results to CSV
with open("six_letter_results.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Write header: solutions as columns
    writer.writerow(["Guess"] + six_letter_solutions)
    # Write each guess and its results
    for i, guess in enumerate(six_letter_guesses):
        row = [guess] + [results[solution][i] for solution in six_letter_solutions]
        writer.writerow(row)


