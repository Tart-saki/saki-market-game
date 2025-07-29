# ⚡ Saki Market Game — World's First PoCC Blockchain for Democratic Decentralized Fair Market (DDFM) for EV Charging Stations

**Welcome to the future of electricity trading!**  
The **Saki Market Game** is the world's first market simulator built on **Proof of Competitive Contribution (PoCC)** — a novel consensus mechanism designed to bring **fairness, competition, and AI-powered equilibrium** to decentralized energy systems.

> 🎯 **Mission:** Democratize clean energy trading by letting AI agents (sellers and buyers) compete in a transparent blockchain-backed ecosystem that rewards efficiency, quality, and contribution — not manipulation.

---

## 🚀 What Makes Saki Market Game Unique?

- ✅ **🧠 AI-Driven Market Simulation**  
  Simulates Nash-equilibrium-based pricing where sellers learn and adapt using gradient descent + Adam optimizer.

- ✅ **🧮 Adaptive Pricing Strategy**  
  Dynamic learning rates + volatility-aware price adjustments for each seller.

- ✅ **🕵️ Collusion Detection + Market Restart**  
  Detects price collusion, introduces a moderator, and restarts market to restore fairness.

- ✅ **🏗 Custom Blockchain Engine**  
  Integrated Merkle Tree-based blockchain with light sync, reward persistence, and transaction history.

- ✅ **🏆 PoCC Consensus Mechanism**  
  Rewards sellers not just for selling, but based on:
  - Utility
  - Quality of service
  - Competitive behavior

- ✅ **🔐 Tart License System**  
  Unique **audio-based license activation** using hidden hash code validation for secure software usage.

- ✅ **📊 Visual Analytics**  
  Auto-generates charts of price evolution and market share for each simulation block.

---

## 🧱 Project Structure

```
Saki_Market_Game/
├── saki_market_game/            # Package folder
│   ├── __init__.py
│   ├── main.py                  # Main entry point
│   ├── blockchain_engine.py     # Blockchain engine
│   ├── saki_core.py             # AI optimization and market logic
│   ├── input_handler.py         # User input validation
├── LICENSE.txt                  # License information
├── serial.txt                   # License hash for audio activation
├── stagano.py                   # Audio hash decoding utility
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
```

---

## 🛠️ Installation & First Run Instructions (For End Users)

1. **Download** the `.exe` release of **Saki Market Game** from the official release page.
2. **Run the application**:  
   - The first time you run it:
     - A **license agreement popup** will appear → click ✅ **Accept** to continue.
     - You will be prompted to **select your licensed audio file (.wav)**.
     - The software validates the hidden hash from the audio against `serial.txt`.
     - If valid → access is granted; otherwise, the program exits.
3. **Choose the storage folder** for blockchain data (Tartchain).
4. Enter market parameters and let the **AI-driven blockchain simulation** begin!
5. Generated reports (Excel and charts) are saved automatically inside your chosen folder.

---

## 🛠️ Developer Setup (Run from Source)

If you want to **develop or modify** the project:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/Saki_Market_Game.git
cd Saki_Market_Game
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate   # macOS/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application
```bash
python -m saki_market_game.main
```

---

## 📚 Example Output

- ✅ Excel reports:
  - `Saki_Market_Prices.xlsx`
  - `Saki_Market_Shares.xlsx`
- ✅ PNG charts:
  - `Price_Evolution.png`
  - `Market_Share_Evolution.png`
- ✅ Blockchain data:
  ```
  /Tartchain/Block_<index>/
  ```

---

📘 Git Ignore Documentation
📖 Learn what’s ignored in .gitignore → README_GITIGNORE.md

---
## 🧠 What Is PoCC?

> **Proof of Competitive Contribution (PoCC)** is a novel blockchain consensus where participants are rewarded not just for participation — but for contributing fairly, competitively, and efficiently to the market.

Reward = `Utility × Quality × Competitiveness`  
This creates **anti-monopoly pressure** and incentivizes **dynamic pricing**.

---

## 🤝 Contributing

We welcome researchers, energy economists, and blockchain engineers to collaborate:

- 🧪 Improve collusion detection logic
- 📉 Suggest new pricing strategies
- 💡 Extend the consensus mechanism
- 💬 Open issues or start a discussion

---

## ⚖️ License

Protected by **Tart Innovation Lab** License.  
🔑 Software activation is secured via **audio-based license validation**.  
For licensing inquiries, contact **saki.pocc@gmail.com**.

---

## 👤 Author

**Behnam Saki**  
*Founder, Tart | Creator of Saki Market Game*  
📍 TART Innovation Lab  
🔗 [LinkedIn](https://www.linkedin.com/in/technologic-art-260a4482/)
🔗[TART YouTube](https://www.youtube.com/@Tart-Saki)
---

## 🌎 Vision

> _“Let the energy of the future be traded by intelligence, governed by fairness, and verified by cryptographic trust.”_  

Join the **Saki Market Game** revolution — where energy meets AI and blockchain justice.
