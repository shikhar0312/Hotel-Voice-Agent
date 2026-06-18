import asyncio

from livekit.agents import RunContext, function_tool

from src.config.settings import settings
from src.infrastructure.crm import HubSpotClient
from src.utils.logger import logger

hubspot_client = HubSpotClient(
    access_token=settings.HUBSPOT_ACCESS_TOKEN,
    base_url=settings.HUBSPOT_API_BASE_URL,
)


def _hubspot_not_configured_message() -> str:
    return (
        "HubSpot CRM is not configured. Please add HUBSPOT_ACCESS_TOKEN in your .env file "
        "for private app access."
    )


@function_tool
async def hubspot_find_contact(context: RunContext, email: str = "", phone: str = ""):
    """Find a HubSpot contact by email or phone number."""
    if not hubspot_client.is_enabled():
        return _hubspot_not_configured_message()

    if not email and not phone:
        return "Please provide at least one field: email or phone."

    logger.info(f"HubSpot contact lookup. email={email}, phone={phone}")

    try:
        contact = await asyncio.to_thread(hubspot_client.search_contact, email, phone)
    except Exception as error:
        logger.error(f"HubSpot lookup failed: {error}")
        return f"HubSpot lookup failed: {error}"

    if not contact:
        return "No HubSpot contact found for the provided details."

    props = contact.get("properties", {})
    first = props.get("firstname", "")
    last = props.get("lastname", "")
    full_name = f"{first} {last}".strip() or "Unknown"
    return (
        f"Found HubSpot contact {full_name}. "
        f"Email: {props.get('email', 'N/A')}. "
        f"Phone: {props.get('phone', 'N/A')}. "
        f"Contact ID: {contact.get('id', 'N/A')}."
    )


@function_tool
async def hubspot_upsert_contact(
    context: RunContext,
    first_name: str,
    last_name: str = "",
    email: str = "",
    phone: str = "",
):
    """Create or update a HubSpot contact using email/phone matching."""
    if not hubspot_client.is_enabled():
        return _hubspot_not_configured_message()

    if not first_name:
        return "First name is required to create or update a HubSpot contact."

    if not email and not phone:
        return "Provide at least one identifier: email or phone."

    logger.info(
        "HubSpot upsert request. "
        f"first_name={first_name}, last_name={last_name}, email={email}, phone={phone}"
    )

    try:
        action, contact_id = await asyncio.to_thread(
            hubspot_client.upsert_contact,
            first_name,
            last_name,
            email,
            phone,
        )
    except Exception as error:
        logger.error(f"HubSpot upsert failed: {error}")
        return f"HubSpot upsert failed: {error}"

    return f"HubSpot contact {action} successfully. Contact ID: {contact_id or 'N/A'}."
