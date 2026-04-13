import os
import re
import json
import tempfile
import subprocess
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

app = FastAPI(
    title="LocalScript API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder:7b-instruct")

COLLECTION_NAME = "lua_examples"
BEST_PRACTICE_PATH = "/app/prompts/LUA_BEST_PRACTICES.md"
AGENTS_PROMPTS_PATH = "/app/prompts/agents.json"

LUA_BEST_PRACTICE = ""
SYSTEM_PROMPTS = {}
embedding_model = None
qdrant_client = None


class HealthResponse(BaseModel):
    status: str
    ollama: str
    qdrant: str


@app.get("/health", response_model=HealthResponse)
def health_check():
    ollama_status = "unavailable"
    qdrant_status = "unavailable"

    try:
        httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
        ollama_status = "available"
    except Exception:
        pass

    try:
        qdrant_client.get_collections()
        qdrant_status = "available"
    except Exception:
        pass

    status = (
        "healthy"
        if ollama_status == "available" and qdrant_status == "available"
        else "degraded"
    )

    return HealthResponse(status=status, ollama=ollama_status, qdrant=qdrant_status)


class GenerateRequest(BaseModel):
    prompt: str


# =================================
# ШАГ 1. Инициализация при старте
# =================================
@app.on_event("startup")
def startup_event():
    global LUA_BEST_PRACTICE, SYSTEM_PROMPTS, embedding_model, qdrant_client

    ascii_art = r"""
    __                     __          
   / /   ____  _________ _/ /          
  / /   / __ \/ ___/ __ `/ /           
 / /___/ /_/ / /__/ /_/ / /            
/_____/\____/\___/\__,_/_/             
   _____           _       __          
  / ___/__________(_)___  / /_         
  \__ \/ ___/ ___/ / __ \/ __/         
 ___/ / /__/ /  / / /_/ / /_           
/____/\___/_/  /_/ .___/\__/           
                /_/                    
    """
    print(ascii_art, flush=True)
    print(f"[*] Используемая LLM модель: {LLM_MODEL}", flush=True)

    print("[*] Загрузка LUA_BEST_PRACTICE в оперативную память...")
    try:
        with open(BEST_PRACTICE_PATH, "r", encoding="utf-8") as f:
            LUA_BEST_PRACTICE = f.read()
    except FileNotFoundError:
        print(
            f"[WARNING] Файл {BEST_PRACTICE_PATH} не найден. Используются пустые правила."
        )
        LUA_BEST_PRACTICE = "Соблюдайте стандартный синтаксис Lua."

    print("[*] Загрузка системных промптов...")
    try:
        with open(AGENTS_PROMPTS_PATH, "r", encoding="utf-8") as f:
            SYSTEM_PROMPTS = json.load(f)
    except FileNotFoundError:
        print(
            f"[ERROR] Файл {AGENTS_PROMPTS_PATH} не найден. Работа агентов невозможна!"
        )
        SYSTEM_PROMPTS = {"analyst": "", "coder": "", "fixer": ""}

    print("[*] Инициализация модели эмбеддингов FastEmbed...")
    TextEmbedding.add_custom_model(
        model="intfloat/multilingual-e5-small",
        pooling=PoolingType.MEAN,
        normalization=True,
        sources=ModelSource(hf="intfloat/multilingual-e5-small"),
        dim=384,
        model_file="onnx/model.onnx",
    )
    embedding_model = TextEmbedding(model_name="intfloat/multilingual-e5-small")

    print("[*] Подключение к Qdrant...")
    qdrant_client = QdrantClient(url=QDRANT_URL)


