import hashlib
import json
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Function to initialize prices within the valid range
def initialize_prices(num_sellers, production_costs, max_profit_percentage):
    """Initializes seller prices within the valid range."""
    prices = []
    for i in range(num_sellers):
        valid_range_low = production_costs[i]
        valid_range_high = production_costs[i] * (1 + max_profit_percentage)
        while True:
            try:
                price = float(input(
                    f"Enter initial price for seller {i + 1} (valid range: {valid_range_low:.2f} - {valid_range_high:.2f}): "))
                if valid_range_low <= price <= valid_range_high:
                    prices.append(price)
                    break
                else:
                    print("⚠ Invalid price. Please enter a value within the valid range.")
            except ValueError:
                print("⚠ Invalid input. Please enter a numeric value.")
    return prices

# Adam Optimizer for adaptive learning rate adjustment
class AdamOptimizer:
    def __init__(self, lr=0.01, beta1=0.9, beta2=0.999, epsilon=1e-8):
        """Initializes Adam optimizer parameters."""
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = 0
        self.v = 0
        self.t = 0

    def update(self, gradient):
        """Updates learning rate using Adam optimization."""
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradient
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradient ** 2)
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        return self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
# Function to dynamically adjust learning rate based on price volatility
def adaptive_learning_rate(iteration, prev_prices, current_prices, min_lr=0.005, base_max_lr=0.05):
    """Dynamically adjusts the learning rate based on price volatility using mean change and standard deviation."""
    price_changes = np.array(current_prices) - np.array(prev_prices)
    price_change_mean = float(np.abs(np.mean(price_changes)))  # Convert to standard float
    price_std = float(np.std(price_changes))  # Convert to standard float

    # Dynamically adjust max_lr based on volatility
    dynamic_max_lr = float(base_max_lr + min(0.05, price_std))  # Ensure standard float type

    # Determine learning rate based on volatility
    if price_change_mean > 0.1 or price_std > 0.1:
        lr = dynamic_max_lr  # Keep learning rate high when volatility is significant
    else:
        lr = max(float(min_lr), min(dynamic_max_lr, float(1 / (iteration ** 0.5))))  # Ensure standard float

    # Print learning rate details for debugging and analysis
    print(f"Iteration {iteration}: Learning Rate = {lr:.4f}, Mean Change = {price_change_mean:.4f}, Std Dev = {price_std:.4f}")

    return lr

