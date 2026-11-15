# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

class BuyerProtection(gl.Contract):
    """
    AI Buyer Protection - E-Commerce Claim Reviewer
    Strict access control + Photo Evidence + AI Judge
    """

    orders: TreeMap[str, str]
    claims: TreeMap[str, str]

    def __init__(self):
        pass

    # ---------- WRITE ----------

    @gl.public.write
    def create_order(self, order_id: str, item_name: str, price: str, buyer: str) -> None:
        if order_id.strip() == "" or item_name.strip() == "":
            raise Exception("Order ID and item name are required")
        if self.orders.get(order_id) is not None:
            raise Exception("Order already exists")
        seller = str(gl.message.sender_address)
        if seller.lower() == buyer.lower():
            raise Exception("Seller cannot be buyer")
        data = {
            "order_id": order_id,
            "item_name": item_name,
            "price": price,
            "buyer": buyer,
            "seller": seller,
            "status": "DELIVERED",
        }
        self.orders[order_id] = json.dumps(data)
        claim = {
            "status": "NO_CLAIM",
            "claim_type": "",
            "description": "",
            "evidence_url": "",
            "verdict": "",
            "refund_percentage": 0,
            "confidence_score": 0,
            "reason": "",
            "is_fraud_suspected": False,
        }
        self.claims[order_id] = json.dumps(claim)

    @gl.public.write
    def file_claim(self, order_id: str, claim_type: str, description: str, evidence_url: str) -> None:
        order_raw = self.orders.get(order_id)
        if order_raw is None:
            raise Exception("Order not found")
        if description.strip() == "":
            raise Exception("Claim description is required")
        order = json.loads(order_raw)
        claim = json.loads(self.claims.get(order_id))
        caller = str(gl.message.sender_address)
        if caller.lower() != order["buyer"].lower():
            raise Exception("Only buyer can file claim for this order")
        if claim["status"] != "NO_CLAIM":
            raise Exception("Claim already filed for this order")
        claim.update({
            "status": "PENDING_REVIEW",
            "claim_type": claim_type,
            "description": description,
            "evidence_url": evidence_url,
        })
        self.claims[order_id] = json.dumps(claim)

    @gl.public.write
    def ai_review_claim(self, order_id: str) -> str:
        order_raw = self.orders.get(order_id)
        if order_raw is None:
            raise Exception("Order not found")
        order = json.loads(order_raw)
        claim = json.loads(self.claims.get(order_id))
        if claim["status"] != "PENDING_REVIEW":
            raise Exception("No pending claim to review")

        item_name = order["item_name"]
        price = order["price"]
        claim_type = claim["claim_type"]
        description = claim["description"]
        evidence_url = claim.get("evidence_url", "")

        def run_review() -> str:
            prompt = f"""
            You are an expert E-Commerce Buyer Protection AI Judge.
            You must DECIDE. Do NOT ask for photos if evidence_url is already provided.

            ORDER: Item: {item_name}, Price: {price}, Status: DELIVERED
            CLAIM: Type: {claim_type}, Description: {description}
            EVIDENCE PHOTO URL: {evidence_url if evidence_url else "NO EVIDENCE PROVIDED"}

            RULES:
            1. If buyer provided evidence_url AND description is detailed and consistent -> verdict = APPROVED, refund_percentage = 100.
            2. If NO evidence AND description is vague like "It is broken" -> verdict = NEED_MORE_EVIDENCE, refund_percentage = 0
            3. If description is contradictory or clearly lying (example: claim NOT_DELIVERED but buyer says "I used it for 2 weeks") -> verdict = REJECTED, refund_percentage = 0, is_fraud_suspected = true
            4. If description is detailed and consistent even without photo, you can still APPROVED.

            Return ONLY valid JSON in this exact format:
            {{
              "verdict": "APPROVED" or "REJECTED" or "NEED_MORE_EVIDENCE",
              "refund_percentage": 0 or 50 or 100,
              "confidence_score": 0-100,
              "reason": "Short clear explanation in English, max 2 sentences, mention if evidence was provided",
              "is_fraud_suspected": true or false
            }}
            """
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            return json.dumps(result, sort_keys=True)

        # FIX: prompt_comparative WAJIB ada principle sebagai argumen ke-2
        raw = gl.eq_principle.prompt_comparative(
            run_review,
            "Two JSON verdicts are equivalent if they have the same verdict value and the same refund_percentage. Ignore differences in wording of reason and small differences in confidence_score."
        )
        parsed = json.loads(raw)

        claim.update({
            "status": "REVIEWED",
            "verdict": parsed.get("verdict", "NEED_MORE_EVIDENCE"),
            "refund_percentage": parsed.get("refund_percentage", 0),
            "confidence_score": parsed.get("confidence_score", 0),
            "reason": parsed.get("reason", ""),
            "is_fraud_suspected": parsed.get("is_fraud_suspected", False),
        })
        self.claims[order_id] = json.dumps(claim)
        return json.dumps(claim)

    # ---------- VIEW ----------

    @gl.public.view
    def get_claim(self, order_id: str) -> str:
        if self.orders.get(order_id) is None:
            return "Order not found"
        return json.dumps({
            "order": json.loads(self.orders.get(order_id)),
            "claim": json.loads(self.claims.get(order_id))
        })

    @gl.public.view
    def get_order(self, order_id: str) -> str:
        if self.orders.get(order_id) is None:
            return "Order not found"
        return self.orders.get(order_id)
