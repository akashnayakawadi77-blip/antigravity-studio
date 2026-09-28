"""
Traveling Panda Chat Agent
Conversational travel planner that asks origin city, dates, preferences,
and generates hyper-detailed itineraries complete with Google Maps links, routes, real photos,
and robust 503 error retry handling.
"""
import os
import time
import datetime
import urllib.parse
from google import genai
from google.genai import types

def get_time_greeting() -> str:
    """Return a time-based greeting."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning! 🌅"
    elif 12 <= hour < 17:
        return "Good Afternoon! ☀️"
    else:
        return "Good Evening! 🌙"

def get_first_question() -> str:
    greeting = get_time_greeting()
    return f"{greeting} I'm your **Traveling Panda** 🐼✈️\n\nWhere would you like to travel? 🗺️"

# ── Conversation Questions (Smart & Direct) ──────────────────────────────────
QUESTIONS = [
    {
        "key": "destination",
        "panda_func": get_first_question,
        "placeholder": "Enter destination (e.g. Goa, Ujjain, Ladakh)...",
    },
    {
        "key": "origin_city",
        "panda": "Where will you be starting your journey from? (Starting City) 📍",
        "placeholder": "e.g. Mumbai, Delhi, Ahmedabad, Bangalore, Pune...",
    },
    {
        "key": "travel_dates",
        "panda": "What are your travel dates? 📅",
        "placeholder": "e.g. Nov 6 to Nov 16 2026, or Dec 15 to Dec 22...",
    },
    {
        "key": "travelers",
        "panda": "Who is traveling with you? 👥",
        "placeholder": "e.g. Solo, Couple, Family, Friends group...",
    },
    {
        "key": "budget",
        "panda": "What is your approximate budget? 💰",
        "placeholder": "e.g. ₹15,000 per person, Budget, Luxury...",
    },
    {
        "key": "stay_preference",
        "panda": "What type of stay do you prefer? 🏨",
        "placeholder": "e.g. Hostel, 3-Star Hotel, Resort, Homestay...",
    },
    {
        "key": "interests",
        "panda": "What are your main interests or planned activities? 🎯",
        "placeholder": "e.g. Temples, Beaches, Food, Trekking, Shopping...",
    },
    {
        "key": "special_requirements",
        "panda": "Any special requirements or preferences? 🙏",
        "placeholder": "e.g. Pure Veg, Senior citizen friendly, or 'No'...",
    },
]

# ── Detailed Itinerary Generator with Google Maps & 503 Auto-Retry ───────────
def generate_itinerary(answers: dict) -> str:
    """Generate an extensive, highly detailed travel itinerary with auto-retry and model fallback."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set.")

    client = genai.Client(api_key=api_key)

    origin = answers.get('origin_city', 'Starting City')
    dest   = answers.get('destination', 'Destination')

    system_prompt = f"""You are Traveling Panda - a world-class travel researcher and planner.
The traveler is starting their journey from: {origin}.
Destination: {dest}.

IMPORTANT RULES:
1. DEPARTURE CITY: Always plan departure from {origin} (NEVER assume Delhi or any other city unless specified by the user!).
2. GOOGLE MAPS INTEGRATION: Include a clickable Google Maps link for EVERY sight, temple, hotel, and restaurant mentioned.
   Format: [📍 Open in Google Maps](https://www.google.com/maps/search/?api=1&query=SPOT_NAME+{urllib.parse.quote(dest)})
3. ROUTING & DISTANCES: Include exact distance in km and travel duration (driving/auto/walk) between consecutive spots.
4. GRANULAR DETAILS:
   - Calculate exact trip duration from dates provided (e.g. Nov 6 to Nov 16 = 11 Days / 10 Nights)
   - Exact train names/numbers, flight options, highway routes from {origin} to {dest} with costs in INR
   - Specific hotel names with prices per night and exact locality
   - Exact temple/attraction entry fees, darshan timings, VIP pass info if applicable
   - Detailed budget breakdown table."""

    prompt = f"""
Create a comprehensive, hyper-detailed travel master plan for this traveler:

- Origin / Starting City: {origin}
- Destination: {dest}
- Travel Dates & Duration: {answers.get('travel_dates')}
- Travelers: {answers.get('travelers')}
- Budget: {answers.get('budget')}
- Accommodation Preference: {answers.get('stay_preference')}
- Primary Interests: {answers.get('interests')}
- Special Requirements: {answers.get('special_requirements')}

Please structure the output with the following rich sections:

# 🐼 Master Travel Guide & Itinerary: {dest}

### 🚀 1. Departure from {origin} & How to Reach
[Detailed flight, train (with train names/numbers), or road routes departing specifically from {origin} to {dest}. Include fare estimates in INR and journey duration]

### 🏨 2. Recommended Accommodations
[3-4 specific stay options tailored to their budget & preference, with prices in INR, exact area/locality, amenities, and Google Maps search link for each hotel]

### 📅 3. Day-by-Day Detailed Itinerary
[For EVERY day of the trip:
 Day 1: Departure from {origin} to {dest}
 Day 2..N: Morning, Afternoon, Evening breakdown with timings, attraction entry fees, Google Maps link for every spot, and distance/travel time between consecutive locations]

### 🍽️ 4. Food & Dining Guide
[Must-try local dishes, famous iconic eateries/street food spots, dish names, cost per meal, and Google Maps search link for key food spots]

### 💰 5. Complete Cost & Budget Breakdown
[Detailed Markdown table listing: Transport from {origin}, Accommodation, Food, Sightseeing & Entry Tickets, Miscellaneous = Total Estimated Cost per person and total group]

### 💡 6. Insider Pro Tips & Safety Advice
[Crucial local advice, dress code, best times to avoid lines/crowds, safety, and money-saving hacks]

Provide all information in a clear, well-formatted, professional Markdown layout.
"""

    models_to_try = [
        'gemini-3.8-flash',
        'gemini-3.7-flash',
        'gemini-3.5-flash',
        'gemini-3.5-flash-lite',
        'gemini-flash-latest',
        'gemini-flash-lite-latest',
        'gemini-2.5-flash-lite'
    ]
    last_error = None

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                    )
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                print(f"Gemini attempt {attempt+1} on model {model_name} failed: {e}")
                time.sleep(2 * (attempt + 1))

    raise last_error or Exception("Failed to generate itinerary after retries.")


def generate_video_script_from_plan(answers: dict, itinerary: str) -> str:
    """Convert the travel plan into a YouTube video script."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Based on this travel plan for {answers.get('destination')}, 
create a full 8-10 minute YouTube video script for Traveling Panda channel.

Travel Plan:
{itinerary[:3000]}

Follow script format with [TRAVELING PANDA ON SCREEN] and [B-ROLL] tags.
"""

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.75)
    )
    return response.text


def get_total_questions() -> int:
    return len(QUESTIONS)
