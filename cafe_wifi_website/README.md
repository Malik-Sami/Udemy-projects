# LaptopFriendly London ☕💻

A curated remote-work cafe directory for London, inspired by [laptopfriendly.co](https://laptopfriendly.co/london) and built as part of the 100 Days of Code (Day 66 & Day 68) Bootcamp.

## Features

- **Rich Modern UI**: Dark glassmorphic design inspired by artisan espresso crema and dark roast tones, with a toggle for Cream Light mode.
- **SQLite Database**: Uses the full `cafes.db` dataset (21+ London spots including Shoreditch, Peckham, London Bridge, South Kensington, Whitechapel, and Clerkenwell).
- **Work-Friendly Scoring**: Automatically calculates an amenity work score (out of 10) based on verified high-speed Wi-Fi, power sockets, call allowance, restrooms, and seat capacity.
- **Real-Time Instant Filtering**: Instant client-side search by name/street/borough, neighborhood dropdown selector, and amenity chips (Power Sockets, Fast Wi-Fi, Call Friendly, Restrooms, Spacious).
- **Multi-criteria Sorting**: Sort by Top Work Score, Price (Low to High / High to Low), Seat capacity, or Alphabetical.
- **View Toggle**: Switch between Grid Card View and List View.
- **Suggest / Add Cafe Modal**: Interactive modal with **real-time live card preview** as you type, and photography presets.
- **Delete / Report Cafe**: Confirmation modal with support for the Day 66 admin API key (`TopSecretAPIKey`).
- **Lucky Pick**: "Feeling lucky?" button that rolls and spotlights a random cafe.
- **Day 66 RESTful API**: Built-in REST API endpoints with an interactive live tester console:
  - `GET /api/cafes` or `GET /api/all` — List all cafes in JSON
  - `GET /api/random` — Fetch a random cafe
  - `GET /api/search?loc=<location>` — Search cafes by location
  - `POST /api/add` — Add a new cafe
  - `PATCH /api/update-price/<id>?new_price=<price>` — Update coffee price
  - `DELETE /api/delete/<id>?api-key=TopSecretAPIKey` — Delete a cafe

## Tech Stack

- **Backend**: Python 3.12, Flask, Flask-SQLAlchemy, SQLite
- **Frontend**: Semantic HTML5, Vanilla CSS3 (modern glassmorphism, responsive grid), Vanilla JavaScript (no heavy frontend frameworks required)
- **Icons & Typography**: Font Awesome 6, Google Fonts (*Outfit* & *Plus Jakarta Sans*)

## Getting Started

From the workspace root or inside `cafe_wifi_website/`:

```bash
# Using uv (recommended)
uv run python cafe_wifi_website/main.py

# Or directly with Python
cd cafe_wifi_website
python main.py
```

Then open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)
