import os
import json
import datetime
import subprocess
import stripe
from pathlib import Path

stripe.api_key = os.getenv("STRIPE_KEY")

campaign_start_date = int(datetime.datetime(2026, 1, 1).timestamp())

# Bank (last update with 04/2026 data since campaign_start_date)
bank_amount = 82
bank_one_time_amount = 52

# Liberapay
command = "curl -s https://liberapay.com/YunoHost | grep receives | awk '{print $3}' | tr '<>' '@' | awk -F@ '{print $3}' | tr -d '€'"
output, error = subprocess.Popen(
    command, stdout=subprocess.PIPE, shell=True
).communicate()
liberapay_amount = float(output) * 4

# Stripe
stripe_recurring_amount = 0
stripe_one_time_amount = 0
recurring_donators_ids = set()
currencies = {
    "eur": 1,
    "usd": 0.8513,
}


def compute_amount(amount, currency):
    euros = amount * currencies[currency]
    fee = euros * (1.5 / 100) + 0.25
    return euros - fee


# Stripe: query recurring donations
subscriptions = stripe.Subscription.list(limit=100)
for sub in subscriptions.auto_paging_iter():
    recurring_donators_ids.add(sub["customer"])
    stripe_recurring_amount += compute_amount(sub["quantity"], sub["currency"])

# Stripe: query all payements since campaign start date
payments = stripe.PaymentIntent.search(
    query=f'created>{campaign_start_date} AND status:"succeeded"'
)
for payment in payments.auto_paging_iter():
    if payment["customer"] in recurring_donators_ids:
        # Ignore payments from recurring donators
        continue
    # Have to /100 the amounts (item units have a value of 100 for whatever reason)
    stripe_one_time_amount += compute_amount(payment["amount"] / 100, sub["currency"])


file = Path(__file__).parent.parent / "donate.json"
file.write_text(
    json.dumps(
        {
            "recurring_amount": round(bank_amount
            + liberapay_amount
            + stripe_recurring_amount),
            "one_time_amount": round(stripe_one_time_amount
            + bank_one_time_amount),
        }
    )
)
