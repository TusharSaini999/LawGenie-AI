# LawGenie AI

LawGenie AI is a React + Vite frontend for an AI legal assistant focused on Indian law research and document-aware Q&A. It includes a modern landing page, an interactive chat interface, file attachment support, and configurable API integration.

## Highlights

- AI chat interface for legal questions
- File attachment support in chat (`.pdf`, `.txt`, `.csv`, `.doc`, `.docx`)
- Message history UI with typing state and timestamps
- Theme switching (light, dark, system)
- Responsive landing page with feature and use-case sections
- Axios-based API client with centralized environment configuration

## Tech Stack

- React 19
- Vite 7
- Tailwind CSS 4
- React Router 7
- Axios
- Heroicons
- Vanta.js + Three.js

## Project Structure

```text
LawGenie-AI/
├─ Frontend/
│  ├─ public/
│  ├─ src/
│  │  ├─ api/                # API wrappers
│  │  ├─ components/         # Reusable UI components
│  │  ├─ config/             # Environment configuration
│  │  ├─ constants/          # Static messages/rules
│  │  ├─ hooks/              # Custom hooks (theme)
│  │  ├─ layouts/            # App layout shell
│  │  ├─ pages/              # Route pages (landing/chat)
│  │  └─ services/           # Chat service abstraction
│  ├─ index.html
│  ├─ package.json
│  └─ vite.config.js
└─ LICENSE
```

## Getting Started

### 1) Prerequisites

- Node.js 20+ (recommended)
- npm 10+ (recommended)

### 2) Install dependencies

```bash
cd Frontend
npm install
```

### 3) Configure environment

Create a `.env` file inside `Frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

> The app requires `VITE_API_BASE_URL` at startup.

### 4) Run development server

```bash
npm run dev
```

Default dev server: `http://localhost:5178`

## Available Scripts

From the `Frontend/` directory:

- `npm run dev` — Start Vite development server
- `npm run build` — Create production build
- `npm run preview` — Preview production build locally
- `npm run lint` — Run ESLint

## API Expectations

The frontend posts chat requests to:

- `POST /chat/`

Request payload shape:

```json
{
  "message": "string",
  "attachments": [
    {
      "name": "file.pdf",
      "size": 123456,
      "type": "application/pdf"
    }
  ]
}
```

The UI accepts any of these response fields as assistant text:

- `answer`
- `response`
- `message`
- `data.answer`
- `data.message`

## Notes

- Path alias `@` points to `Frontend/src`.
- Chat input limits: up to 2 files, 5 MB per file, message length up to 2000 characters.
- If the API is unreachable or returns an unexpected payload, a fallback error message is shown in chat.
