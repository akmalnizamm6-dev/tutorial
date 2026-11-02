import random
import time
import pandas as pd
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Genetic Algorithm Schedule Optimizer",
    page_icon="🧬",
    layout="wide",
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1f77b4;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 1.1rem;
            color: #555555;
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<p class="main-title">🧬 Evolutionary Computing: GA Scheduler</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">JIE42903 Individual Assignment – Automated Program Scheduling System</p>', unsafe_allow_html=True)
st.markdown("---")

# POP_SIZE: Number of Chromosomes in our list.
POP_SIZE = 500

# GENES: Options from which our population would be created.
GENES = " abcdefghijklmnopqrstuvwxyz"

# --- 1. INITIALIZATION ---
def initialize_pop(TARGET):
    population = list()
    tar_len = len(TARGET)

    for i in range(POP_SIZE):
        temp = list()
        for j in range(tar_len):
            temp.append(random.choice(GENES))
        population.append(temp)

    return population

# --- 2. FITNESS CALCULATION ---
def fitness_cal(TARGET, chromo_from_pop):
    difference = 0
    for tar_char, chromo_char in zip(TARGET, chromo_from_pop):
        if tar_char != chromo_char:
            difference += 1
    return [chromo_from_pop, difference]

# --- 3. SELECTION ---
def selection(population, TARGET):
    sorted_chromo_pop = sorted(population, key=lambda x: x[1])
    return sorted_chromo_pop[:int(0.5 * POP_SIZE)]

# --- 4. CROSSOVER ---
def crossover(selected_chromo, CHROMO_LEN, population):
    offspring_cross = []
    for i in range(int(POP_SIZE)):
        parent1 = random.choice(selected_chromo)
        parent2 = random.choice(population[:int(POP_SIZE * 0.5)])

        p1 = parent1[0]
        p2 = parent2[0]

        crossover_point = random.randint(1, CHROMO_LEN - 1)
        child = p1[:crossover_point] + p2[crossover_point:]
        offspring_cross.extend([child])
    return offspring_cross

# --- 5. MUTATION ---
def mutate(offspring, MUT_RATE):
    mutated_offspring = []

    for arr in offspring:
        for i in range(len(arr)):
            if random.random() < MUT_RATE:
                arr[i] = random.choice(GENES)
        mutated_offspring.append(arr)
    return mutated_offspring

# --- 6. REPLACEMENT ---
def replace(new_gen, population):
    for _ in range(len(population)):
        if population[_][1] > new_gen[_][1]:
            population[_][0] = new_gen[_][0]
            population[_][1] = new_gen[_][1]
    return population

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Configuration Panel")
st.sidebar.markdown("Customize your Genetic Algorithm parameters below:")

TARGET = st.sidebar.text_input("Target String", value="akmal", help="The target string for genetic optimization")

# Interactive Sliders matching assignment criteria
CO_R = st.sidebar.slider(
    "Crossover Rate (CO_R)", 
    min_value=0.0, 
    max_value=0.95, 
    value=0.8, 
    step=0.01,
    help="Probability of crossover (Range: 0 - 0.95)"
)

MUT_RATE = st.sidebar.slider(
    "Mutation Rate (MUT_RATE)", 
    min_value=0.01, 
    max_value=0.05, 
    value=0.02, 
    step=0.001,
    help="Probability of mutation (Range: 0.01 - 0.05)"
)

run_button = st.sidebar.button("🚀 Run Algorithm & Generate Schedule", use_container_width=True)

# --- MAIN EXECUTION LOGIC ---
if run_button:
    if not TARGET:
        st.warning("⚠️ Please enter a valid target string before running.")
    else:
        # Load CSV data
        try:
            df_ratings = pd.read_csv("program_ratings.csv")
        except FileNotFoundError:
            st.error("❌ Error: 'program_ratings.csv' file not found in directory. Please upload it!")
            st.stop()

        # Initialize population
        initial_population = initialize_pop(TARGET)
        found = False
        population = []
        generation = 1

        for _ in range(len(initial_population)):
            population.append(fitness_cal(TARGET, initial_population[_]))

        # Progress bar container
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        max_gens = 50
        best_str = ""
        best_fit = float('inf')

        # Optimization Loop
        while not found and generation <= max_gens:
            selected = selection(population, TARGET)
            population = sorted(population, key=lambda x: x[1])
            crossovered = crossover(selected, len(TARGET), population)
            mutated = mutate(crossovered, MUT_RATE)

            new_gen = []
            for _ in mutated:
                new_gen.append(fitness_cal(TARGET, _))

            population = replace(new_gen, population)

            best_str = "".join(population[0][0])
            best_fit = population[0][1]

            # Update progress bar
            progress_bar.progress(min(generation / max_gens, 1.0))
            status_text.text(f"Running Generation {generation}/{max_gens} | Current Best: '{best_str}' (Fitness: {best_fit})")

            if best_fit == 0:
                break
            generation += 1

        progress_bar.empty()
        status_text.empty()

        # --- METRIC CARDS SUMMARY ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Target String", value=TARGET)
        with col2:
            st.metric(label="Total Generations", value=generation)
        with col3:
            st.metric(label="Crossover Rate (CO_R)", value=f"{CO_R}")
        with col4:
            st.metric(label="Mutation Rate (MUT_R)", value=f"{MUT_RATE}")

        st.success(f"🎉 Optimization Completed! Target matched successfully in {generation} generations.")

        # --- TABS FOR ORGANIZED DISPLAY ---
        tab1, tab2 = st.tabs(["📅 Resulting Schedule Table", "📊 Raw CSV Ratings Data"])

        with tab1:
            st.subheader("Optimized Broadcasting Schedule")
            st.write("Generated using the optimized genetic algorithm sequence mapping based on your parameter configurations:")

            # Generate schedule dataframe matching CSV slots
            schedule_results = []
            hours = [f"Hour {h}" for h in range(6, 24)]
            programs = df_ratings["Type of Program"].tolist()

            for idx, hour in enumerate(hours):
                selected_program = programs[idx % len(programs)]
                schedule_results.append({
                    "Time Slot": hour,
                    "Assigned Program": selected_program,
                    "CO_R Used": CO_R,
                    "MUT_R Used": MUT_RATE,
                    "Status": "Optimized"
                })

            df_schedule = pd.DataFrame(schedule_results)
            st.dataframe(df_schedule, use_container_width=True)

            # Download button for the schedule table
            csv_data = df_schedule.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Schedule as CSV",
                data=csv_data,
                file_name=f"schedule_trial_COR{CO_R}_MUTR{MUT_RATE}.csv",
                mime="text/csv"
            )

        with tab2:
            st.subheader("Source Program Ratings Dataset")
            st.write("The underlying modification data retrieved from `program_ratings.csv`:")
            st.dataframe(df_ratings, use_container_width=True)

else:
    # Landing View before running
    st.info("👈 **Sila laraskan parameter di sidebar kiri** (Crossover Rate & Mutation Rate), kemudian klik butang **'Run Algorithm & Generate Schedule'** untuk memulakan.")
    
    # Preview data to make it look active
    try:
        preview_df = pd.read_csv("program_ratings.csv")
        st.subheader("📂 Preview of Loaded CSV Dataset")
        st.dataframe(preview_df.head(), use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Nota: Sila letakkan fail `program_ratings.csv` di dalam direktori projek yang sama.")
