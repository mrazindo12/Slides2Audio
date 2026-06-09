# Slide2Audio

Convert presentations, PDFs, Word documents, and text files into spoken MP3 audio — powered by AI.

Slide2Audio extracts text from your uploaded files, optionally rewrites it into a natural lecture script using Google Gemini, then synthesizes high-quality speech with Microsoft Edge TTS.

---

## How It Works

```
Upload File → Extract Text → (Optional) AI Lecture Script → Text-to-Speech → MP3 Audio
```

1. **Upload** a `.pptx`, `.pdf`, `.docx`, or `.txt` file
2. **Text extraction** pulls readable content from every slide, page, or paragraph
3. **AI enhancement** (optional) — Gemini rewrites the raw text into a natural, conversational lecture script
4. **Speech synthesis** — Edge TTS converts the text into an MP3 with your chosen voice
5. **Download** or play the generated audio directly in the browser

> If the Gemini API key is missing or the quota is exhausted, the app gracefully falls back to using the raw extracted text — it will always produce audio.

---

## Project Structure

```
Slide2Audio/
├── backend/                  # Python FastAPI server
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point & routes
│   │   ├── config.py         # Settings (env vars, CORS, paths)
│   │   ├── parse.py          # Text extraction (PPTX, PDF, DOCX, TXT)
│   │   ├── exceptions.py     # Custom exception classes & handlers
│   │   ├── validators.py     # Request/response schemas
│   │   ├── controllers/      # Request handling logic
│   │   ├── services/         # Business logic layer
│   │   │   ├── parser_service.py   # File parsing with validation
│   │   │   ├── tts_service.py      # Edge TTS audio generation
│   │   │   └── llm_service.py      # Gemini AI lecture generation
│   │   ├── models/           # Pydantic response models
│   │   └── tests/            # Pytest test suite
│   ├── audio/                # Generated MP3 files (auto-created)
│   ├── .env                  # Environment variables (API keys)
│   └── requirements.txt      # Python dependencies
│
└── frontend/                 # React + Vite UI
    ├── src/
    │   ├── App.jsx           # Main application component
    │   ├── App.css           # Component styles
    │   ├── index.css          # Global styles & design system
    │   └── main.jsx          # React entry point
    ├── index.html            # HTML shell
    ├── vite.config.js        # Vite config with API proxy
    └── package.json          # Node dependencies
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Gemini API Key** (optional — get one free at [aistudio.google.com](https://aistudio.google.com))

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Slide2Audio
```

### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment variables

Create or edit `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> Leave this empty or remove the line to skip the AI lecture generation step entirely. The app will still work using raw extracted text.

### 4. Frontend setup

```bash
cd frontend
npm install
```

---

## Running the App

You need **two terminals** — one for the backend, one for the frontend.

**Terminal 1 — Backend:**

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open the URL shown in the terminal (typically `http://localhost:5173`).

---

## API Reference

### `POST /convert`

Upload a file for conversion.

| Parameter | Type       | Description                          |
|-----------|------------|--------------------------------------|
| `file`    | `file`     | The document to convert (required)   |
| `voice`   | `string`   | Edge TTS voice ID (default: `en-US-AriaNeural`) |

**Response:**

```json
{
  "text_content": "The extracted or AI-generated lecture text...",
  "audio_filename": "3fa85f64-5717-4562-b3fc-2c963f66afa6.mp3"
}
```

### `GET /audio/{filename}`

Stream or download a generated MP3 file.

---

## Available Voices

| Voice ID                | Name                |
|-------------------------|---------------------|
| `en-US-AriaNeural`      | Aria (Female, US)   |
| `en-US-GuyNeural`       | Guy (Male, US)      |
| `en-GB-SoniaNeural`     | Sonia (Female, UK)  |
| `en-GB-RyanNeural`      | Ryan (Male, UK)     |
| `en-AU-NatashaNeural`   | Natasha (Female, AU)|
| `en-AU-WilliamNeural`   | William (Male, AU)  |

---

## Running Tests

```bash
cd backend
python -m pytest
```

---

## Supported File Types

| Format | Extension | What Gets Extracted                     |
|--------|-----------|------------------------------------------|
| PowerPoint | `.pptx` | Text from all shapes on every slide  |
| PDF        | `.pdf`  | Text from every page                 |
| Word       | `.docx` | Text from every paragraph            |
| Plain Text | `.txt`  | Full file contents                   |

---

## Tech Stack

| Layer    | Technology                                                  |
|----------|-------------------------------------------------------------|
| Frontend | React 19, Vite 8, Lucide Icons                             |
| Backend  | Python, FastAPI, Pydantic v2                                |
| AI       | Google Gemini 2.0 Flash (via `google-genai`)                |
| TTS      | Microsoft Edge TTS (via `edge-tts`)                         |
| Parsing  | `python-pptx`, `PyPDF2`, `python-docx`                     |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Blank page in browser | Make sure the frontend dev server is running and check the correct port in the terminal output |
| `RESOURCE_EXHAUSTED` / 429 error | Your Gemini free tier quota is used up. The app will still work — it falls back to raw text. Wait for quota to reset or upgrade your plan |
| `Audio file not found` | Make sure the backend is running. Generated audio is stored in `backend/audio/` |
| CORS errors | The backend allows `localhost:5173` and `localhost:5174` by default. Check that ports match |

---

## License

MIT
