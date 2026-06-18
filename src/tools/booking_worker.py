"""
src/tools/booking_worker.py
────────────────────────────
Hotel booking tools — reserve rooms before guest arrives.

Tools:
    check_availability  — list free rooms for a date range
    book_room           — create a reservation
    cancel_booking      — cancel an existing booking
"""

import json
import logging
from datetime import date, datetime

from livekit.agents import function_tool, RunContext

from src.database.db import get_db_conn

logger = logging.getLogger(__name__)


def _parse_date(date_str: str) -> date:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Could not parse date '{date_str}'. Please use YYYY-MM-DD format e.g. 2026-07-15."
    )


@function_tool
async def check_availability(
    context: RunContext,
    checkin_date: str,
    checkout_date: str,
    room_type: str = "any",
):
    """
    Check which rooms are available for a given date range.
    Always call this before book_room so the guest can choose a room.
    checkin_date and checkout_date must be in YYYY-MM-DD format.
    room_type can be Standard, Deluxe, Suite, Penthouse, or any.
    """
    try:
        checkin  = _parse_date(checkin_date)
        checkout = _parse_date(checkout_date)
    except ValueError as e:
        return str(e)

    if checkout <= checkin:
        return "Checkout date must be after check-in date."

    if checkin < date.today():
        return "Check-in date cannot be in the past."

    nights = (checkout - checkin).days

    try:
        async with get_db_conn() as conn:
            type_filter = "" if room_type.lower() == "any" else "AND r.room_type ILIKE $3"

            query = f"""
                SELECT r.room_number, r.room_type, r.rate_per_night,
                       r.max_occupancy, r.description
                FROM rooms r
                WHERE r.is_active = TRUE
                  {type_filter}
                  AND r.room_id NOT IN (
                      SELECT b.room_id FROM bookings b
                      WHERE b.status IN ('BOOKED', 'CHECKED_IN')
                        AND b.booked_checkin_date  < $2
                        AND b.booked_checkout_date > $1
                  )
                ORDER BY r.rate_per_night, r.room_number
            """
            params = [checkin, checkout]
            if room_type.lower() != "any":
                params.append(f"%{room_type}%")

            rows = await conn.fetch(query, *params)

        if not rows:
            return (
                f"No {room_type} rooms available from {checkin_date} to {checkout_date}. "
                "Please try different dates or a different room type."
            )

        result = f"Available rooms from {checkin_date} to {checkout_date} ({nights} nights):\n"
        for r in rows:
            total = float(r["rate_per_night"]) * nights
            result += (
                f"- Room {r['room_number']} | {r['room_type']} | "
                f"₹{float(r['rate_per_night']):,.0f}/night | "
                f"Total: ₹{total:,.0f} | {r['description']}\n"
            )
        return result

    except Exception as e:
        logger.exception("check_availability error")
        return f"Sorry, I could not check availability right now. Error: {str(e)}"


@function_tool
async def book_room(
    context: RunContext,
    guest_name: str,
    id_number: str,
    room_number: str,
    checkin_date: str,
    checkout_date: str,
    special_requests: str = "",
):
    """
    Create a new room booking for a guest.
    Always call check_availability first to confirm the room is free.
    guest_name is the full name of the guest.
    id_number is the guest government-issued ID.
    room_number is the room to book e.g. 101.
    checkin_date and checkout_date must be in YYYY-MM-DD format.
    special_requests is optional any special needs the guest has.
    """
    try:
        checkin  = _parse_date(checkin_date)
        checkout = _parse_date(checkout_date)
    except ValueError as e:
        return str(e)

    if checkout <= checkin:
        return "Checkout date must be after check-in date."

    nights = (checkout - checkin).days

    try:
        async with get_db_conn() as conn:

            # Look up room
            room = await conn.fetchrow(
                "SELECT room_id, room_type, rate_per_night FROM rooms "
                "WHERE room_number = $1 AND is_active = TRUE",
                room_number,
            )
            if not room:
                return f"Room {room_number} not found. Please call check_availability to see valid rooms."

            # Race condition guard — double check availability
            conflict = await conn.fetchrow(
                """
                SELECT booking_id FROM bookings
                WHERE room_id = $1
                  AND status IN ('BOOKED', 'CHECKED_IN')
                  AND booked_checkin_date  < $3
                  AND booked_checkout_date > $2
                """,
                room["room_id"], checkin, checkout,
            )
            if conflict:
                return (
                    f"Room {room_number} is no longer available for those dates. "
                    "Please call check_availability again to find another room."
                )

            # Create booking
            booking_id = await conn.fetchval(
                """
                INSERT INTO bookings
                    (guest_name, id_number, room_id,
                     booked_checkin_date, booked_checkout_date,
                     special_requests, status)
                VALUES ($1, $2, $3, $4, $5, $6, 'BOOKED')
                RETURNING booking_id
                """,
                guest_name.strip().title(),
                id_number.strip().upper(),
                room["room_id"],
                checkin,
                checkout,
                special_requests.strip() or None,
            )

        total = float(room["rate_per_night"]) * nights
        logger.info("Booking created: #%s | %s | Room %s", booking_id, guest_name, room_number)

        return (
            f"Booking confirmed! Your booking ID is {booking_id}. "
            f"Room {room_number} ({room['room_type']}) is reserved for {nights} night(s) "
            f"from {checkin_date} to {checkout_date}. "
            f"Estimated total: ₹{total:,.2f}. "
            "Please bring your ID when you arrive to check in."
            + (f" Special requests noted: {special_requests}." if special_requests else "")
        )

    except Exception as e:
        logger.exception("book_room error")
        return f"Booking failed. Please try again. Error: {str(e)}"


@function_tool
async def cancel_booking(
    context: RunContext,
    booking_id: int,
    id_number: str,
):
    """
    Cancel an existing booking.
    Only BOOKED reservations can be cancelled — not ones already checked in.
    booking_id is the ID given at time of booking.
    id_number is the guest ID for identity verification.
    """
    try:
        async with get_db_conn() as conn:

            booking = await conn.fetchrow(
                """
                SELECT b.booking_id, b.guest_name, b.id_number, b.status,
                       b.booked_checkin_date, b.booked_checkout_date, r.room_number
                FROM bookings b
                JOIN rooms r ON r.room_id = b.room_id
                WHERE b.booking_id = $1
                """,
                booking_id,
            )

            if not booking:
                return f"No booking found with ID {booking_id}."

            if booking["id_number"].upper() != id_number.strip().upper():
                return "ID number does not match our records. Cannot cancel."

            if booking["status"] == "CHECKED_IN":
                return "Cannot cancel a booking that is already checked in. Please speak to the front desk."

            if booking["status"] in ("CHECKED_OUT", "CANCELLED"):
                return f"Booking {booking_id} is already {booking['status']}."

            await conn.execute(
                "UPDATE bookings SET status = 'CANCELLED' WHERE booking_id = $1",
                booking_id,
            )

        logger.info("Booking #%s cancelled by %s", booking_id, booking["guest_name"])
        return (
            f"Booking {booking_id} has been successfully cancelled. "
            f"Room {booking['room_number']} is now released. "
            "We hope to welcome you another time!"
        )

    except Exception as e:
        logger.exception("cancel_booking error")
        return f"Cancellation failed. Please try again. Error: {str(e)}"
