import random
import time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Genetic Algorithm Schedule Optimizer",
    page_icon="🧬",
    layout="wide",
)

# Custom Styling / Header
st.title("🧬 Genetic Algorithm Scheduling & Optimization System")
st.markdown(
    "Welcome! This interactive web application optimizes TV program schedules"
    " using **Genetic Algorithms** based on program ratings and user-defined"
    " parameters."
)
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


# --- SIDEBAR UI CONTROLS ---
st.sidebar.header("⚙️ Algorithm Configuration")
st.sidebar.markdown("Tune your evolutionary parameters below:")

TARGET = st.sidebar.text_input(
    "Target String (Fitness Goal)", value="akmal", help="The target text string the algorithm tries to evolve towards."
)

# Interactive Sliders
CO_R = st.sidebar.slider(
    "Crossover Rate (CO_R)",
    min_value=0.0,
    max_value=0.95,
    value=0.8,
    step=0.01,
    help="Probability of crossover between parent chromosomes.",
)

MUT_RATE = st.sidebar.slider(
    "Mutation Rate (MUT_RATE)",
    min_value=0.01,
    max_value=0.05,
    value=0.02,
    step=0.001,
    help="Probability of gene mutation.",
)

run_button = st.sidebar.button(
    "🚀 Run Optimization", type="primary", use_container_width=True
)

# --- MAIN EXECUTION ---
if run_button:
  if not TARGET:
    st.warning("⚠️ Please enter a valid target string.")
  else:
    # Load CSV file with spinner feedback
    with st.spinner("Loading program ratings data..."):
      try:
        df_ratings = pd.read_csv("program_ratings.csv")
      except FileNotFoundError:
        st.error(
            "❌ Error: 'program_ratings.csv' file not found in the directory."
            " Please upload it."
        )
        st.stop()

    # Display dataset info in an expandable section
    with st.expander("📊 View Raw Program Ratings Dataset (CSV)", expanded=False):
      st.dataframe(df_ratings, use_container_width=True)

    # 1) Initialize population
    initial_population = initialize_pop(TARGET)
    found = False
    population = []
    generation = 1
    fitness_history = []

    # 2) Calculate fitness for current population
    for _ in range(len(initial_population)):
      population.append(fitness_cal(TARGET, initial_population[_]))

    # Progress Bar & Status UI
    st.subheader("🔄 Optimization Progress")
    progress_bar = st.progress(0)
    status_text = st.empty()

    max_generations = 60
    while not found and generation <= max_generations:
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
      fitness_history.append({"Generation": generation, "Fitness": best_fit})

      # Update progress bar
      progress_val = min(generation / max_generations, 1.0)
      progress_bar.progress(
          progress_val,
          text=f"Generation {generation} | Best String: '{best_str}' | Fitness: {best_fit}",
      )

      if best_fit == 0:
        status_text.success(
            f"🎯 Target successfully evolved at Generation {generation}!"
        )
        break
      generation += 1

    # --- METRICS DASHBOARD ---
    st.markdown("---")
