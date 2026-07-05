#!/usr/bin/env python3

import datetime
import json
import os
from pathlib import Path

import requests
import stripe

campaign_start_date = int(datetime.datetime(2026, 1, 1).timestamp())

# Bank (last update with 04/2026 data since campaign_start_date)
bank_amount = 82
bank_one_time = 52


def get_liberapay_amounts(org: str) -> tuple[float, float]:
    # Get amount from web page html
    response = requests.get(f"https://liberapay.com/{org}")
    if response.text is None:
        return 0, 0
    html = response.text.splitlines()
    line_receives = next((line for line in html if "receives" in line))
    if not line_receives:
        return 0, 0
    valuestr = line_receives.split("<b>", 1)[1].split("</b>", 1)[0]
    value = float(valuestr.strip("€"))
    # monthly
    return (value * 4, 0)


def get_stripe_amounts(api_key: str) -> tuple[float, float]:
    def compute_amount(amount: float, currency: str) -> float:
        currencies = {
            "eur": 1,
            "usd": 0.8513,
        }
        euros = amount * currencies[currency]
        fee = euros * (1.5 / 100) + 0.25
        return euros - fee

    recurring_amount = 0
    one_time_amount = 0
    recurring_donators_ids = set()

    client = stripe.StripeClient(api_key)

    # Stripe: query recurring donations
    subscriptions = client.v1.subscriptions.list()
    for sub in subscriptions.auto_paging_iter():
        recurring_donators_ids.add(sub["customer"])
        recurring_amount += compute_amount(sub["quantity"], sub["currency"])

    # Stripe: query all payements since campaign start date
    query = f'created>{campaign_start_date} AND status:"succeeded"'
    payments = client.v1.payment_intents.search({"query": query})
    for payment in payments.auto_paging_iter():
        # if payment["customer"] in recurring_donators_ids:
        #     # Ignore payments from recurring donators
        #     continue
        # Have to /100 the amounts (item units have a value of 100 for whatever reason)
        amount = compute_amount(payment["amount"] / 100, payment["currency"])
        one_time_amount += amount

    return recurring_amount, one_time_amount


def dump_donate_json(recurring: float, one_time: float) -> None:
    file = Path(__file__).parent.parent / "donate.json"
    data = {"recurring_amount": recurring, "one_time_amount": one_time}
    file.write_text(json.dumps(data))


def main() -> None:
    stripe_api_key = os.getenv("STRIPE_KEY")
    if stripe_api_key is None:
        raise RuntimeError("Please set STRIPE_KEY environment variable!")

    liberapay_recurring, liberapay_one_time = get_liberapay_amounts("YunoHost")
    stripe_recurring, stripe_one_time = get_stripe_amounts(stripe_api_key)

    recurring = round(bank_amount + liberapay_recurring + stripe_recurring)
    one_time = round(bank_one_time + liberapay_one_time + stripe_one_time)
    dump_donate_json(recurring, one_time)


if __name__ == "__main__":
    main()
