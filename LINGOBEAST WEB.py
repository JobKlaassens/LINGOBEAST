import streamlit as st
import csv
import math
from collections import Counter

# --- CONFIGURATIE ---
st.set_page_config(page_title="LingoBeast", page_icon="🦁")

# --- CSS STYLING VOOR DE BLOKJES ---
# Dit stukje CSS zorgt ervoor dat de knoppen vierkant lijken en grotere letters hebben
st.markdown("""
<style>
    div.stButton > button:first-child {
        height: 3em;
        width: 100%;
        font-size: 24px !important;
        font-weight: bold;
        border: 2px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIES (LOGICA) ---

def load_precomputed_logs(first_letter, word_length):
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
        st.error(f"Bestand {log_file} niet gevonden.")
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
    guess_analysis = {guess: Counter() for guess in guesses}
    
    # We beperken de analyse als er nog heel veel woorden zijn voor snelheid
    if len(remaining_solutions) > 500:
         guesses_to_check = guesses[:500]
    else:
         guesses_to_check = guesses

    for solution in remaining_solutions:
        for guess in guesses_to_check:
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

st.title("🦁 LingoBeast")

# Initialiseer Sessie Status
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'possible_words' not in st.session_state:
    st.session_state.possible_words = []
if 'current_guess' not in st.session_state:
    st.session_state.current_guess = ""
if 'feedback_colors' not in st.session_state:
    st.session_state.feedback_colors = [] # Lijst met 0, 1 of 2

# Helper functie om kleuren te cyclen (0->1->2->0)
def cycle_color(index):
    st.session_state.feedback_colors[index] = (st.session_state.feedback_colors[index] + 1) % 3

# --- STAP 1: SETUP ---
if st.session_state.step == 1:
    st.write("Start een nieuw spel:")
    col1, col2 = st.columns(2)
    with col1:
        length = st.radio("Aantal letters", [5, 6])
    with col2:
        first_letter = st.text_input("Eerste letter", max_chars=1).lower()

    if st.button("🚀 Start Beast"):
        if first_letter and len(first_letter) == 1:
            st.session_state.length = length
            st.session_state.first_letter = first_letter
            
            logs = load_precomputed_logs(first_letter, length)
            if logs:
                st.session_state.possible_words = list(logs.keys())
                st.session_state.current_guess = max(logs, key=logs.get)
                # Reset kleuren: Eerste letter groen (2), rest grijs (0)
                st.session_state.feedback_colors = [2] + [0] * (length - 1)
                st.session_state.step = 2
                st.rerun()
        else:
            st.warning("Vul een geldige letter in.")

# --- STAP 2: SPELEN ---
elif st.session_state.step == 2:
    st.write(f"**{len(st.session_state.possible_words)}** woorden over.")
    
    st.markdown("### Klik op de letters om de kleur te wijzigen:")
    
    # Hier maken we de interactieve knoppen
    # We gebruiken kolommen om ze naast elkaar te zetten
    cols = st.columns(st.session_state.length)
    
    current_word = st.session_state.current_guess.upper()
    
    for i, col in enumerate(cols):
        status = st.session_state.feedback_colors[i]
        letter = current_word[i]
        
        # Bepaal emoji/kleur op basis van status
        if status == 2:
            display_text = f"{letter}\n🟩" # Groen
        elif status == 1:
            display_text = f"{letter}\n🟨" # Geel
        else:
            display_text = f"{letter}\n⬛" # Grijs/Zwart
            
        # Maak de knop. on_click zorgt dat de functie 'cycle_color' wordt aangeroepen
        col.button(display_text, key=f"btn_{i}", on_click=cycle_color, args=(i,))

    st.write("") # Witregel
    
    # Bevestig knop
    if st.button("✅ Volgende Gok Berekenen"):
        # Zet de kleurenlijst om naar een string "21020"
        feedback_str = "".join(map(str, st.session_state.feedback_colors))
        
        if feedback_str == "2" * st.session_state.length:
            st.balloons()
            st.success(f"Gefeliciteerd! Het woord was {st.session_state.current_guess.upper()}!")
            if st.button("Opnieuw Spelen"):
                st.session_state.step = 1
                st.rerun()
        else:
            # Filteren
            st.session_state.possible_words = filter_words(
                st.session_state.possible_words, 
                st.session_state.current_guess, 
                feedback_str
            )
            
            if not st.session_state.possible_words:
                st.error("Geen woorden meer mogelijk! Heb je de feedback goed ingevuld?")
            else:
                # Nieuwe gok berekenen
                with st.spinner("Beast is aan het rekenen..."):
                    best, _ = calculate_weighted_avg_log(st.session_state.possible_words, st.session_state.possible_words)
                    st.session_state.current_guess = best
                    # Reset kleuren voor de nieuwe ronde (eerste letter groen behouden is vaak handig, maar reset is veiliger)
                    st.session_state.feedback_colors = [2] + [0] * (st.session_state.length - 1)
                    st.rerun()

    # Reset knop voor als je vastloopt
    st.markdown("---")
    if st.button("Spel Resetten"):
        st.session_state.step = 1
        st.rerun()
