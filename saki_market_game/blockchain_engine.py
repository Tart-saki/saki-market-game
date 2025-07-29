import hashlib
import json
import os
import time
import numpy as np

# 🔹 Create seller node folders
def initialize_seller_nodes(num_sellers, BASE_DIR):
    for i in range(num_sellers):
        node_dir = os.path.join(BASE_DIR, f"Node_{i + 1}_ledger")
        os.makedirs(node_dir, exist_ok=True)

# 🔹 Light sync: only latest block to each node
def light_sync_for_new_nodes(energy_chain, num_sellers, BASE_DIR):
    latest_block_index = len(energy_chain.chain) - 1
    block_folder = os.path.join(BASE_DIR, f"Block_{latest_block_index}")
    block_file = os.path.join(block_folder, "block_data.json")

    if os.path.exists(block_file):
        with open(block_file, "r") as file:
            latest_block_data = json.load(file)

        for i in range(num_sellers):
            node_ledger_dir = os.path.join(BASE_DIR, f"Node_{i + 1}_ledger")
            os.makedirs(node_ledger_dir, exist_ok=True)
            node_ledger_file = os.path.join(node_ledger_dir, f"latest_block_ledger.json")

            with open(node_ledger_file, "w") as node_file:
                json.dump(latest_block_data, node_file, indent=4)

    print("✅ Light sync completed for new nodes.")

# 🔹 Distribute rewards with PoCC
def distribute_rewards_v2(prices, buyer_shares, weighted_utility, qualities, production_costs, num_sellers):
    epsilon = 1e-9
    total_payment = sum(np.array(prices) * np.array(buyer_shares))

    if total_payment == 0:
        print("⚠ Warning: No transactions occurred. No rewards distributed.")
        return np.zeros(num_sellers), 0

    profits = np.array(prices) * np.array(buyer_shares) - np.array(production_costs) * np.array(buyer_shares)
    total_profit = max(sum(profits), epsilon)
    reward_pool = 0.01 * total_payment
    total_payment_with_reward = total_payment + reward_pool

    total_utility = max(sum(weighted_utility), epsilon)
    normalized_utility = weighted_utility / total_utility
    total_supply = max(sum(buyer_shares), epsilon)
    normalized_supply = buyer_shares / total_supply
    normalized_profits = profits / total_profit
    total_quality = max(sum(qualities), epsilon)
    normalized_qualities = np.array(qualities) / total_quality

    base_rewards = reward_pool * 0.80 * (normalized_utility * normalized_supply)
    efficiency_rewards = reward_pool * 0.15 * normalized_profits
    fairness_rewards = reward_pool * 0.05 * normalized_qualities

    total_rewards = base_rewards + efficiency_rewards + fairness_rewards

    print("\n🏆 Final Reward Distribution Results:")
    print(f"🔹 Total Transaction Amount (with 1% Reward Fee): {total_payment_with_reward:.2f}")
    print(f"🔹 Total Rewards Distributed: {reward_pool:.2f}")
    print("\n🎖 Sellers & Their Rewards:")
    for i in range(num_sellers):
        print(f"🔹 Seller {i+1}: Final Reward = {total_rewards[i]:.4f}")

    return total_rewards, total_payment_with_reward

# 🔹 Merkle Tree
class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        self.merkle_root = self.build_merkle_tree(transactions)

    def build_merkle_tree(self, transactions):
        if not transactions:
            return None
        if len(transactions) == 1:
            return transactions[0]
        new_level = []
        for i in range(0, len(transactions), 2):
            left = transactions[i]
            right = transactions[i + 1] if i + 1 < len(transactions) else left
            combined = hashlib.sha256((left + right).encode()).hexdigest()
            new_level.append(combined)
        return self.build_merkle_tree(new_level) if len(new_level) > 1 else new_level[0]

    def get_merkle_root(self):
        return self.merkle_root

