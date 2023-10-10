FROM python:3.8
RUN mkdir /tmp/emptydir
WORKDIR /app
COPY . .
RUN pip install -r req.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8502"]
