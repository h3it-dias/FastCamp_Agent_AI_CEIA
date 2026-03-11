from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

stay_agent = Agent(
    name="stay_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests accommodation options at the destination within the user's budget.",
    instruction=(
        "Given a destination, travel dates, and budget, suggest 2-3 accommodation options. "
        "For each option, include the hotel or property name, area or neighborhood, estimated price per night, "
        "and key amenities. Prioritize comfortable and budget-friendly stays. "
        "Respond in plain English. Keep it concise and well-formatted."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=stay_agent,
    app_name="stay_app",
    session_service=session_service
)
USER_ID = "user_stay"
SESSION_ID = "session_stay"

async def execute(request):
    session_service.create_session(
        app_name="stay_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"User is traveling to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 accommodation options. "
        f"For each option include property name, area or neighborhood, estimated price per night, and key amenities. "
        f"Respond in JSON format using the key 'stays' with a list of stay objects."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "stays" in parsed and isinstance(parsed["stays"], list):
                    return {"stays": parsed["stays"]}
                else:
                    print("'stays' key missing or not a list in response JSON")
                    return {"stays": response_text}
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"stays": response_text}