# 🔹 Block structure
class EnergyBlock:
    def __init__(self, index, timestamp, transactions, previous_hash, BASE_DIR):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.BASE_DIR = BASE_DIR

        if isinstance(transactions, dict) and "final_prices" in transactions:
            tx_hashes = [hashlib.sha256(json.dumps(tx).encode()).hexdigest() for tx in transactions["final_prices"]]
            self.merkle_tree = MerkleTree(tx_hashes)
            self.merkle_root = self.merkle_tree.get_merkle_root()
        else:
            self.merkle_root = None

        self.block_hash = self.calculate_hash()
        self.save_block()

    def calculate_hash(self):
        block_content = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_content.encode()).hexdigest()

    def save_block(self):
        block_dir = os.path.join(self.BASE_DIR, f"Block_{self.index}")
        os.makedirs(block_dir, exist_ok=True)
        block_file = os.path.join(block_dir, "block_data.json")

        with open(block_file, "w") as file:
            json.dump({
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
                "block_hash": self.block_hash
            }, file, indent=4)

        if isinstance(self.transactions, dict) and "final_prices" in self.transactions:
            for i in range(len(self.transactions["final_prices"])):
                node_ledger_dir = os.path.join(self.BASE_DIR, f"Node_{i + 1}_ledger")
                os.makedirs(node_ledger_dir, exist_ok=True)
                node_ledger_file = os.path.join(node_ledger_dir, f"block_{self.index}_ledger.json")

                with open(node_ledger_file, "w") as node_file:
                    json.dump({
                        "index": self.index,
                        "transactions": self.transactions,
                        "block_hash": self.block_hash
                    }, node_file, indent=4)

        print(f"✅ Block {self.index} saved successfully!")

# 🔹 Blockchain class
class EnergyBlockchain:
    def __init__(self, BASE_DIR):
        self.chain = []
        self.BASE_DIR = BASE_DIR
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = EnergyBlock(0, time.time(), {"message": "Genesis Block"}, "0", self.BASE_DIR)
        self.chain.append(genesis_block)

    def add_block(self, transactions):
        previous_block = self.chain[-1]
        new_block = EnergyBlock(len(self.chain), time.time(), transactions, previous_block.block_hash, self.BASE_DIR)
        self.chain.append(new_block)

        if len(self.chain) > 1000:
            self.chain = self.chain[-1000:]
            print("🔄 Blockchain trimmed to last 1000 blocks.")

# 🔹 Save blockchain
def save_blockchain(energy_chain, BASE_DIR):
    blockchain_data = []
    for block in energy_chain.chain:
        blockchain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "previous_hash": block.previous_hash,
            "block_hash": block.block_hash
        })

    blockchain_file = os.path.join(BASE_DIR, "blockchain.json")
    with open(blockchain_file, "w", encoding="utf-8") as file:
        json.dump(blockchain_data, file, indent=4)
    print("✅ Blockchain saved successfully at:", blockchain_file)

# 🔹 Load blockchain
def load_blockchain(BASE_DIR):
    blockchain_file = os.path.join(BASE_DIR, "blockchain.json")

    if os.path.exists(blockchain_file):
        if os.path.getsize(blockchain_file) == 0:
            print("⚠ Blockchain file is empty. Creating new blockchain...")
            return EnergyBlockchain(BASE_DIR)

        try:
            with open(blockchain_file, "r", encoding="utf-8") as file:
                blockchain_data = json.load(file)
        except json.JSONDecodeError:
            print("⚠ Blockchain file corrupted. Creating new blockchain...")
            return EnergyBlockchain(BASE_DIR)

        energy_chain = EnergyBlockchain(BASE_DIR)
        energy_chain.chain = []
        for block in blockchain_data:
            restored_block = EnergyBlock(
                block["index"],
                block["timestamp"],
                block["transactions"],
                block["previous_hash"],
                BASE_DIR
            )
            restored_block.block_hash = block["block_hash"]
            energy_chain.chain.append(restored_block)

        print("🔄 Blockchain loaded successfully!")
        return energy_chain
    else:
        print("⚠ No previous blockchain found. Creating a new one...")
        return EnergyBlockchain(BASE_DIR)
