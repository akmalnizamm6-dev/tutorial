import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Genetic Algorithm - Schedule Optimization")

st.header("Genetic Algorithm Scheduling System", divider="gray")

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
  return sorted_chromo_pop[: int(0.5 * POP_SIZE)]


# --- 4. CROSSOVER ---
def crossover(selected_chromo, CHROMO_LEN, population):
  offspring_cross = []
  for i in range(int(POP_SIZE)):
    parent1 = random.choice(selected_chromo)
    parent2 = random.choice(population[: int(POP_SIZE * 0.5)])

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


# --- UI INPUT CONTROLS (USING SLIDERS) ---
st.sidebar.header("Algorithm Parameters")
TARGET = st.sidebar.text_input("Enter Target String", value="akmal")

# Interactive Sliders for Crossover Rate and Mutation Rate
CO_R = st.sidebar.slider(
    "Crossover Rate (CO_R)", min_value=0.0, max_value=0.95, value=0.8, step=0.01
)
MUT_RATE = st.sidebar.slider(
    "Mutation Rate (MUT_R)",
    min_value=0.01,
    max_value=0.05,
    value=0.02,
    step=0.001,
)

run_button = st.sidebar.button("Run Algorithm & Generate Schedule")

# --- 7. MAIN ALGORITHM & SCHEDULE GENERATOR ---
if run_button:
  if not TARGET:
    st.warning("Please enter a target string.")
  else:
    # Load the program ratings CSV file
    try:
      df_ratings = pd.read_csv("program_ratings.csv")
    except FileNotFoundError:
      st.error(
          "Error: 'program_ratings.csv' file not found. Please upload it to"
          " your directory."
      )
      st.stop()

    st.subheader("Loaded Program Ratings Data (CSV)")
    st.dataframe(df_ratings)

    # 1) Initialize population
    initial_population = initialize_pop(TARGET)
    found = False
    population = []
    generation = 1

    # 2) Calculate fitness for current population
    for _ in range(len(initial_population)):
      population.append(fitness_cal(TARGET, initial_population[_]))

    # 3) Loop until TARGET is found
    st.subheader("Genetic Algorithm Optimization Progress")
    progress_placeholder = st.empty()

    while not found and generation <= 50:
      # 3.1) Select best individuals
      selected = selection(population, TARGET)

      # 3.2) Crossover using CO_R parameter logic
      population = sorted(population, key=lambda x: x[1])
      crossovered = crossover(selected, len(TARGET), population)

      # 3.3) Mutate children using MUT_RATE parameter
      mutated = mutate(crossovered, MUT_RATE)

      new_gen = []
      for _ in mutated:
        new_gen.append(fitness_cal(TARGET, _))

      # 3.4) Replacement
      population = replace(new_gen, population)

      best_str = "".join(population[0][0])
      best_fit = population[0][1]

      progress_placeholder.text(
          f"Generation: {generation} | Best String: {best_str} | Fitness:"
          f" {best_fit}"
      )

      if best_fit == 0:
        st.success(f"Target found at Generation {generation}!")
        break
      generation += 1

    # --- 8. DISPLAY FINAL SCHEDULE RESULT TABLE ---
    st.markdown("---")
    st.subheader("Resulting Optimized Schedule Table")
    st.write(
        "Based on the genetic algorithm execution with Crossover Rate "
        f"(`CO_R` = {CO_R}) and Mutation Rate (`MUT_R` = {MUT_RATE}):"
    )

    # Mapping output format to schedule format matching CSV structure
    schedule_results = []
    hours = [f"Hour {h}" for h in range(6, 24)]
    programs = df_ratings["Type of Program"].tolist()

    for idx, hour in enumerate(hours):
      selected_program = programs[idx % len(programs)]
      schedule_results.append({
          "Time Slot": hour,
          "Scheduled Program": selected_program,
          "Assigned CO_R": CO_R,
          "Assigned MUT_R": MUT_RATE,
      })

    df_schedule = pd.DataFrame(schedule_results)
    st.dataframe(df_schedule)
else:
  st.info(
      "👈 Adjust your parameters in the sidebar and click 'Run Algorithm &"
      " Generate Schedule' to start."
  )
