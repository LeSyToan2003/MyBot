import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai.rag.retrieve.retriever import Retriever
from ai.llm.bot.bot import BotEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "fe"))

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

retriever = Retriever()
bot = BotEngine()

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    global bot, retriever
    retriever = Retriever()
    bot = BotEngine()
    return templates.TemplateResponse("index.html", {"request": request})

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    query = data.get("query", "")
    requery = query
    context = retriever.retrieve(requery)
    response = bot.chat(input=requery, context=context)

    return JSONResponse(content={"response": response})