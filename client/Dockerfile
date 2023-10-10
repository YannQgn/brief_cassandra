FROM python:3.8
RUN mkdir /tmp/emptydir
WORKDIR /app
COPY . .
RUN pip install -r req.txt
CMD ["streamlit", "run", "app.py", "--server.port", "8501"]