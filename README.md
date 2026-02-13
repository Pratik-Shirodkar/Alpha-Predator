# Zero-Knowledge Alpha Predator 🦁🔒

**Autonomous DeFi Agent • x402 Payments • Encrypted Execution on SKALE**

> 🏆 **Submitted for SF Agentic Commerce x402 Hackathon**

## 🎯 Track Alignment & Eligibility

### 1. 🥇 Encrypted Agents (SKALE)
**Requirement**: "Uses BITE v2 in a way that materially changes the workflow... Demonstrates a conditional trigger... Shows encrypted → condition check → decrypt/execute"

**Our Implementation**:
- **Material Change**: We use **Threshold Encryption** to hide trade intents in the mempool, preventing front-running (sandwich attacks). This is a "why private" workflow that standard public execution cannot solve.
- **Conditional Trigger**: We set conditions (e.g., `CONFIDENCE > 0.8`) that must be met before decryption.
- **On-Chain Execution**: We sign and broadcast **real transactions** to the **SKALE BITE V2 Sandbox 2** (Chain ID: `103698795`).
- **Evidence**: 
  - Real BITE SDK (`@skalenetwork/bite`) integration.
  - Live **Blockscout Explorer Links** for every encrypted intent.
  - UI Visualization of the full `Intent → Encrypt → Condition → Decrypt` lifecycle.

### 2. 🤖 Agentic Tool Usage on x402 (CDP)
**Requirement**: "Uses CDP Wallets... Uses x402 in a real flow: HTTP 402 → pay → retry... Demonstrates tool chaining"

**Our Implementation**:
- **Real Workflow**: Discover (Alpha Scan) → Decide (Consensus) → Pay (x402) → Outcome (Encrypted Trade).
- **Tool Chaining**: The agent chains 3 distinct tools (Technical Analysis, Sentiment Analysis, On-Chain Metrics), each requiring individual payments.
- **x402 Flow**: The agent hits a 402 endpoint, pays using its wallet, and retries the request with the payment proof.
- **Cost Reasoning**: `BudgetManager` enforces a strict $10.00 cap, demonstrating "budget awareness".

### 3. 🛡️ Overall Track: Best Agentic App
**Requirement**: "Real utility... Reliability... Trust + safety... Receipts/logs"

**Our Implementation**:
- **Real Utility**: Solves the real problem of paying for premium data without human intervention.
- **Trust & Safety**: 
  - **Risk Controls**: Slippage protection, max spend caps, and confidence thresholds.
  - **Audit Trail**: Every micro-transaction is logged in the "Audit Trail" panel with timestamps and amounts.
- **Reliability**: Deterministic state machine handles the full lifecycle from scan to execution.

---

## 🏗️ Architecture

### 1. Agentic Workflow (Backend)
- **Framework**: Python (FastAPI) + LangChain
- **Payment Layer**: **x402** (HTTP 402 Payment Required) middleware.
- **Consensus Engine**: Aggregates insights from 3 distinct analyst agents.

### 2. Encrypted Execution (SKALE Layer)
- **Integration**: Real **@skalenetwork/bite** SDK (TypeScript) via Next.js Bridge.
- **Chain**: **BITE V2 Sandbox 2** (Chain ID: `103698795`)
- **Flow**:
  1. Agent decides to trade.
  2. Backend sends intent to `/api/bite/encrypt`.
  3. API uses `ethers.Wallet` (private key) + `bite.encryptTransaction()`.
  4. **Submits ON-CHAIN** to the BITE Contract (`0xc4083...`).
  5. Returns real Transaction Hash (viewable on Blockscout).

---

## 🛠️ Quickstart

### Prerequisites
- Node.js 18+
- Python 3.10+
- SKALE sFUEL (for BITE Sandbox 2 gas) in your wallet.

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/zk-alpha-predator.git
cd zk-alpha-predator
```

### 2. Configure Credentials
Create `frontend/.env.local`:
```env
# Private key with sFUEL on SKALE BITE V2 Sandbox 2
BITE_PRIVATE_KEY=0x...
```

Create `backend/.env` (Required for Real CDP Wallet):
```env
# Coinbase Developer Platform Credentials
CDP_API_KEY_NAME=organizations/...
CDP_API_KEY_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----...
```

### 3. Start Backend (Agent Brain)
```bash
# In /rootDir
python -m backend.main
# Server starts at http://localhost:8000
```

### 4. Start Frontend (Dashboard)
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:3000
```

---

## 🧩 Tech Stack
- **Frontend**: Next.js 15, React 19, Glassmorphism UI (Custom CSS)
- **Backend**: Python, FastAPI, WebSockets
- **Blockchain**: SKALE (BITE v2 Sandbox), Coinbase (CDP Wallets)
- **AI**: OpenAI GPT-4o (simulated logic for demo stability)

## 📄 License
MIT
