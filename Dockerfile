FROM python:3.12.1

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]