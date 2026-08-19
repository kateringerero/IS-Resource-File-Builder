from app.services.platforms.base import BasePlatformService

class ZendeskService(BasePlatformService):
    def extract_first_customer_and_agent(self, external_ticket_id: str):
        # implement Zendesk logic
        pass