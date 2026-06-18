"""
src/tools/checkout_worker.py
─────────────────────────────
Guest checkout, bill calculation, and room release.

Billing Rules:
    - Always charge BOOKED nights minimum
    - If guest stays longer than booked → charge extra full days
    - Standard checkout time is 11:00 AM
    - If guest checks out AFTER 11:00 AM on their checkout day → fine per extra full day
    - Fine rate from .env: LATE_CHECKOUT_FINE_PER_DAY (default 2000)

Scenarios (3 nights booked July 20-23 at 3500/night):
    Checkout July 23 at 10:00 AM  →  10,500           (no fine)
    Checkout July 23 at 3:00 PM   →  10,500 + 2,000   (late fine)
    Checkout July 24 at 9:00 AM   →  14,000            (4 nights, no fine)
    Checkout July 24 at 2:00 PM   →  14,000 + 2,000   (4 nights + late fine)

Tools:
    checkout_guest  — process checkout and generate bill
    get_bill        — fetch bill for a completed stay
"""

import logging
import os
from datetime import datetime, timezone, timedelta

from livekit.agents import function_tool, RunContext

from src.database.db import get_db_conn

logger = logging.getLogger(__name__)

STANDARD_CHECKOUT_HOUR   = 11
STANDARD_CHECKOUT_MINUTE = 0
LATE_FINE_PER_DAY        = float(os.getenv("LATE_CHECKOUT_FINE_PER_DAY", "2000"))


def _calculate_bill(booked_checkin_date, booked_checkout_date, actual_checkout_ts, rate_per_night):
    """Core billing logic — pure function."""

    booked_nights = (booked_checkout_date - booked_checkin_date).days

    if actual_checkout_ts.tzinfo is None:
        actual_checkout_ts = actual_checkout_ts.replace(tzinfo=timezone.utc)

    # Extra nights beyond booked checkout date
    actual_checkout_date = actual_checkout_ts.date()
    extra_nights  = max(0, (actual_checkout_date - booked_checkout_date).days)
    actual_nights = booked_nights + extra_nights

    # Late fine — applies if guest is still in room after 11 AM
    # on their effective checkout day (booked date + any extra nights)
    effective_checkout_date = booked_checkout_date + timedelta(days=extra_nights)
    deadline = datetime(
        effective_checkout_date.year,
        effective_checkout_date.month,
        effective_checkout_date.day,
        STANDARD_CHECKOUT_HOUR,
        STANDARD_CHECKOUT_MINUTE,
        tzinfo=timezone.utc,
    )

    is_late       = actual_checkout_ts > deadline
    late_fine     = LATE_FINE_PER_DAY if is_late else 0.0
    base_amount   = actual_nights * rate_per_night
    total_amount  = base_amount + late_fine

    return {
        "booked_nights":  booked_nights,
        "actual_nights":  actual_nights,
        "extra_nights":   extra_nights,
        "rate_per_night": rate_per_night,
        "base_amount":    base_amount,
        "is_late":        is_late,
        "late_fine":      late_fine,
        "total_amount":   total_amount,
    }


