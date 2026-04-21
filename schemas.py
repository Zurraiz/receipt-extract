"""
Document schemas — each schema defines what fields to extract.
To customize for a new client: copy an existing schema, rename it, adjust fields.
The AI prompt is built automatically from whatever fields you define here.
"""

SCHEMAS = {

    "invoice": {
        "label": "Invoice",
        "fields": {
            "vendor_name":      "Name of the company/vendor issuing the invoice",
            "vendor_address":   "Full address of the vendor",
            "invoice_number":   "Invoice or reference number",
            "invoice_date":     "Date the invoice was issued",
            "due_date":         "Payment due date if present",
            "bill_to":          "Name or company the invoice is billed to",
            "line_items":       "List of items/services with description, quantity, unit price, and total",
            "subtotal":         "Subtotal before tax",
            "tax":              "Tax amount or percentage",
            "discount":         "Discount amount if any",
            "total_amount":     "Final total amount due",
            "currency":         "Currency code or symbol (e.g. USD, GBP, €)",
            "payment_terms":    "Payment terms (e.g. Net 30)",
            "notes":            "Any additional notes or payment instructions"
        }
    },

    "receipt": {
        "label": "Receipt",
        "fields": {
            "store_name":       "Name of the store or merchant",
            "store_address":    "Address of the store",
            "date":             "Date of purchase",
            "time":             "Time of purchase if present",
            "items":            "List of purchased items with name, quantity, and price",
            "subtotal":         "Subtotal before tax",
            "tax":              "Tax amount",
            "total":            "Total amount paid",
            "payment_method":   "How it was paid (cash, card, etc.)",
            "card_last_four":   "Last 4 digits of card if shown",
            "receipt_number":   "Receipt or transaction number"
        }
    },

    "purchase_order": {
        "label": "Purchase Order",
        "fields": {
            "po_number":        "Purchase order number",
            "issue_date":       "Date the PO was issued",
            "buyer_name":       "Name of the buying company",
            "buyer_address":    "Address of the buyer",
            "supplier_name":    "Name of the supplier",
            "supplier_address": "Address of the supplier",
            "items":            "List of ordered items with description, quantity, unit price, and total",
            "delivery_date":    "Expected delivery date",
            "shipping_address": "Delivery address if different from buyer",
            "subtotal":         "Subtotal",
            "tax":              "Tax amount",
            "total":            "Total order value",
            "payment_terms":    "Payment terms",
            "notes":            "Special instructions or notes"
        }
    },

    "bank_statement": {
        "label": "Bank Statement",
        "fields": {
            "bank_name":        "Name of the bank",
            "account_holder":   "Name on the account",
            "account_number":   "Account number (last 4 digits only if partially masked)",
            "statement_period": "Period covered by the statement",
            "opening_balance":  "Balance at the start of the period",
            "closing_balance":  "Balance at the end of the period",
            "transactions":     "List of transactions with date, description, debit, credit, and balance",
            "total_debits":     "Total amount debited",
            "total_credits":    "Total amount credited"
        }
    },

    "custom": {
        "label": "Custom",
        "fields": {}
    }

}


def get_schema(name: str) -> dict:
    return SCHEMAS.get(name, SCHEMAS["invoice"])


def list_schemas() -> list:
    return [{"id": k, "label": v["label"]} for k, v in SCHEMAS.items()]
