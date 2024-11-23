import tkinter as tk
from tkinter import simpledialog, messagebox
import csv
import math
from collections import Counter

class LingoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lingo Game")

        # Default settings
        self.word_length = 5  # Default to 5-letter words
        self.first_letter = ''
        self.possible_words = []
        self.remaining_words = []
        self.word_logs = {}

        # Feedback related
        self.feedback = [0] * self.word_length  # Initial feedback state
        self.letter_vars = []
        self.letter_buttons = []

        # Initialize the UI
        self.init_ui()

    def init_ui(self):
        # Initialize the main UI elements
        self.container = tk.Frame(self.root)
        self.container.pack(padx=10, pady=10)

        # Start the game setup
        self.reset_game()

    def reset_game(self):
        # Clear any existing content
        for widget in self.container.winfo_children():
            widget.destroy()

        # Ask user for word length and first letter
        self.ask_word_length()

    def ask_word_length(self):
        # Ask for word length (5 or 6)
        word_length = simpledialog.askinteger("Word Length", "Is it a 5 or 6 letter word?", minvalue=5, maxvalue=6)
        if not word_length:
            return
        self.word_length = word_length
        self.feedback = [0] * self.word_length  # Reset feedback for the new word length

        # Ask for the first letter
        first_letter = simpledialog.askstring("First Letter", "Enter the first letter:").lower()
        if not first_letter or len(first_letter) != 1:
            return
        self.first_letter = first_letter

        # Load words and set up the board
        self.load_words()
        self.setup_board()

    def load_words(self):
        # Load precomputed word logs
        self.word_logs = self.load_precomputed_logs(self.first_letter, self.word_length)
        self.possible_words = list(self.word_logs.keys())
        self.remaining_words = self.possible_words.copy()

    def setup_board(self):
        # Create a board for letters
        self.board_frame = tk.Frame(self.container)
        self.board_frame.pack(side=tk.LEFT, padx=10)

        # Initialize grid for letters
        self.letter_vars = [tk.StringVar() for _ in range(self.word_length)]
        self.letter_buttons = []

        for i in range(self.word_length):
            var = self.letter_vars[i]
            var.set(self.first_letter.upper() if i == 0 else "")  # Set first letter

            button = tk.Button(
                self.board_frame,
                textvariable=var,
                width=2,
                font=("Arial", 24),
                justify="center",
                command=lambda idx=i: self.cycle_feedback(idx)
            )
            button.grid(row=0, column=i, padx=5)

            if i == 0:
                button.config(state="disabled")  # Disable the first letter button

            self.letter_buttons.append(button)

        # Create possible word display and info
        self.create_word_list_display()
        self.create_info_display()

        # Add Confirm Feedback button
        self.confirm_button = tk.Button(self.container, text="Confirm Feedback", command=self.apply_feedback)
        self.confirm_button.pack(pady=10)

    def create_word_list_display(self):
        # Display possible words
        self.word_list_frame = tk.Frame(self.container)
        self.word_list_frame.pack(side=tk.LEFT, padx=10)

        self.word_listbox = tk.Listbox(self.word_list_frame, font=("Arial", 12), width=20, height=15)
        self.word_listbox.pack(side=tk.LEFT, fill=tk.Y)

        # Add scrollbar
        scrollbar = tk.Scrollbar(self.word_list_frame, orient="vertical")
        scrollbar.config(command=self.word_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.word_listbox.config(yscrollcommand=scrollbar.set)

        # Display words with log values
        self.update_word_list()
        self.word_listbox.bind('<<ListboxSelect>>', self.on_word_selected)

    def create_info_display(self):
        # Create info display
        self.info_frame = tk.Frame(self.container)
        self.info_frame.pack(side=tk.LEFT, padx=10)

        self.info_label = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.info_label.pack(pady=5)

        self.update_info_display()

    def update_info_display(self):
        # Show remaining possibilities and bits of information
        num_possibilities = len(self.remaining_words)
        bits_info = round(math.log2(num_possibilities), 2) if num_possibilities > 0 else 0
        self.info_label.config(text=f"Possibilities: {num_possibilities}\nBits of Info: {bits_info}")

    def cycle_feedback(self, index):
        # Cycle through feedback states: 0 (white) -> 1 (yellow) -> 2 (green)
        print(f"Button clicked at index {index}")  # Debugging print
        self.feedback[index] = (self.feedback[index] + 1) % 3
        print(f"Feedback for index {index} is now {self.feedback[index]}")  # Debugging print
        self.update_feedback_display(index)

    def update_feedback_display(self, index):
        # Update the color based on feedback
        colors = {0: "#FFFFFF", 1: "#FFD700", 2: "#32CD32"}  # white, yellow, green
        color = colors[self.feedback[index]]
        print(f"Updating button at index {index} to color {color}")  # Debugging print

        # Force a color change
        self.letter_buttons[index].config(bg=color)
        self.letter_buttons[index].update_idletasks()  # Force UI to refresh

    def update_word_list(self):
        # Update the list of possible words
        self.word_listbox.delete(0, tk.END)
        for word in self.remaining_words:
            log_info = round(self.word_logs[word], 2)
            self.word_listbox.insert(tk.END, f"{word} - {log_info}")

    def on_word_selected(self, event):
        # Handle word selection
        if not self.word_listbox.curselection():
            return
        index = self.word_listbox.curselection()[0]
        selected_word = self.word_listbox.get(index).split(" - ")[0]

        for i, letter in enumerate(selected_word):
            self.letter_vars[i].set(letter.upper())

        self.feedback = [0] * self.word_length
        self.update_feedback_display_all()

    def update_feedback_display_all(self):
        # Update colors of all entries
        for i in range(self.word_length):
            self.update_feedback_display(i)

    def apply_feedback(self):
        # Apply feedback to filter words
        if all(f == 2 for f in self.feedback):
            messagebox.showinfo("Congratulations", "You guessed the word correctly!")
            return

        feedback_str = "".join(map(str, self.feedback))  # Convert feedback to string format (e.g., "21020")
        selected_word = "".join(var.get().lower() for var in self.letter_vars)  # Get the current guess

        # Filter the remaining words based on feedback
        self.remaining_words = self.filter_words(self.remaining_words, selected_word, feedback_str)

        if not self.remaining_words:
            messagebox.showerror("No Words", "No possible words left. Please check the feedback.")
            return

        # Calculate the next best guess
        next_guess, _ = self.calculate_weighted_avg_log(self.remaining_words, self.remaining_words)
        self.update_word_list()  # Update the list of possible words
        self.update_info_display()  # Update the possibilities info display

        # Pre-fill the next guess letters for user
        for i, letter in enumerate(next_guess):
            self.letter_vars[i].set(letter.upper())
        self.feedback = [0] * self.word_length  # Reset feedback for next round
        self.update_feedback_display_all()

    # Modified filter and calculation functions
    def filter_words(self, possible_words, guess, feedback):
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

    def calculate_weighted_avg_log(self, remaining_solutions, guesses):
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
    def load_precomputed_logs(self, first_letter, word_length):
        # Loads the precomputed log scores for the words starting with the given letter and length.
        if word_length == 5:
            log_file = f"five_letter_logs_{first_letter}.csv"
        else:
            log_file = f"six_letter_logs_{first_letter}.csv"
        word_logs = {}

        try:
            with open(log_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                for row in reader:
                    word_logs[row[0]] = float(row[1])  # word, log_score
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"Precomputed file {log_file} not found!")

        return word_logs

if __name__ == "__main__":
    root = tk.Tk()
    app = LingoGUI(root)
    root.mainloop()