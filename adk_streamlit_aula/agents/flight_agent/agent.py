from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Recommends flight options to a destination based on travel dates and budget.",
    instruction=(
        "Given a destination, travel dates, and budget, suggest 2-3 realistic flight options. "
        "For each option, include airline, departure and arrival times, estimated price, and number of stops. "
        "Prioritize affordable and practical flights that fit the user's budget. "
        "Respond in plain English. Keep it concise and well-formatted."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)
USER_ID = "user_flight"
SESSION_ID = "session_flight"

async def execute(request):
    session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User is traveling to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 realistic flight options. "
        f"For each option include airline, departure and arrival times, estimated price, and number of stops. "
        f"Respond in JSON format using the key 'flights' with a list of flight objects."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "flight" in parsed and isinstance(parsed["activities"], list):
                    return {"flight": parsed["flight"]}
                else:
                    print("'flights' key missing or not a list in response JSON")
                    return {"flights": response_text}
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"flights": response_text}