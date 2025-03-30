import os
import json
import datetime
import subprocess
import stripe
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_KEY")

campaign_start_date = int(datetime.datetime(2025, 1, 1).timestamp())

# Bank
bank_amount = 52

# Liberapay
command = "curl -s https://liberapay.com/YunoHost | grep receives | awk '{print $3}' | tr '<>' '@' | awk -F@ '{print $3}' | tr -d '€'"
output, error = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
liberapay_amount = float(output) * 4

# Stripe
stripe_recurring_amount = 0
stripe_one_time_amount = 0
recurring_donators_ids = set()
currencies = {
    "eur": 1,
    "usd": 0.908,
}

# Stripe: query recurring donations
subscriptions = stripe.Subscription.list(limit=100)
for sub in subscriptions.auto_paging_iter():
    recurring_donators_ids.add(sub["customer"])
    stripe_recurring_amount += sub["quantity"] * currencies[sub["currency"]]

# Stripe: query all payements since campaign start date
payments = stripe.PaymentIntent.search(
    query=f'created>{campaign_start_date} AND status:"succeeded"'
)
for payment in payments.auto_paging_iter():
    if payment["customer"] in recurring_donators_ids:
        # Ignore payments from recurring donators
        continue
    # Have to /100 the amounts (item units have a value of 100 for whatever reason)
    stripe_one_time_amount += payment["amount"] / 100 * currencies[sub["currency"]]


file = Path(__file__).parent.parent / "donate.json"
file.write_text(json.dumps({
    "recurring_amount": bank_amount + liberapay_amount + stripe_recurring_amount,
    "one_time_amount": stripe_one_time_amount
}))