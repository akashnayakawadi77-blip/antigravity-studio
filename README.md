# Traveling Panda Agent - Content Pipeline Engine 🐼

This is a lightweight web application designed to automate the content pipeline for the YouTube travel channel hosted by the "Traveling Panda".

## Features
- **Real-Time Logistics Scraping:** Uses DuckDuckGo search to fetch the latest flight routes, hotel pricing tiers, and seasonal advisories.
- **AI Script Generation:** Leverages Google's Gemini API to write an 8-10 minute YouTube script based on a strict blueprint.
- **Formatting & SEO:** Auto-generates production tags (`[TRAVELING PANDA ON SCREEN]`, `[B-ROLL]`), a budget table, YouTube titles, description, and search tags.
- **Voiceover Placeholder:** Includes a service module for ElevenLabs API integration to generate the Traveling Panda's voice.

## Setup

1. **Install Dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys:**
   - Copy `.env.example` to a new file named `.env`
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_key_here
     ```
   - (Optional) Add your ElevenLabs API key.

3. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## Usage
1. Open the provided Local URL in your browser.
2. Enter a destination city (e.g., "Goa", "Kerala").
3. Click "Generate Script & Assets".
4. Review the scraped data and the final generated Markdown script. You can download the script directly from the interface.
