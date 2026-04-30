# 🔗 Linklyt AI — Illuminate Any Link

Linklyt is a high-performance **RAG (Retrieval-Augmented Generation)** application that allows you to scrape, index, and chat with any website in seconds. Powered by the world's fastest inference engine and robust cloud scraping, Linklyt turns static web pages into interactive knowledge bases.

![Linklyt Dashboard](https://linklyt-tau.vercel.app/og-image.png) *(Note: Replace with your actual OG image or screenshot)*

## 🚀 Key Features

- **Instant URL Analysis**: Scrapes any website (including JS-heavy sites) using Firecrawl.
- **Lightning Fast Q&A**: Answers questions in ~1 second using Groq's LPU technology and Llama 3.1.
- **Persistent Memory**: Uses Supabase with `pgvector` for efficient semantic search.
- **One-Click Automation**: Seamlessly exports research summaries and answers to Google Sheets via n8n.
- **Modern UI**: A sleek, dark-themed interface built with React and Tailwind CSS.

## 🛠️ Tech Stack

- **Frontend**: [React.js](https://reactjs.org/) + [Tailwind CSS](https://tailwindcss.com/) + [Vite](https://vitejs.dev/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Intelligence**: [Groq](https://groq.com/) (Llama 3.1 8B)
- **Scraping**: [Firecrawl](https://www.firecrawl.dev/)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL + pgvector)
- **Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)

## ⚙️ Installation

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_service_role_key
   HUGGINGFACEHUB_API_TOKEN=your_hf_token
   GROQ_API_KEY=your_groq_key
   FIRECRAWL_API_KEY=your_firecrawl_key
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file:
   ```env
   VITE_BACKEND_URL=http://localhost:8000
   VITE_N8N_WEBHOOK_URL=your_n8n_webhook
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

## 📖 Usage

1. **Analyse**: Paste a URL and click "Analyse". Linklyt will scrape the site, generate a summary, and store it in memory.
2. **Ask**: Ask any question about the page. The AI will use the indexed context to provide a factual answer.
3. **Automate**: Click "Automate" to send your research data to your connected Google Sheet.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by [Abhi Guru](https://github.com/AbhiGuru25)
