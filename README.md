# 🛡️ Buyer Protection - AI E-Commerce Claim Reviewer

Decentralized buyer protection for e-commerce, powered by **GenLayer Intelligent Contracts**.

Instead of a human CS deciding refunds manually, an on-chain AI Judge reviews every claim, checks the evidence, and decides: `APPROVED`, `REJECTED`, or `NEED_MORE_EVIDENCE`.

Built for **GenLayer**.

## 🔗 Links

- **GitHub:** https://github.com/isnoop4/buyer-protection
- **Contract Address (Testnet):** `0x2Bc36a337DF07155C2A33Ca337d0594964984465`
- **Explorer:** https://explorer-studio.genlayer.com/address/0x2Bc36a337DF07155C2A33Ca337d0594964984465

## ❓ Problem

In e-commerce, buyer claims are slow and unfair:
- Buyer says "item not received / wrong item"
- Seller says "already shipped"
- Platform CS decides manually, takes days, often biased

## 💡 Solution

Smart contract + AI Judge on GenLayer:

1. Buyer creates an order
2. Buyer files a claim with description + `evidence_url` (photo)
3. `ai_review_claim` calls LLM with `prompt_comparative`
4. AI returns structured verdict:
```json
{
  "verdict": "APPROVED",
  "refund_percentage": 100,
  "confidence_score": 94,
  "is_fraud_suspected": false,
  "reason": "..."
}
