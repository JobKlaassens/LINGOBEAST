import streamlit as st
import csv
import math
from collections import Counter
import os


# --- JOUW ORIGINELE LOGICA FUNCTIES ---

def load_precomputed_logs(first_letter, word_length):
    # Let op: Zorg dat je CSV bestanden in dezelfde map staan op GitHub
    if word_length == 5:
        log_file = f"five_letter_logs_{first_letter}.csv"
    else:
        log_file = f"six_letter_logs_{first_letter}.csv"

    word_logs = {}
    try:
        with open(log_file, "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                word_logs[row[0]] = float(row[1])
    except FileNotFoundError:
        st.error(f"Kan bestand {log_file} niet vinden. Zorg dat deze geüpload is.")
        return {}
    return word_logs


def filter_words(possible_words, guess, feedback):
    filtered_words = []
    for word in possible_words:
        solution_list = list(word)
        guess_list = list(guess)
        matches = [0] * len(guess)

        # Stap 1: Groen (2)
        for i in range(len(guess)):
            if guess_list[i] == solution_list[i]:
                matches[i] = 2
                solution_list[i] = None

                # Stap 2: Geel (1)
        for i in range(len(guess)):
            if matches[i] == 0 and guess_list[i] in solution_list:
                matches[i] = 1
                solution_list[solution_list.index(guess_list[i])] = None

        if "".join(map(str, matches)) == feedback:
            filtered_words.append(word)
    return filtered_words


def calculate_weighted_avg_log(remaining_solutions, guesses):
    # Dit kan traag zijn in de browser als de lijst lang is,
    # dus we tonen een laadbalkje of beperken het.
    guess_analysis = {guess: Counter() for guess in guesses}

    for solution in remaining_solutions:
        for guess in guesses:
            solution_list = list(solution)
            guess_list = list(guess)
            feedback = ["0"] * len(guess)

            for i in range(len(guess)):
                if guess_list[i] == solution_list[i]:
                    feedback[i] = "2"
                    solution_list[i] = None

            for i in range(len(guess)):
                if feedback[i] == "0" and guess_list[i] in solution_list:
                    feedback[i] = "1"
                    solution_list[solution_list.index(guess_list[i])] = None

            guess_analysis[guess].update(["".join(feedback)])

    guess_weighted_logs = {}
    for guess, counts in guess_analysis.items():
        total = sum(counts.values())
        fractions = {result: count / total for result, count in counts.items()}
        logs = {result: math.log2(1 / fraction) for result, fraction in fractions.items()}
        weighted_avg_log = sum(fraction * logs[result] for result, fraction in fractions.items())
        guess_weighted_logs[guess] = weighted_avg_log

    if not guess_weighted_logs:
        return None, {}

    best_guess = max(guess_weighted_logs, key=guess_weighted_logs.get)
    return best_guess, guess_weighted_logs


# --- DE WEBSITE INTERFACE ---

st.title("🦁 LingoBeast Online")
st.write("De ultieme Lingo raadmachine.")

# Sessie status bijhouden (geheugen van de website)
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'possible_words' not in st.session_state:
    st.session_state.possible_words = []
if 'current_guess' not in st.session_state:
    st.session_state.current_guess = ""

# Stap 1: Setup
if st.session_state.step == 1:
    col1, col2 = st.columns(2)
    with col1:
        length = st.radio("Woordlengte", [5, 6])
    with col2:
        first_letter = st.text_input("Eerste letter", max_chars=1).lower()

    if st.button("Start Spel"):
        if first_letter and len(first_letter) == 1:
            st.session_state.length = length
            st.session_state.first_letter = first_letter

            # Laad woorden
            logs = load_precomputed_logs(first_letter, length)
            if logs:
                st.session_state.possible_words = list(logs.keys())
                # Beste eerste gok bepalen
                st.session_state.current_guess = max(logs, key=logs.get)
                st.session_state.step = 2
                st.rerun()  # Herlaad de pagina
        else:
            st.warning("Vul een geldige eerste letter in.")

# Stap 2: Het spel
elif st.session_state.step == 2:
    st.info(f"Woordlengte: {st.session_state.length} | Eerste letter: {st.session_state.first_letter.upper()}")

    st.markdown(f"### 💡 Advies: Gok **{st.session_state.current_guess.upper()}**")

    st.write("Vul de feedback in die je van Lingo krijgt:")
    st.caption("0 = Grijs (fout), 1 = Geel (andere plek), 2 = Groen (goed)")

    feedback = st.text_input("Feedback code (bijv. 21020)", max_chars=st.session_state.length)

    if st.button("Verwerk Feedback"):
        if len(feedback) == st.session_state.length and feedback.isdigit():
            if feedback == "2" * st.session_state.length:
                st.balloons()
                st.success("Gefeliciteerd! We hebben hem!")
                if st.button("Nieuw Spel"):
                    st.session_state.step = 1
                    st.rerun()
            else:
                # Filter woorden
                old_count = len(st.session_state.possible_words)
                st.session_state.possible_words = filter_words(
                    st.session_state.possible_words,
                    st.session_state.current_guess,
                    feedback
                )
                new_count = len(st.session_state.possible_words)

                st.write(f"Mogelijkheden gingen van {old_count} naar {new_count}.")

                if new_count == 0:
                    st.error("Geen woorden meer over! Check je feedback input.")
                elif new_count == 1:
                    st.success(f"Het woord is: {st.session_state.possible_words[0].upper()}")
                else:
                    # Bereken nieuwe beste gok
                    with st.spinner('Beast is aan het rekenen...'):
                        # Optimalisatie: als er nog heel veel woorden zijn, reken dan niet alles door om tijd te besparen
                        subset = st.session_state.possible_words[:500]
                        best, _ = calculate_weighted_avg_log(st.session_state.possible_words, subset)
                        st.session_state.current_guess = best
                        st.rerun()
        else:
            st.warning(f"Feedback moet precies {st.session_state.length} cijfers bevatten (0, 1 of 2).")

    # Toon lijst met mogelijke woorden (optioneel)
    with st.expander("Zie overgebleven woorden"):
        st.write(st.session_state.possible_words)