from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import asyncio
from database import save_message
import aiohttp

# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# twilio_client = Client()
uri = os.environ.get("MONGO_DB_URI")


async def send_post_request(session, phone_number, message_body):
    url = " https://9eb0-92-98-156-59.ngrok-free.app/send_first_message"
    save_message(phone_number=phone_number, message_text=message_body, AI_response=True)

    data = {
        "phone_number": phone_number,
        "message_body": message_body,
    }

    async with session.post(url, data=data) as resp:
        response_text = await resp.text()
        return response_text


async def main():
    agents = get_numbers()

    async with aiohttp.ClientSession() as session:
        tasks = [
            send_post_request(
                session,
                agent["phone_number"],
                f"Hello, {agent['agent_name']}. Is the property with url {agent['property_url']} at {agent['property_location']} still available for rent?",
            )
            for agent in agents
        ]

        responses = await asyncio.gather(*tasks)

        for agent, response in zip(agents, responses):
            print(f"Response for {agent['agent_name']} - {response}")


def get_numbers() -> list[dict[str, str]]:
    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client["Bottest"]
    bayut_db = db["Bayut_data"]
    query = {}
    projection = {
        "agents.agent_name": 1,
        "agents.phone_number": 1,
        "properties": 1,
        "_id": 0,
    }
    cursor = bayut_db.find(query, projection)
    agents = [document for document in cursor]

    combined_agents = []
    for entry in agents:
        agents_list = entry.get("agents", [])
        for agent_info in agents_list:
            cleaned_agent = {
                "agent_name": agent_info.get("agent_name", ""),
                "phone_number": agent_info.get("phone_number", ""),
            }
            properties = agent_info.get("properties", [])
            # Fetch only apartments available for rent
            rent_properties = [
                d
                for d in properties
                if d.get("Purpose") == "For Rent" and d.get("Type") == "Apartment"
            ]
            if rent_properties:
                filtered_property = rent_properties[0]
                keys_to_retrieve = [
                    "property_url",
                    "Type",
                    "Purpose",
                    "Property_location",
                    "property_price",
                    "property_payment_frequency",
                ]
                filtered_property = {
                    key: filtered_property[key]
                    for key in keys_to_retrieve
                    if key in filtered_property
                }
                cleaned_agent.update(filtered_property)
                combined_agents.append(cleaned_agent)
            else:
                pass

    # return combined_agents
    return [
        {
            "agent_name": "Baraa Zaid",
            "phone_number": "+971526236758",
            "property_url": "https://www.bayut.com/property/details-8188736.html",
            "Type": "Apartment",
            "Purpose": "Rent",
            "property_location": "JVC, Dubai",
            "property_price": "AED 5000",
            "property_payment_frequency": "Monthly",
        }
    ]


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
