import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class HubSpotClient:
    def __init__(self, access_token: str, base_url: str = "https://api.hubapi.com") -> None:
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")

    def is_enabled(self) -> bool:
        return bool(self.access_token and self.access_token.strip())

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query_params:
            url = f"{url}?{urllib.parse.urlencode(query_params)}"

        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
                if not raw_body:
                    return {}
                return json.loads(raw_body)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HubSpot API error {error.code}: {body}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"HubSpot connection failed: {error.reason}") from error

    def search_contact(self, email: str = "", phone: str = "") -> dict[str, Any] | None:
        filters: list[dict[str, str]] = []
        if email:
            filters.append(
                {
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email.strip(),
                }
            )
        if phone:
            filters.append(
                {
                    "propertyName": "phone",
                    "operator": "EQ",
                    "value": phone.strip(),
                }
            )

        if not filters:
            return None

        payload = {
            "filterGroups": [{"filters": filters}],
            "properties": ["firstname", "lastname", "email", "phone"],
            "limit": 1,
        }

        result = self._request("POST", "/crm/v3/objects/contacts/search", payload)
        contacts = result.get("results", [])
        if not contacts:
            return None
        return contacts[0]

    def create_contact(
        self,
        first_name: str,
        last_name: str = "",
        email: str = "",
        phone: str = "",
    ) -> dict[str, Any]:
        properties: dict[str, str] = {"firstname": first_name.strip()}
        if last_name:
            properties["lastname"] = last_name.strip()
        if email:
            properties["email"] = email.strip()
        if phone:
            properties["phone"] = phone.strip()

        return self._request("POST", "/crm/v3/objects/contacts", {"properties": properties})

    def update_contact(
        self,
        contact_id: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone: str = "",
    ) -> dict[str, Any]:
        properties: dict[str, str] = {}
        if first_name:
            properties["firstname"] = first_name.strip()
        if last_name:
            properties["lastname"] = last_name.strip()
        if email:
            properties["email"] = email.strip()
        if phone:
            properties["phone"] = phone.strip()

        if not properties:
            return {}

        return self._request(
            "PATCH",
            f"/crm/v3/objects/contacts/{contact_id}",
            {"properties": properties},
        )

    def upsert_contact(
        self,
        first_name: str,
        last_name: str = "",
        email: str = "",
        phone: str = "",
    ) -> tuple[str, str]:
        existing = self.search_contact(email=email, phone=phone)
        if existing:
            contact_id = existing.get("id", "")
            self.update_contact(
                contact_id=contact_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )
            return "updated", contact_id

        created = self.create_contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )
        return "created", str(created.get("id", ""))
