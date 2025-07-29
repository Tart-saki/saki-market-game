# Function to collect user inputs
def get_user_input(num_sellers):
    """Collects and validates user inputs for seller parameters."""

    global buyer_demand, supply_coefficient, max_profit_percentage, max_change_percentage

    def get_validated_vector(prompt, num_sellers, min_value=None):
        """Helper function to get a validated list of numbers with correct length."""
        while True:
            try:
                values = input(prompt).strip().split(',')
                values = [float(v) for v in values]
                if len(values) != num_sellers:
                    print(f"⚠ Error: You must enter exactly {num_sellers} values separated by commas.")
                    continue
                if min_value is not None and any(v < min_value for v in values):
                    print(f"⚠ Error: Each value must be at least {min_value:.2f}.")
                    continue
                return values
            except ValueError:
                print("⚠ Invalid input. Please enter only numeric values separated by commas.")

    print("\n📥 Please provide the required inputs:")

    # Get buyer demand
    while True:
        try:
            buyer_demand = float(input("Enter total demand of the buyer: ").strip())
            if buyer_demand <= 0:
                print("⚠ Error: Demand must be a positive number.")
                continue
            break
        except ValueError:
            print("⚠ Invalid input. Please enter a valid numeric value.")

    # Get supply coefficient (must be between 0.2 and 1)
    while True:
        try:
            supply_coefficient = float(input("Enter supply coefficient (between 0.2 and 1): ").strip())
            if 0.2 <= supply_coefficient <= 1:
                print(f"🔎 Debug: supply_coefficient received = {supply_coefficient}")
                break
            else:
                print("⚠ Error: Supply coefficient must be between 0.2 and 1.")
        except ValueError:
            print("⚠ Invalid input. Please enter a valid numeric value.")

    # Compute minimum capacity per seller
    min_capacity = buyer_demand / (supply_coefficient * num_sellers)
    print(f"⚠ Note: Each seller must have a minimum capacity of {min_capacity:.2f}.")

    # Get seller parameters
    capacities = get_validated_vector(f"Enter capacities of {num_sellers} sellers (comma-separated): ", num_sellers, min_capacity)
    qualities = get_validated_vector(f"Enter qualities of {num_sellers} sellers (comma-separated): ", num_sellers)
    production_costs = get_validated_vector(f"Enter production costs of {num_sellers} sellers (comma-separated): ", num_sellers)

    # Get max profit percentage
    while True:
        try:
            max_profit_percentage = float(input("Enter max profit percentage (e.g., 0.7 for 70%): ").strip())
            if 0 <= max_profit_percentage <= 1:
                break
            else:
                print("⚠ Error: Profit percentage must be between 0 and 1 (0% - 100%).")
        except ValueError:
            print("⚠ Invalid input. Please enter a valid numeric value.")

    # Get min_profit per seller with constraint
    min_profits = []
    for i in range(num_sellers):
        lower_bound = 0
        upper_bound = capacities[i] * (production_costs[i] * max_profit_percentage)
        prompt = (
            f"Enter minimum required profit for seller {i + 1} "
            f"(capacity: {capacities[i]}, cost: {production_costs[i]:.2f}, "
            f"upper bound: {upper_bound:.2f}): "
        )
        while True:
            try:
                min_profit = float(input(prompt).strip())
                if lower_bound <= min_profit <= upper_bound:
                    min_profits.append(min_profit)
                    break
                else:
                    print(f"⚠ Error: Minimum profit must be between {lower_bound:.2f} and {upper_bound:.2f}.")
            except ValueError:
                print("⚠ Invalid input. Please enter a valid numeric value.")

    # Get max price change percentage
    while True:
        try:
            max_change_percentage = float(input("Enter max allowable price change percentage (e.g., 0.1 for 10%): ").strip())
            if 0 <= max_change_percentage <= 1:
                break
            else:
                print("⚠ Error: Max change percentage must be between 0 and 1.")
        except ValueError:
            print("⚠ Invalid input. Please enter a valid numeric value.")

    return capacities, qualities, production_costs, buyer_demand, max_profit_percentage, min_profits, max_change_percentage, supply_coefficient



