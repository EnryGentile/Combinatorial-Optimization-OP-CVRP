# Combinatorial-Optimization-OP-CVRP
Heuristic algorithms (Genetic, Memetic, Clarke &amp; Wright) and exact models (Gurobi) for solving the Orienteering Problem and CVRP.

# Combinatorial Optimization: Orienteering Problem & CVRP

This repository contains the source code, instances, and results for the final project of the "Combinatorial and Network Optimization Algorithms" course at the University of Naples Federico II. 

**Authors:** Enrico Gentile, Gianni D'Avanzo 

## 📖 Project Overview
The project focuses on solving two complex NP-hard routing problems by comparing custom heuristic/metaheuristic algorithms with exact mathematical models. 

1. **Orienteering Problem (OP):** The goal is to maximize the total score collected by visiting a subset of control points within a given time/distance limit.
2. **Capacitated Vehicle Routing Problem (CVRP):** The goal is to minimize the total routing cost for a fleet of vehicles with fixed capacity, ensuring all customer demands are met without exceeding vehicle limits.

## ⚙️ Algorithms and Methodologies

### Orienteering Problem
*   **Genetic & Memetic Algorithms:** Developed a custom population-based approach using selection (Tournament), Single-Point Crossover, and mutation strategies.
*   **Local Search Optimization:** Integrated a greedy local search (Memetic approach) to improve route generation.
*   **Exact Solver:** Formulated the problem with MTZ constraints for subtour elimination and solved it using **Gurobi Optimizer**. 

### Capacitated Vehicle Routing Problem
*   **Clarke & Wright Savings Algorithm:** Implemented to cluster nodes and generate initial vehicle routes based on distance savings.
*   **Route Optimization:** Enhanced the generated clusters using **2-opt** and **Nearest Neighbor** local search strategies.
*   **Exact Solver:** Formulated and solved the CVRP using Gurobi.

## 📊 Results and Performance
The algorithms were tested on instances of increasing complexity (from 51 up to 200 nodes for OP, and various vehicle/node configurations for CVRP). 
*   The metaheuristic approaches achieved near-optimal solutions with significantly lower computational times compared to the exact Gurobi models.
*   *Please check the `results/` folder for detailed routing plots and terminal execution logs.*

## 🛠️ Technologies Used
*   **Python 3.x**
*   **Gurobi Optimizer** (Mathematical modeling and exact solving)
*   **Matplotlib** (Network and route visualization)

## 📁 Repository Structure
*   `/src`: Python source codes for OP and CVRP algorithms.
*   `/data`: Benchmark instances (coordinates, demands, scores).
*   `/results`: Execution plots and performance screenshots.
*   `/docs`: Full project report.
