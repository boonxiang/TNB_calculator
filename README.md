# ⚡ TNB Electricity Bill Calculator & Estimator

An interactive web application designed to help Malaysian consumers navigate the complexities of **TNB (Tenaga Nasional Berhad)** electricity tariffs. This tool provides both forward bill calculation and reverse usage estimation with high precision.

## 🚀 Key Features

* **Bidirectional Logic**: 
  * **Usage to Bill**: Calculate total costs including tiered rates, rebates, and taxes.
  * **Bill to Usage**: A custom iterative algorithm that estimates energy consumption (kWh) based on a target bill amount (RM).
* **Comprehensive Tariff Support**: 
  * **Domestic**: General and Time of Use (TOU) rates.
  * **Non-Domestic**: Low, Medium, and High voltage categories (General & TOU).
* **Detailed Financial Breakdown**: Includes precise logic for:
  * Tiered pricing structures (≤1500 kWh vs >1500 kWh).
  * **EEI Rebates** and **AFA** adjustments.
  * **Service Tax (8%)** and **KWTBB (1.6%)** contributions.
* **Interactive UX**: Built with a responsive Tailwind CSS interface, featuring real-time toast notifications and dynamic form handling.

## 🛠️ Tech Stack

* **Frontend**: HTML5, JavaScript (ES6+), Tailwind CSS.
* **Algorithms**: Iterative Binary Search for reverse-matching financial data.
* **Styling**: Inter Font family with custom CSS animations for result visualization.

## 🧠 Logic & Engineering

I focused on ensuring the mathematical accuracy of the billing engine:
1. **Iterative Matching**: Since the TNB billing formula is non-linear (due to taxes and tiered rebates), the "Estimate Usage" feature uses a search algorithm to find the exact kWh value that matches a user's input bill within a **RM 0.01 tolerance**.
2. **Data-Driven Architecture**: Tariff rates are stored in structured objects, allowing for seamless updates if regulatory rates change.

## 🕹️ Behavioral Features (Easter Eggs)
To add a touch of personality and mimic real-world system constraints, I scripted:
* **Random Break**: The calculator periodically "gets tired" and takes a 5-second coffee break after 20 calculations.
* **Time Bomb**: Access to calculations is restricted during specific time windows (e.g., at the 30-minute mark) to simulate "maintenance" or rest periods.


*Developed by Boon Xiang*
