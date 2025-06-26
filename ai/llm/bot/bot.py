import os
import json
from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage
from ..prompt import bot_template
from dotenv import load_dotenv

load_dotenv()

class BotEngine:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        self.history_file = os.path.join(self.root_dir, "data", "qa_rag", "logs", "chat_history.json")

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

        self.llm = ChatOllama(model="llama3.2:3b", temperature=0.1)

        self.prompt = PromptTemplate.from_template(bot_template.template)

        self.chain: Runnable = self.prompt | self.llm

        self.session_histories = {}

        self.runnable = RunnableWithMessageHistory(
            self.chain,
            self.get_memory,
            input_messages_key="input",
            history_messages_key="history"
        )

    def get_memory(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self.session_histories:
            self.session_histories[session_id] = ChatMessageHistory()

        return self.session_histories[session_id]

    def save_chat_history(self, input: str, response: str):
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)

        history.append({
            "user": input,
            "bot": response
        })

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_chat_history(self) -> list[dict[str, str]]:
        with open(self.history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def chat(self, input: str, context: str) -> str:
        response = self.runnable.invoke(
            {
                "input": input,
                "context": context
            },
            config={"configurable": {"session_id": "alpha-session"}}
        )

        output = response.content if isinstance(response, AIMessage) else response

        self.save_chat_history(input, output)

        return output