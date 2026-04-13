FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y lua5.4 && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from fastembed import TextEmbedding; from fastembed.common.model_description import PoolingType, ModelSource; TextEmbedding.add_custom_model(model='intfloat/multilingual-e5-small', pooling=PoolingType.MEAN, normalization=True, sources=ModelSource(hf='intfloat/multilingual-e5-small'), dim=384, model_file='onnx/model.onnx'); model = TextEmbedding(model_name='intfloat/multilingual-e5-small')"

COPY . /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