# ==========================================
# ХЕЛПЕРЫ ДЛЯ ВЗАИМОДЕЙСТВИЯ С OLLAMA И QDRANT
# ==========================================
def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Вызов локальной модели Ollama"""
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "num_ctx": 4096,
            "num_predict": 512,
            "temperature": 0.1,
        },
    }

    try:
        response = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120.0)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации LLM: {str(e)}")


def extract_lua_code(llm_output: str) -> str:
    """Извлекает код из маркдаун блока ```lua ... ```"""
    match = re.search(r"```(?:lua)?(.*?)```", llm_output, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return llm_output.strip()


# ==========================================
# ШАГ 3. Реализация функций пайплайна
# ==========================================


def run_analyst(user_prompt: str) -> str:
    system_prompt = SYSTEM_PROMPTS.get("analyst", "Ты системный аналитик.")
    return call_llm(system_prompt, user_prompt)


def run_rag_search(tech_spec: str, top: int = 3) -> str:
    query_vector = list(embedding_model.embed([tech_spec]))[0].tolist()

    search_response = qdrant_client.query_points(
        collection_name=COLLECTION_NAME, query=query_vector, limit=top
    )
    search_result = search_response.points

    if not search_result:
        return "Примеры в базе не найдены."

    examples_text = ""
    for idx, hit in enumerate(search_result, start=1):
        payload = hit.payload
        examples_text += f"--- ПРИМЕР {idx} ---\nЗапрос: {payload.get('request', '')}\nОжидаемый код:\n{payload.get('code', '')}\n\n"

    return examples_text


def run_coder(tech_spec: str, code_examples: str, best_practices: str) -> str:
    system_prompt = SYSTEM_PROMPTS.get("coder", "Ты Lua-разработчик.")
    user_prompt = (
        f"LUA BEST PRACTICES:\n{best_practices}\n\n"
        f"ПОХОЖИЕ ПРИМЕРЫ (RAG):\n{code_examples}\n\n"
        f"ТЕХНИЧЕСКОЕ ЗАДАНИЕ:\n{tech_spec}"
    )

    raw_response = call_llm(system_prompt, user_prompt)
    return extract_lua_code(raw_response)


def run_style_check(code: str) -> str | None:
    try:
        with tempfile.NamedTemporaryFile(suffix=".lua", delete=False) as tmp:
            tmp.write(code.encode("utf-8"))
            tmp_path = tmp.name

        result = subprocess.run(
            ["luac", "-p", tmp_path], capture_output=True, text=True
        )
        os.remove(tmp_path)

        if result.returncode != 0:
            return result.stderr.strip()
        return None

    except FileNotFoundError:
        print("[WARNING] Компилятор 'luac' не найден в системе. Проверка пропущена.")
        return None


def run_fixer(
    tech_spec: str, code: str, style_error: str, code_examples: str, best_practices: str
) -> str:
    system_prompt = SYSTEM_PROMPTS.get("fixer", "Ты Lua-разработчик. Почини код.")
    user_prompt = (
        f"ТЗ:\n{tech_spec}\n\n"
        f"БАЗА ЗНАНИЙ (Ограничения):\n{best_practices}\n\n"
        f"НЕРАБОЧИЙ КОД:\n{code}\n\n"
        f"ОШИБКА КОМПИЛЯТОРА:\n{style_error}\n\n"
        "ПОЧИНИ ЭТОТ КОД."
    )

    raw_response = call_llm(system_prompt, user_prompt)
    return extract_lua_code(raw_response)


# ==========================================
# ШАГ 2. Хендлер /generate
# ==========================================
@app.post("/generate")
def generate_code(request: GenerateRequest):
    print(f"\n[?] Новый запрос: {request.prompt}")

    tech_spec = run_analyst(request.prompt)
    print("[1] Аналитик: ТЗ сформировано.")

    code_examples = run_rag_search(tech_spec, top=3)
    print("[2] RAG: Примеры найдены.")

    code = run_coder(tech_spec, code_examples, LUA_BEST_PRACTICE)
    print("[3] Кодер: Первый вариант скрипта написан.")

    style_error = run_style_check(code)

    if style_error:
        print(f"[4] Чекер: Найдена синтаксическая ошибка: {style_error}")
        code = run_fixer(tech_spec, code, style_error, code_examples, LUA_BEST_PRACTICE)
        print("[5] Фиксер: Ошибка исправлена.")
    else:
        print("[4] Чекер: Ошибок нет. Код валиден.")

    return {"result": f"lua{{{code}}}lua"}


@app.get("/chat", include_in_schema=False)
def redirect_to_chat():
    """
    Редиректит пользователя с localhost:8000/chat на интерфейс Streamlit (порт 8501).
    """
    # Поскольку браузер делает запрос снаружи контейнера, мы перенаправляем
    # его на localhost:8501 (порт, который мы пробросили для Streamlit)
    return RedirectResponse(url="http://localhost:8501")