@function_tool
async def checkout_guest(
    context: RunContext,
    guest_name: str,
    id_number: str,
):
    """
    Check out a guest, calculate their final bill, and release their room.
    Minimum charge is always the booked number of nights.
    Extra nights are charged if the guest stayed beyond their booked checkout date.
    A late fine is added if the guest checks out after 11 AM on their checkout day.
    Ask the guest for their name and ID number before calling this tool.
    """
    now_utc = datetime.now(timezone.utc)

    try:
        async with get_db_conn() as conn:

            # Find CHECKED_IN booking
            booking = await conn.fetchrow(
                """
                SELECT
                    b.booking_id, b.guest_name, b.id_number, b.status,
                    b.booked_checkin_date, b.booked_checkout_date,
                    b.actual_checkin_ts, b.digital_key,
                    r.room_number, r.room_type, r.rate_per_night
                FROM bookings b
                JOIN rooms r ON r.room_id = b.room_id
                WHERE LOWER(b.guest_name) = LOWER($1)
                  AND b.id_number        = UPPER($2)
                  AND b.status           = 'CHECKED_IN'
                LIMIT 1
                """,
                guest_name.strip(),
                id_number.strip(),
            )

            if not booking:
                # Check if already checked out
                already_out = await conn.fetchrow(
                    """
                    SELECT bi.total_amount
                    FROM bookings b
                    LEFT JOIN bills bi ON bi.booking_id = b.booking_id
                    WHERE LOWER(b.guest_name) = LOWER($1)
                      AND b.id_number        = UPPER($2)
                      AND b.status           = 'CHECKED_OUT'
                    ORDER BY b.actual_checkout_ts DESC
                    LIMIT 1
                    """,
                    guest_name.strip(),
                    id_number.strip(),
                )
                if already_out:
                    return (
                        f"You have already checked out. "
                        f"Your final bill was ₹{float(already_out['total_amount']):,.2f}. "
                        "We hope you enjoyed your stay at Grandview Hotel!"
                    )
                return "No active check-in found for that name and ID. Please verify your details."

            # Calculate bill
            bill = _calculate_bill(
                booked_checkin_date  = booking["booked_checkin_date"],
                booked_checkout_date = booking["booked_checkout_date"],
                actual_checkout_ts   = now_utc,
                rate_per_night       = float(booking["rate_per_night"]),
            )

            # Save bill + update booking atomically
            async with conn.transaction():
                await conn.execute(
                    """
                    UPDATE bookings
                    SET status             = 'CHECKED_OUT',
                        actual_checkout_ts = $1
                    WHERE booking_id = $2
                    """,
                    now_utc,
                    booking["booking_id"],
                )
                bill_id = await conn.fetchval(
                    """
                    INSERT INTO bills
                        (booking_id, booked_nights, actual_nights, rate_per_night,
                         base_amount, late_checkout_hours, late_fine, total_amount)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING bill_id
                    """,
                    booking["booking_id"],
                    bill["booked_nights"],
                    bill["actual_nights"],
                    bill["rate_per_night"],
                    bill["base_amount"],
                    1.0 if bill["is_late"] else 0.0,
                    bill["late_fine"],
                    bill["total_amount"],
                )

        logger.info(
            "Checkout: booking #%s | %s | Room %s | Total ₹%.2f",
            booking["booking_id"], booking["guest_name"],
            booking["room_number"], bill["total_amount"],
        )

        extra_note = (
            f" You stayed {bill['extra_nights']} extra night(s) beyond your booked checkout date."
            if bill["extra_nights"] else ""
        )
        fine_note = (
            f" A late checkout fine of ₹{bill['late_fine']:,.2f} was applied "
            "as you checked out after 11:00 AM."
            if bill["is_late"] else ""
        )

        return (
            f"Thank you for staying with us, {booking['guest_name']}! "
            f"You stayed for {bill['actual_nights']} night(s) in Room {booking['room_number']}."
            f"{extra_note}{fine_note} "
            f"Room rate: ₹{bill['rate_per_night']:,.2f} x {bill['actual_nights']} nights "
            f"= ₹{bill['base_amount']:,.2f}. "
            + (f"Late fine: ₹{bill['late_fine']:,.2f}. " if bill["is_late"] else "")
            + f"Total bill: ₹{bill['total_amount']:,.2f}. "
            "We hope to welcome you back soon. Goodbye and safe travels!"
        )

    except Exception as e:
        logger.exception("checkout_guest error")
        return f"Checkout failed. Please try again. Error: {str(e)}"


@function_tool
async def get_bill(
    context: RunContext,
    booking_id: int,
    id_number: str,
):
    """
    Fetch the bill for a completed booking.
    Useful if a guest calls back asking about their charges after checkout.
    booking_id is the ID given at time of booking.
    id_number is the guest ID for verification.
    """
    try:
        async with get_db_conn() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    b.guest_name, b.booked_checkin_date, b.booked_checkout_date,
                    b.actual_checkout_ts, r.room_number, r.room_type,
                    bi.booked_nights, bi.actual_nights, bi.rate_per_night,
                    bi.base_amount, bi.late_fine, bi.total_amount
                FROM bookings b
                JOIN rooms r  ON r.room_id    = b.room_id
                JOIN bills bi ON bi.booking_id = b.booking_id
                WHERE b.booking_id = $1
                  AND b.id_number  = UPPER($2)
                """,
                booking_id,
                id_number.strip(),
            )

        if not row:
            return (
                f"No bill found for booking {booking_id} with that ID. "
                "Please check your booking ID and ID number."
            )

        return (
            f"Bill for booking {booking_id}: {row['guest_name']}, "
            f"Room {row['room_number']} ({row['room_type']}). "
            f"{row['actual_nights']} night(s) at ₹{float(row['rate_per_night']):,.2f} "
            f"= ₹{float(row['base_amount']):,.2f}."
            + (f" Late checkout fine: ₹{float(row['late_fine']):,.2f}." if row["late_fine"] else "")
            + f" Total: ₹{float(row['total_amount']):,.2f}."
        )

    except Exception as e:
        logger.exception("get_bill error")
        return f"Could not retrieve bill. Error: {str(e)}"