# Function to simulate the market using Nash equilibrium and Adam optimizer
def saki(num_sellers, capacities, qualities, production_costs, buyer_demand, max_profit_percentage, min_profits,
         max_change_percentage, tolerance=0.01, max_iterations=1000, initial_prices=None,
         use_moderator=False, moderator_price=None):
    """
    Simulates a competitive electricity market using Nash equilibrium and Adam optimizer.

    Parameters:
    - num_sellers (int): Number of electricity sellers.
    - capacities (list): Available supply capacities of each seller.
    - qualities (list): Quality scores of electricity provided by each seller.
    - production_costs (list): Production costs of electricity for each seller.
    - buyer_demand (float): Total electricity demand from the buyer.
    - max_profit_percentage (float): Maximum allowed profit percentage for sellers.
    - min_profits (list): Minimum acceptable profits for each seller.
    - max_change_percentage (float): Maximum allowable price change per iteration.
    - tolerance (float): Convergence threshold for price changes.
    - max_iterations (int): Maximum number of iterations allowed.
    - initial_prices (list, optional): Initial prices of sellers (if provided).
    - use_moderator (bool, optional): Whether a moderator seller is included.
    - moderator_price (float, optional): Predefined price for the moderator.

    Returns:
    - final_prices (list): Final equilibrium prices of sellers.
    - buyer_shares (list): Allocated electricity shares for each seller.
    - price_history (list): Evolution of prices over iterations.
    - share_history (list): Evolution of market shares over iterations.
    - iterations (int): Number of iterations taken for convergence.
    """

    global weighted_utility  # Store weighted utility scores for reward distribution

    # 🟢 Step 1: Initialize seller prices
    if initial_prices is not None:
        prices = initial_prices.copy()  # Use predefined prices
    else:
        prices = initialize_prices(num_sellers, production_costs, max_profit_percentage)  # Get user input prices

    # ✅ If a moderator exists, set its price to the predefined value
    if use_moderator and moderator_price is not None:
        prices[-1] = max(production_costs[-1], min(moderator_price, production_costs[-1] * (1 + max_profit_percentage)))

    buyer_shares = np.zeros(num_sellers)  # Initialize buyer's allocated shares
    price_history = []  # Store price evolution for later analysis
    share_history = []  # Store market share evolution for later analysis

    # 🟢 Step 2: Initialize Adam optimizer for dynamic price adjustments
    adam_optimizers = [AdamOptimizer(lr=0.05) for _ in range(num_sellers)]

    iteration = 0  # Track the number of iterations
    reset_threshold = max(10, max_iterations // 20)  # Threshold for market stagnation detection
    no_significant_change_count = 0  # Count consecutive iterations with negligible price changes

    price_history.append(prices.copy())  # Store initial prices
    share_history.append(buyer_shares.copy())  # Store initial shares

    # 🟢 Step 3: Iterative market price adjustment
    while iteration < max_iterations:
        iteration += 1
        prev_prices = prices.copy()  # Store previous prices before update

        # ✅ Compute utility scores based on price-to-quality ratio and capacity
        utility_scores = (np.array(qualities) / np.array(prices)) * np.array(capacities)

        # 🚀 Prevent zero division: If all sellers have zero utility, assign equal shares
        if np.sum(utility_scores) == 0:
            utility_scores = np.ones(num_sellers) / num_sellers  # Assign equal scores

        weighted_utility = utility_scores / np.sum(utility_scores)  # Normalize utility scores
        buyer_shares = weighted_utility * buyer_demand  # Compute buyer allocation
        buyer_shares = np.minimum(buyer_shares, capacities)  # Ensure shares don't exceed capacities

        # 🟢 Step 4: Update seller prices using gradient descent
        for i in range(num_sellers):
            if buyer_shares[i] > 0:  # Only adjust prices for active sellers
                # ✅ Compute profit gradient (difference between allocation and cost-adjusted price)
                profit_gradient = buyer_shares[i] - (prices[i] - production_costs[i])

                # ✅ Adjust learning rate dynamically
                if iteration <= 10:
                    learning_rate = adam_optimizers[i].update(profit_gradient)
                else:
                    learning_rate = adaptive_learning_rate(iteration, prev_prices, prices)

                # ✅ Compute new price using gradient descent
                new_price = prices[i] + learning_rate * profit_gradient

                # ✅ Apply max price change restriction to prevent abrupt fluctuations
                max_change = prices[i] * max_change_percentage
                new_price = max(min(new_price, prices[i] + max_change), prices[i] - max_change)

                # ✅ Ensure price remains within valid profit range
                new_price = min(max(new_price, production_costs[i]), production_costs[i] * (1 + max_profit_percentage))

                # ✅ Ensure minimum profit constraint is met
                profit = (new_price - production_costs[i]) * buyer_shares[i]
                if profit < min_profits[i]:
                    step = 0.5
                    while profit < min_profits[i]:
                        new_price += step
                        if new_price > production_costs[i] * (1 + max_profit_percentage):
                            break
                        profit = (new_price - production_costs[i]) * buyer_shares[i]
                    prices[i] = min(new_price, production_costs[i] * (1 + max_profit_percentage))
                else:
                    prices[i] = new_price

        # ✅ Store price and market share history
        price_history.append(prices.copy())
        share_history.append(buyer_shares.copy())

        # ✅ Step 5: Check for market convergence
        price_difference = np.abs(np.array(prices) - np.array(prev_prices))
        if np.all(price_difference < tolerance):
            no_significant_change_count += 1  # Increase counter if price change is minimal
        else:
            no_significant_change_count = 0  # Reset counter if significant price change occurs

        # 🚨 Detect market stagnation and reset learning rates
        if no_significant_change_count >= reset_threshold:
            print("\n⚠ Market seems stagnant! Resetting learning rates for better convergence.")
            adam_optimizers = [AdamOptimizer(lr=0.05) for _ in range(num_sellers)]  # Reset optimizers
            no_significant_change_count = 0  # Reset stagnation counter

        # ✅ If all prices remain stable, stop iterations
        if np.allclose(prev_prices, prices, atol=tolerance):
            break

    # 🏆 Step 6: Display final weighted utility scores
    print("\n📊 Weighted Utility Scores of Sellers:")
    for i in range(num_sellers):
        print(f"Seller {i + 1}: {weighted_utility[i]:.7f}")

    return prices, buyer_shares, price_history, share_history, iteration