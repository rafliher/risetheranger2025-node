FROM python:3

RUN useradd -ms /bin/bash ctf

COPY . .

RUN mkdir -p notes
RUN chmod 744 .
RUN chmod 777 notes

USER ctf

RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "gunicorn", "--bind", "0.0.0.0", "main:app"]