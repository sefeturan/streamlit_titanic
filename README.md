# 🚢 Titanic Passenger Insights

An interactive data exploration and preprocessing dashboard built with **Python**, **Pandas**, **Plotly**, and **Streamlit** to examine passenger survival patterns in the Titanic dataset.

## 📋 Project Overview

This web application allows users to filter passenger subgroups dynamically and inspect how raw data is cleaned and transformed step by step before analysis[cite: 1, 2, 3].

### Key Features
* **Interactive Sidebar Filters:** Filter all metrics, charts, and tables by **Passenger Class (`pclass`)**, **Sex (`sex`)**, and **Age Group (`age_group`)**[cite: 1, 2].
* **Overview Tab:** Displays four KPI cards (**Passengers in Selection**, **Survivors**, **Survival Rate**, **Average Fare**) alongside survival count and passenger class survival rate bar charts[cite: 2].
* **Explore Tab:** Compares survival rates by passenger class and sex, visualizes age distributions by survival status, and examines ticket fare distributions across classes[cite: 2].
* **Preprocessing Tab:** Demonstrates the complete data preparation pipeline with before-and-after previews[cite: 3, 4]:
  1. **Initial Dataset Inspection:** Shape (`891 rows × 15 columns`), column names, data types, missing counts, and `.loc` sample preview[cite: 1, 3].
  2. **Missing Value Imputation:** Fills missing `age` values with the median and missing `embarked` values with the mode (`deck` excluded due to high missingness)[cite: 1, 3].
  3. **Min-Max Normalization:** Rescales `age` and `fare` to `[0, 1]` (`age_norm`, `fare_norm`) while preserving original columns[cite: 1, 3].
  4. **Age Discretization:** Groups `age` into `Child (0–12)`, `Teen (13–18)`, `Young Adult (19–35)`, `Adult (36–60)`, and `Older Adult (61+)`[cite: 1, 3].
  5. **Categorical Coding:** Encodes `sex` and `embarked` into numeric columns without altering `survived` or normalizing encoded features[cite: 1, 3].
* **Data Explorer Tab:** Lets users switch between **Raw**, **Cleaned**, and **Transformed** dataset views and customize visible columns[cite: 3].

## 🛠️ Tech Stack
* **Python 3**
* **Streamlit** (Web application framework)[cite: 1, 4]
* **Pandas** (Data manipulation & preprocessing)[cite: 1]
* **Plotly Express** (Interactive visualizations)

## 🚀 Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)sefeturan/streamlit_titanic.git
   cd streamlit_titanic
