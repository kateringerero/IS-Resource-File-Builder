import requests
from requests.auth import HTTPBasicAuth
from app.services.platforms.base import BasePlatformService

class GorgiasService(BasePlatformService):
    def __init__(self, email: str, api_key: str, api_base_url: str):
        self.email = email
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")

    def fetch_ticket(self, ticket_id: str) -> dict:
        """
        Fetch ticket details
        """
        url = f"{self.api_base_url}/tickets/{ticket_id}"

        response = requests.get(
            url,
            auth=HTTPBasicAuth(self.email, self.api_key),
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def fetch_messages(self, ticket_id: str) -> list:
        """
        Fetch messages for a ticket
        """
        url = f"{self.api_base_url}/tickets/{ticket_id}/messages"

        response = requests.get(
            url,
            auth=HTTPBasicAuth(self.email, self.api_key),
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        # Gorgias usually wraps messages in "data"
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return data

    def extract_first_customer_and_agent(self, ticket_id: str):
        ticket = self.fetch_ticket(ticket_id)

        # IMPORTANT: messages are already inside ticket
        messages = ticket.get("messages", [])

        customer_message = None
        agent_response = None

        for msg in messages:
            body = (
                msg.get("stripped_text")  # BEST field (cleaned)
                or msg.get("body_text")
                or ""
            ).strip()

            if not body:
                continue

            # CUSTOMER MESSAGE
            if customer_message is None and msg.get("from_agent") is False:
                customer_message = body
                continue

            # AGENT RESPONSE
            if customer_message and agent_response is None and msg.get("from_agent") is True:
                agent_response = body
                break

        return customer_message, agent_response, ticket