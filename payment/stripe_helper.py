import datetime

import stripe

from django.urls import reverse

from library_config import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = 1.5


def count_start_price(borrowing):

    days_borrowing = (borrowing.expected_return_date - borrowing.borrow_date).days + 1

    start_price_in_cents = int(
        days_borrowing
        * float(borrowing.book.daily)
        * 100
    )

    return start_price_in_cents


def count_fine_price(borrowing):
    overdue_days = (
            borrowing.actual_return_date
            - borrowing.expected_return_date
    ).days

    fine_price_in_cents = int(
        overdue_days
        * float(borrowing.book.daily)
        * FINE_MULTIPLIER
        * 100
    ) if overdue_days > 0 else 0

    return fine_price_in_cents


def create_payment(borrowing, session):
    payment = Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        user=borrowing.user
    )

    if borrowing.actual_return_date:
        if borrowing.actual_return_date > borrowing.expected_return_date:
            payment.type = "FINE"
            payment.money_to_pay = round(
                count_fine_price(borrowing) / 100, 2
            )
            payment.save()

            return payment

    payment.money_to_pay = round(
        count_start_price(borrowing) / 100, 2
    )
    payment.save()
    return payment


def create_stripe_session(borrowing, request):

    success_url = request.build_absolute_uri(
        reverse(
            "payment:payment-success",
            args=[borrowing.id]
        )
    )
    cancel_url = request.build_absolute_uri(
        reverse(
            "payment:payment-cancel",
            args=[borrowing.id]
        )
    )
    if borrowing.borrow_date == datetime.date.today():
        price_in_cents = count_start_price(borrowing)
    else:
        price_in_cents = count_fine_price(borrowing)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": price_in_cents,
                "product_data": {
                    "name": borrowing.book.title,
                    "description": f"User: {borrowing.user.email}",
                },
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = create_payment(borrowing, session)

    borrowing.payments.add(payment)
    borrowing.save()

    return session.url
