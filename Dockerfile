FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt update && apt upgrade -y

COPY ./backend /code/backend

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
