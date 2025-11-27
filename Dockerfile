FROM python:3.10.18
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./ /code
CMD ["bash", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4"]
