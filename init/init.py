import os
import time
import requests
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

TextEmbedding.add_custom_model(
    model="intfloat/multilingual-e5-small",
    pooling=PoolingType.MEAN,
    normalization=True,
    sources=ModelSource(hf="intfloat/multilingual-e5-small"),
    dim=384,
    model_file="onnx/model.onnx",
)

OLLAMA_URL = "http://ollama:11434"
QDRANT_URL = "http://qdrant:6333"
LLM_MODEL = "qwen2.5-coder:7b-instruct"
COLLECTION_NAME = "lua_examples"


def wait_for_service(url, service_name, timeout=60):
    """Ждем, пока сервис не начнет отвечать HTTP 200"""
    print(f"Ожидание запуска {service_name} по адресу {url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"[OK] {service_name} готов!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    raise Exception(f"[ERROR] Время ожидания {service_name} истекло.")


def pull_ollama_model():
    """Скачиваем модель Ollama (если её нет)"""
    print(f"Проверка модели {LLM_MODEL} в Ollama...", flush=True)
    tags_res = requests.get(f"{OLLAMA_URL}/api/tags").json()
    existing_models = [m["name"] for m in tags_res.get("models", [])]

    if LLM_MODEL in existing_models or f"{LLM_MODEL}:latest" in existing_models:
        print(f"[OK] Модель {LLM_MODEL} уже загружена.")
        return

    print(f"Скачивание модели {LLM_MODEL} (это может занять время)...", flush=True)
    # stream=False, чтобы дождаться полного скачивания
    pull_res = requests.post(f"{OLLAMA_URL}/api/pull", json={"name": LLM_MODEL})
    if pull_res.status_code == 200:
        print(f"[OK] Модель {LLM_MODEL} успешно скачана!", flush=True)
    else:
        raise Exception(f"[ERROR] Не удалось скачать модель: {pull_res.text}")


def init_qdrant_db():
    """Инициализация векторной базы и заливка примеров RAG"""
    print("Подключение к Qdrant...", flush=True)
    client = QdrantClient(url=QDRANT_URL)

    # Проверяем, существует ли коллекция
    if client.collection_exists(COLLECTION_NAME):
        print(f"[OK] Коллекция {COLLECTION_NAME} уже существует.", flush=True)
        return

    print(f"Создание коллекции {COLLECTION_NAME}...", flush=True)
    # Для intfloat/multilingual-e5-small размерность вектора = 384
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # Здесь можно добавить загрузку ваших 8 примеров из json
    examples_path = (
        "/examples/examples.json"  # Путь при маппинге volume (см. docker-compose)
    )
    if os.path.exists(examples_path):
        print("Загрузка эмбеддингов для RAG...")
        embedding_model = TextEmbedding(model_name="intfloat/multilingual-e5-small")

        with open(examples_path, "r", encoding="utf-8") as f:
            examples = json.load(f)

        points = []
        for i, ex in enumerate(examples):
            # Векторизуем запрос пользователя (по нему будем искать)
            vector = list(embedding_model.embed([ex["user_request"]]))[0]
            points.append(
                PointStruct(
                    id=i,
                    vector=vector.tolist(),
                    payload={
                        "request": ex["user_request"],
                        "code": ex["expected_code"],
                    },
                )
            )
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"[OK] Загружено {len(points)} примеров в базу знаний!", flush=True)
    else:
        print(
            f"[WARNING] Файл {examples_path} не найден. Пропуск заливки примеров.",
            flush=True,
        )


if __name__ == "__main__":
    print("=== Старт контейнера инициализации (Migrations) ===", flush=True)

    wait_for_service(OLLAMA_URL, "Ollama")
    pull_ollama_model()

    wait_for_service(QDRANT_URL, "Qdrant")
    init_qdrant_db()

    print("=== Инициализация успешно завершена! ===")
