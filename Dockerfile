FROM python:3.9.7

ADD . app/
WORKDIR app
RUN pip install poetry==1.3.2

RUN poetry config virtualenvs.create true --local
RUN poetry config virtualenvs.in-project true --local
RUN poetry config installer.parallel false

RUN poetry install --no-dev
EXPOSE 8000
ENTRYPOINT ["poetry", "run"]
CMD ["python","run.py"]
