FROM python:latest
LABEL "Author"="Justine Brun brunjustin@eisti.eu"
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U flask-cors

EXPOSE 5000

CMD [ "python3" , "app.py"]
