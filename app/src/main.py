import os
import re
import tempfile
import subprocess
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

app = FastAPI(title="LocalScript API")

# Константы (в идеале часть из них перенести в .env)
OLLAMA_URL = "http://ollama:11434"
QDRANT_URL = "http://qdrant:6333"
LLM_MODEL = "qwen2.5-coder:7b-instruct"
COLLECTION_NAME = "lua_examples"
BEST_PRACTICE_PATH = "/app/prompts/LUA_BEST_PRACTICES.md"

# Глобальные переменные для загрузки в память
LUA_BEST_PRACTICE = ""
embedding_model = None
qdrant_client = None


class GenerateRequest(BaseModel):
    prompt: str


# ==========================================
# ШАГ 1. Инициализация при старте (Загрузка в ОЗУ)
# ==========================================
@app.on_event("startup")
def startup_event():
    global LUA_BEST_PRACTICE, embedding_model, qdrant_client

    print("Загрузка LUA_BEST_PRACTICE в оперативную память...")
    try:
        with open(BEST_PRACTICE_PATH, "r", encoding="utf-8") as f:
            LUA_BEST_PRACTICE = f.read()
    except FileNotFoundError:
        print(
            f"[WARNING] Файл {BEST_PRACTICE_PATH} не найден. Используются пустые правила."
        )
        LUA_BEST_PRACTICE = "Соблюдайте стандартный синтаксис Lua."

    print("Инициализация модели эмбеддингов FastEmbed...")
    TextEmbedding.add_custom_model(
        model="intfloat/multilingual-e5-small",
        pooling=PoolingType.MEAN,
        normalization=True,
        sources=ModelSource(hf="intfloat/multilingual-e5-small"),
        dim=384,
        model_file="onnx/model.onnx",
    )
    embedding_model = TextEmbedding(model_name="intfloat/multilingual-e5-small")

    print("Подключение к Qdrant...")
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
            "temperature": 0.1,  # Низкая температура для написания кода и логики
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
    system_prompt = (
        "Ты системный аналитик. Твоя задача преобразовать задачу пользователя "
        "в строгое техническое задание для программиста. "
        "Опиши 'ВХОДНЫЕ ДАННЫЕ', 'ВЫХОДНЫЕ ДАННЫЕ' и 'ТРЕБОВАНИЯ РЕАЛИЗАЦИИ'. "
        "Если запрос пользователя неоднозначен, добавь раздел 'УТОЧНЕНИЯ' и напиши вопросы."
    )
    return call_llm(system_prompt, user_prompt)


def run_rag_search(tech_spec: str, top: int = 3) -> str:
    # Генерируем вектор по ТЗ аналитика
    query_vector = list(embedding_model.embed([tech_spec]))[0].tolist()

    # Ищем в базе
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
    system_prompt = (
        "Ты senior Lua-разработчик. Твоя задача написать код по Техническому Заданию. "
        "СТРОГО соблюдай 'LUA BEST PRACTICES' и ориентируйся на переданные примеры (RAG). "
        "Верни ТОЛЬКО Lua код внутри маркдаун блока ```lua ... ``` без лишних объяснений. "
        "Если в ТЗ есть раздел 'УТОЧНЕНИЯ', добавь эти вопросы как комментарии в самом начале Lua кода."
    )
    user_prompt = (
        f"LUA BEST PRACTICES:\n{best_practices}\n\n"
        f"ПОХОЖИЕ ПРИМЕРЫ (RAG):\n{code_examples}\n\n"
        f"ТЕХНИЧЕСКОЕ ЗАДАНИЕ:\n{tech_spec}"
    )

    raw_response = call_llm(system_prompt, user_prompt)
    return extract_lua_code(raw_response)


def run_style_check(code: str) -> str | None:
    """
    Проверка синтаксиса через локальный компилятор luac.
    Возвращает текст ошибки, либо None если всё отлично.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".lua", delete=False) as tmp:
            tmp.write(code.encode("utf-8"))
            tmp_path = tmp.name

        # Вызываем проверку синтаксиса
        result = subprocess.run(
            ["luac", "-p", tmp_path], capture_output=True, text=True
        )
        os.remove(tmp_path)

        if result.returncode != 0:
            return result.stderr.strip()  # Ошибка синтаксиса
        return None  # Код валиден

    except FileNotFoundError:
        # Если luac не установлен в контейнере, пропускаем шаг
        print(
            "[WARNING] Компилятор 'luac' не найден в системе. Проверка синтаксиса пропущена."
        )
        return None


def run_fixer(
    tech_spec: str, code: str, style_error: str, code_examples: str, best_practices: str
) -> str:
    system_prompt = (
        "Ты Lua-разработчик. Предыдущая версия скрипта выдала синтаксическую ошибку. "
        "Исправь ошибку и верни ТОЛЬКО исправленный Lua код внутри ```lua ... ```."
    )
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
# ШАГ 2. Хендлер /generate (Только бизнес-логика)
# ==========================================
@app.post("/generate")
def generate_code(request: GenerateRequest):
    # 1. Анализируем запрос, получаем ТЗ
    tech_spec = run_analyst(request.prompt)

    # 2. Ищем релевантные примеры в Qdrant
    code_examples = run_rag_search(tech_spec, top=3)

    # 3. Пишем первый вариант кода
    code = run_coder(tech_spec, code_examples, LUA_BEST_PRACTICE)

    # 4. Проверяем код на синтаксические ошибки (детерминированно)
    style_error = run_style_check(code)

    # 5. Если есть ошибка синтаксиса - запускаем фиксера
    if style_error:
        print(f"[CHECKER FAILED]: Найдена ошибка. Запуск фиксера...\n{style_error}")
        code = run_fixer(tech_spec, code, style_error, code_examples, LUA_BEST_PRACTICE)

    # Экранируем переносы строк для JSON формата, как просили в PDF
    # Формат ответа: {"result": "lua{...}lua"}
    return {"result": f"lua{{{code}}}lua"}
