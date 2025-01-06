FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt update && apt upgrade -y

COPY ./backend /code/backend
EXPOSE 8000

# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD [ "sh", "-c", "uvicorn backend.main:backend --host=0.0.0.0 --port $PORT" ]
