# 🧠 Direct Mapped Cache Simulator

This Python project simulates a **Direct Mapped Cache** system to help understand how memory addresses are mapped into cache lines. It is useful for students and developers learning computer architecture fundamentals.

## 🚀 Features

- Direct-mapped cache simulation
- Calculates and displays hit/miss statistics
- Reads memory addresses from input file
- Outputs detailed log to a result file
- Simple and modular Python code

## 📁 Project Structure

DirectMapped_Cache/
├── cache_simulator.py # Main Python script
├── input.txt # Memory access input (hex addresses)
├── output.txt # Simulation result (large output file)
├── README.md # Project documentation
└── .gitignore # Files to exclude from version control

## 📌 How to Run

### Step 1: Prepare Input

Create an `input.txt` file with one memory address per line (in hexadecimal):

### Step 2: Run the Script

Execute the simulator using Python:

```bash
python3 cache_simulator.py input.txt

