import streamlit as st
import csv
import math
from collections import Counter

st.set_page_config(page_title="LingoBeast", page_icon="🦁")

st.markdown("""
<style>
    div.stButton > button:first-child {
        height: 3em;
        width: 100%;
        font-size: 24px !important;
        font-weight: bold;
        border: 2px solid #333;
    }
    
    div[data-testid="stHorizontalBlock"] button {
        height: auto;
        font-size: 16px !important;
        font-weight: normal;
        border: 1px solid #ccc;
    }
    
    .footer {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

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

        for i in range(len(guess)):
            if guess_list[i] == solution_list[i]:
                matches[i] = 2
                solution_list[i] = None 

        for i in range(len(guess)):
            if matches[i] == 0 and guess_list[i] in solution_list:
                matches[i] = 1
                solution_list[solution_list.index(guess_list[i])] = None 

        if "".join(map(str, matches)) == feedback:
            filtered_words.append(word)
    return filtered_words

def calculate_weighted_avg_log(remaining_solutions, guesses):
    guess_analysis = {guess: Counter() for guess in guesses}
    
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

st.title("🦁 LingoBeast")

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'possible_words' not in st.session_state:
    st.session_state.possible_words = []
if 'current_guess' not in st.session_state:
    st.session_state.current_guess = ""
if 'feedback_colors' not in st.session_state:
    st.session_state.feedback_colors = [] 
if 'latest_scores' not in st.session_state:
    st.session_state.latest_scores = {}

def cycle_color(index):
    st.session_state.feedback_colors[index] = (st.session_state.feedback_colors[index] + 1) % 3

def switch_word(new_word):
    st.session_state.current_guess = new_word
    st.session_state.feedback_colors = [2] + [0] * (st.session_state.length - 1)

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
                st.session_state.latest_scores = logs
                st.session_state.current_guess = max(logs, key=logs.get)
                st.session_state.feedback_colors = [2] + [0] * (length - 1)
                st.session_state.step = 2
                st.rerun()
        else:
            st.warning("Vul een geldige letter in.")

elif st.session_state.step == 2:
    st.write(f"**{len(st.session_state.possible_words)}** woorden over.")
    
    st.markdown("### Huidige gok:")
    cols = st.columns(st.session_state.length)
    current_word = st.session_state.current_guess.upper()
    
    for i, col in enumerate(cols):
        status = st.session_state.feedback_colors[i]
        letter = current_word[i] if i < len(current_word) else "?"
        
        if status == 2:
            display_text = f"{letter}\n🟩" 
        elif status == 1:
            display_text = f"{letter}\n🟨"
        else:
            display_text = f"{letter}\n⬛"
            
        col.button(display_text, key=f"btn_{i}", on_click=cycle_color, args=(i,))

    sorted_scores = sorted(st.session_state.latest_scores.items(), key=lambda x: x[1], reverse=True)
    alternatives = [item for item in sorted_scores if item[0] != st.session_state.current_guess][:5]

    if alternatives:
        st.markdown("---")
        st.write("👇 *Liever een ander woord? Klik om te kiezen:*")
        alt_cols = st.columns(len(alternatives))
        
        for idx, (alt_word, score) in enumerate(alternatives):
            if alt_cols[idx].button(f"{alt_word.upper()}"):
                switch_word(alt_word)
                st.rerun()
    
    st.markdown("---")

    if st.button("✅ Feedback Bevestigen", type="primary"):
        feedback_str = "".join(map(str, st.session_state.feedback_colors))
        
        if feedback_str == "2" * st.session_state.length:
            st.balloons()
            st.success(f"Gefeliciteerd! Het woord was {st.session_state.current_guess.upper()}!")
            if st.button("Opnieuw Spelen"):
                st.session_state.step = 1
                st.rerun()
        else:
            st.session_state.possible_words = filter_words(
                st.session_state.possible_words, 
                st.session_state.current_guess, 
                feedback_str
            )
            
            if not st.session_state.possible_words:
                st.error("Geen woorden meer mogelijk! Heb je de feedback goed ingevuld?")
            else:
                with st.spinner("Beast is aan het rekenen..."):
                    best, scores = calculate_weighted_avg_log(st.session_state.possible_words, st.session_state.possible_words)
                    
                    st.session_state.current_guess = best
                    st.session_state.latest_scores = scores
                    st.session_state.feedback_colors = [2] + [0] * (st.session_state.length - 1)
                    st.rerun()

    if st.button("Spel Resetten"):
        st.session_state.step = 1
        st.rerun()

st.markdown("---")
st.markdown(
    """
    <div class="footer">
        🦁 Programma gemaakt door <b>Job Klaassens</b>
    </div>
    """,
    unsafe_allow_html=True
)
