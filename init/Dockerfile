FROM python:3.12-slim

WORKDIR /init

COPY ./requirements.txt /init
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from fastembed import TextEmbedding; from fastembed.common.model_description import PoolingType, ModelSource; TextEmbedding.add_custom_model(model='intfloat/multilingual-e5-small', pooling=PoolingType.MEAN, normalization=True, sources=ModelSource(hf='intfloat/multilingual-e5-small'), dim=384, model_file='onnx/model.onnx'); model = TextEmbedding(model_name='intfloat/multilingual-e5-small')"

COPY ./init.py /init/init.py

CMD ["python", "init.py"]
