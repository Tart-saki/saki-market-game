import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tkinter import Tk, Toplevel, messagebox, Button, Frame, WORD, filedialog
from tkinter.scrolledtext import ScrolledText

# Import stagano function
from stagano import extract_hidden_hash

from saki_market_game.blockchain_engine import (
    load_blockchain, save_blockchain, initialize_seller_nodes,
    light_sync_for_new_nodes, distribute_rewards_v2
)
from saki_market_game.saki_core import saki, initialize_prices
from saki_market_game.input_handler import get_user_input

# --------------------First-run configuration------------------
CONFIG_FIRST_RUN = "first_run.json"

def is_first_run():
    """Check if program is running for the first time."""
    return not os.path.exists(CONFIG_FIRST_RUN)

def set_first_run_complete():
    """Mark that first run has been completed."""
    with open(CONFIG_FIRST_RUN, "w") as f:
        json.dump({"first_run_completed": True}, f)

# ------------------------- Utilities -------------------------
def resource_path(relative_path):
    """Get absolute path to resource (compatible with PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)

# ------------------------- License Popup -------------------------
def show_license_popup():
    """Displays LICENSE.txt in a popup and asks user to accept."""
    root = Tk()
    root.withdraw()  # Hide the root window

    license_window = Toplevel()
    license_window.title("📜 License Agreement")
    license_window.geometry("700x500")
    license_window.resizable(False, False)

    try:
        license_path = resource_path("LICENSE.txt")
        with open(license_path, "r", encoding="utf-8") as f:
            license_text = f.read()
    except FileNotFoundError:
        messagebox.showerror("Error", "LICENSE.txt not found.")
        license_window.destroy()
        return False

    text_area = ScrolledText(license_window, wrap=WORD, font=("Arial", 10))
    text_area.pack(expand=True, fill="both", padx=10, pady=10)
    text_area.insert("end", license_text)
    text_area.config(state="disabled")

    def accept():
        license_window.destroy()
        root.destroy()

    def decline():
        messagebox.showinfo("Exit", "You must accept the license to use this application.")
        license_window.destroy()
        root.destroy()
        sys.exit()

    btn_frame = Frame(license_window)
    btn_frame.pack(pady=10)

    Button(btn_frame, text="✅ Accept", command=accept, bg="green", fg="white", width=15).pack(side="left", padx=20)
    Button(btn_frame, text="❌ Decline", command=decline, bg="red", fg="white", width=15).pack(side="right", padx=20)

    license_window.grab_set()
    license_window.wait_window()
    return True


# ------------------------- Collusion Detection -------------------------
def detect_collusion(num_sellers, final_prices, buyer_shares, price_history, iterations, price_stability_threshold=0.01, min_iterations=10):
    """Detects potential collusion among sellers."""
    early_stop_flag = iterations < min_iterations
    if early_stop_flag:
        print(f"\n⚠ Warning: Market stabilized in only {iterations} iterations. Possible collusion detected!")

    if len(price_history) < 2:
        print("\n⚠ Not enough price history for collusion detection.")
        return early_stop_flag

    price_history = np.array(price_history)
    avg_price_change = np.mean(np.abs(price_history[1:] - price_history[:-1]), axis=0)
    price_stability_flag = np.all(avg_price_change < price_stability_threshold)

    if price_stability_flag:
        print("\n⚠ Warning: Prices remained almost unchanged during the game. Possible collusion detected!")

    market_share_variance = np.std(buyer_shares)
    equal_share_flag = market_share_variance < 0.05

    if equal_share_flag:
        print("\n⚠ Warning: Market shares among sellers are nearly identical. Possible collusion detected!")

    collusion_detected = sum([early_stop_flag, price_stability_flag, equal_share_flag]) >= 2

    if collusion_detected:
        print("\n🚨 Collusion Confirmed! Market will be restarted with a new moderator seller.")

    return collusion_detected


# ------------------------- Main Execution -------------------------
def main():
    if is_first_run():
        # 1️⃣ Show License Popup
        if not show_license_popup():
            return

        # 2️⃣ Validate Serial from audio
        serial_path = resource_path("serial.txt")
        try:
            with open(serial_path, "r", encoding="utf-8") as f:
                stored_hash = f.read().strip()
        except FileNotFoundError:
            print("❌ serial.txt not found. Exiting...")
            sys.exit()

        # Ask user for audio license file
        root = Tk()
        root.withdraw()
        audio_file = filedialog.askopenfilename(
            title="Select your licensed audio file",
            filetypes=[("WAV audio files", "*.wav")]
        )
        root.destroy()

        if not audio_file:
            print("❌ No audio file selected. Exiting...")
            sys.exit()

        short_hash, full_hash = extract_hidden_hash(audio_file)

        if full_hash != stored_hash:
            print("🚫 Invalid license detected. Exiting program...")
            sys.exit()

        print("✅ License validated successfully. Proceeding...\n")

        # ✅ Mark first run as complete
        set_first_run_complete()
    else:
        print("🔑 License already validated. Skipping license and serial check.")
    print("🧠 Welcome to the ⚡ Saki Market Blockchain ⚡")

    # 5️⃣ Load or create config for Tartchain folder
    CONFIG_FILE = "saki_config.json"

    def ask_user_for_directory():
        root = Tk()
        root.withdraw()
        path = filedialog.askdirectory(title="Please choose where to save Tartchain data")
        root.destroy()
        return path

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        BASE_DIR = config.get("base_dir", "")
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR, exist_ok=True)
    else:
        BASE_DIR = ask_user_for_directory()
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump({"base_dir": BASE_DIR}, f)

    print(f"📂 Tartchain folder set to: {BASE_DIR}")

    # 6️⃣ Blockchain logic
    energy_chain = load_blockchain(BASE_DIR)

    while True:
        try:
            num_sellers = int(input("Enter number of sellers (or 0 to exit): ").strip())
            if num_sellers == 0:
                print("🚪 Exiting blockchain...")
                save_blockchain(energy_chain, BASE_DIR)
                exit()
            if num_sellers > 0:
                break
            else:
                print("⚠ Error: Number of sellers must be positive.")
        except ValueError:
            print("⚠ Invalid input. Please enter a valid integer.")

    initialize_seller_nodes(num_sellers, BASE_DIR)
    light_sync_for_new_nodes(energy_chain, num_sellers, BASE_DIR)

    capacities, qualities, production_costs, buyer_demand, max_profit_percentage, min_profits, max_change_percentage, supply_coefficient = get_user_input(num_sellers)
    initial_prices = initialize_prices(num_sellers, production_costs, max_profit_percentage)

    final_prices, buyer_shares, price_history, share_history, iterations = saki(
        num_sellers, capacities, qualities, production_costs, buyer_demand, max_profit_percentage,
        min_profits, max_change_percentage, initial_prices=initial_prices
    )

    collusion_detected = detect_collusion(num_sellers, final_prices, buyer_shares, price_history, iterations)

    if collusion_detected:
        print("\n⚠ Collusion detected! Adding moderator and rerunning.")
        moderator_capacity = max(capacities)
        moderator_quality = min(0.99, max(qualities))
        moderator_cost = min(production_costs)
        moderator_price = min(min(final_prices) * 0.70, moderator_cost * 1.05)
        moderator_min_profit = 0

        num_sellers += 1
        capacities.append(moderator_capacity)
        qualities.append(moderator_quality)
        production_costs.append(moderator_cost)
        min_profits.append(moderator_min_profit)
        final_prices.append(moderator_price)

        final_prices, buyer_shares, price_history, share_history, iterations = saki(
            num_sellers, capacities, qualities, production_costs, buyer_demand, max_profit_percentage,
            min_profits, max_change_percentage, initial_prices=final_prices,
            use_moderator=True, moderator_price=moderator_price
        )

    weighted_utility = np.zeros(num_sellers)
    valid_indices = np.array(final_prices) > 0
    if np.any(valid_indices):
        weighted_utility[valid_indices] = (np.array(qualities)[valid_indices] / np.array(final_prices)[valid_indices]) * np.array(buyer_shares)[valid_indices]
        weighted_utility = weighted_utility / np.sum(weighted_utility) if np.sum(weighted_utility) > 0 else np.full(num_sellers, 1 / num_sellers)
    else:
        weighted_utility = np.full(num_sellers, 1 / num_sellers)

    rewards, total_payment_with_reward = distribute_rewards_v2(
        final_prices, buyer_shares, weighted_utility, qualities, production_costs, num_sellers
    )

    transactions = {
        "final_prices": final_prices.tolist() if isinstance(final_prices, np.ndarray) else final_prices,
        "buyer_shares": buyer_shares.tolist() if isinstance(buyer_shares, np.ndarray) else buyer_shares,
        "iterations": iterations,
        "rewards": rewards.tolist() if isinstance(rewards, np.ndarray) else rewards,
        "total_payment_with_reward": total_payment_with_reward
    }

    energy_chain.add_block(transactions)
    print("\n✅ Block added successfully!")

    save_blockchain(energy_chain, BASE_DIR)
    print("✅ Blockchain saved successfully!")

    print("\n📊 Final Market Results:")
    print(f"🔹 Final Prices: {[round(p, 2) for p in final_prices]}")
    print(f"🔹 Buyer Shares: {[round(s, 2) for s in buyer_shares]}")
    print(f"🔹 Number of Iterations: {iterations}")

    block_index = len(energy_chain.chain) - 1
    block_folder = os.path.join(BASE_DIR, f"Block_{block_index}")
    os.makedirs(block_folder, exist_ok=True)

    df_prices = pd.DataFrame(price_history, columns=[f"Seller {i + 1}" for i in range(num_sellers)])
    df_shares = pd.DataFrame(share_history, columns=[f"Seller {i + 1}" for i in range(num_sellers)])
    df_prices.to_excel(os.path.join(block_folder, "Saki_Market_Prices.xlsx"), index=True)
    df_shares.to_excel(os.path.join(block_folder, "Saki_Market_Shares.xlsx"), index=True)

    plt.figure(figsize=(10, 5))
    for i in range(num_sellers):
        plt.plot(range(len(price_history)), [p[i] for p in price_history], marker='o', label=f"Seller {i + 1}")
    plt.xlabel("Iteration")
    plt.ylabel("Price")
    plt.title("Price Evolution Over Iterations")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(block_folder, "Price_Evolution.png"))
    plt.close()

    plt.figure(figsize=(10, 5))
    for i in range(num_sellers):
        plt.plot(range(len(share_history)), [s[i] for s in share_history], marker='o', label=f"Seller {i + 1}")
    plt.xlabel("Iteration")
    plt.ylabel("Market Share")
    plt.title("Market Share Evolution Over Iterations")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(block_folder, "Market_Share_Evolution.png"))
    plt.close()

    print(f"\n📊 All plots saved in {block_folder}")
    input("\n🔚 Press Enter to exit the program...")


if __name__ == "__main__":
    main()
