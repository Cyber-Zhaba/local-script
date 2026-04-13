FROM python:3.12-slim

WORKDIR /init

COPY ./requirements.txt /init
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='intfloat/multilingual-e5-small')"

COPY ./init.py /init/init.py

CMD ["python", "init.py"]
