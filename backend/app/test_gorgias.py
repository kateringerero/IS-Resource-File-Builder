from app.services.platforms.gorgias_service import GorgiasService

service = GorgiasService(
    email="katherine@talentpopteam.co",
    api_key="985a4d749c504f293c69b63ca05b4892c5fc7dc6e7d0ddd07a8ca7bc039935e9",
    api_base_url="https://talentpopimplementation.gorgias.com/api/"
)

ticket_id = "251625875"

customer, agent, ticket = service.extract_first_customer_and_agent(ticket_id)

print("=== RAW TICKET ===")
print(ticket)

messages = service.fetch_messages(ticket_id)

print("\n=== RAW MESSAGES ===")
for m in messages[:5]:
    print(m)

print("\n=== EXTRACTED ===")
print("CUSTOMER:", customer)
print("AGENT:", agent)