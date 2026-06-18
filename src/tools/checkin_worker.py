"""
src/tools/checkin_worker.py  (REVISED)
───────────────────────────────────────
Physical check-in when a guest arrives at the hotel.
Guest must already have a booking (created by booking_worker).

Tools:
    check_in_guest      — verify booking, issue digital key
    get_checkin_status  — check if a room is occupied
"""

import json
import logging
import random
import string
from datetime import date

from livekit.agents import function_tool, RunContext

from src.database.db import get_db_conn

logger = logging.getLogger(__name__)


def _generate_digital_key(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@function_tool
async def check_in_guest(
    context: RunContext,
    guest_name: str,
    id_number: str,
):
    """
    Check in a guest who has an existing booking and has physically arrived at the hotel.
    Verifies their identity, confirms the booking, issues a digital room key,
    and marks the room as CHECKED_IN.
    Ask the guest for their name and ID number before calling this tool.
    If the guest does not have a booking, offer to book a room for them using book_room.
    """
    today = date.today()

    try:
        async with get_db_conn() as conn:

            # Find BOOKED reservation for this guest
            booking = await conn.fetchrow(
                """
                SELECT
                    b.booking_id, b.guest_name, b.id_number, b.status,
                    b.booked_checkin_date, b.booked_checkout_date,
                    b.special_requests,
                    r.room_number, r.room_type, r.rate_per_night
                FROM bookings b
                JOIN rooms r ON r.room_id = b.room_id
                WHERE LOWER(b.guest_name) = LOWER($1)
                  AND b.id_number        = UPPER($2)
                  AND b.status           = 'BOOKED'
                ORDER BY b.booked_checkin_date ASC
                LIMIT 1
                """,
                guest_name.strip(),
                id_number.strip(),
            )

            if not booking:
                # Check if already checked in
                already_in = await conn.fetchrow(
                    """
                    SELECT r.room_number, b.digital_key
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
                if already_in:
                    return (
                        f"You are already checked into Room {already_in['room_number']}. "
                        f"Your digital key is {already_in['digital_key']}. "
                        "Is there anything else I can help you with?"
                    )

                return (
                    "No active booking found for that name and ID. "
                    "Please check your details or I can make a new booking for you right now."
                )

            # Date check — don't check in too early
            checkin_date = booking["booked_checkin_date"]
            if today < checkin_date:
                days_early = (checkin_date - today).days
                return (
                    f"Your booking starts on {checkin_date}. "
                    f"That is {days_early} day(s) from today. "
                    "Early check-in is subject to availability. Please speak to the front desk."
                )

            # Issue digital key and stamp check-in time
            digital_key = _generate_digital_key()
            await conn.execute(
                """
                UPDATE bookings
                SET status            = 'CHECKED_IN',
                    digital_key       = $1,
                    actual_checkin_ts = NOW() AT TIME ZONE 'UTC'
                WHERE booking_id = $2
                """,
                digital_key,
                booking["booking_id"],
            )

        nights   = (booking["booked_checkout_date"] - checkin_date).days
        special  = booking["special_requests"] or ""

        logger.info(
            "Check-in: booking #%s | %s | Room %s | key=%s",
            booking["booking_id"], booking["guest_name"],
            booking["room_number"], digital_key,
        )

        return (
            f"Welcome to Grandview Hotel, {booking['guest_name']}! "
            f"You are now checked into Room {booking['room_number']} ({booking['room_type']}). "
            f"Your digital key is {digital_key}. "
            f"Your stay is for {nights} night(s), checking out on {booking['booked_checkout_date']}. "
            + (f"We have noted your special requests: {special}. " if special else "")
            + "Enjoy your stay!"
        )

    except Exception as e:
        logger.exception("check_in_guest error")
        return f"Check-in failed. Please try again. Error: {str(e)}"


@function_tool
async def get_checkin_status(
    context: RunContext,
    room_number: str,
):
    """
    Check whether a specific room is currently AVAILABLE, BOOKED, or CHECKED_IN.
    room_number is the room to check e.g. 101.
    """
    try:
        async with get_db_conn() as conn:
            row = await conn.fetchrow(
                """
                SELECT b.status, b.guest_name,
                       b.booked_checkin_date, b.booked_checkout_date
                FROM bookings b
                JOIN rooms r ON r.room_id = b.room_id
                WHERE r.room_number = $1
                  AND b.status IN ('BOOKED', 'CHECKED_IN')
                ORDER BY b.booked_checkin_date ASC
                LIMIT 1
                """,
                room_number,
            )

        if not row:
            return f"Room {room_number} is currently AVAILABLE."

        if row["status"] == "CHECKED_IN":
            return (
                f"Room {room_number} is OCCUPIED by {row['guest_name']}, "
                f"checking out on {row['booked_checkout_date']}."
            )
        else:
            return (
                f"Room {room_number} is BOOKED for {row['guest_name']}, "
                f"arriving on {row['booked_checkin_date']}."
            )

    except Exception as e:
        logger.exception("get_checkin_status error")
        return f"Could not check room status. Error: {str(e)}"
