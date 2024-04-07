FROM python:3.8-alpine
ENV PYTHONUNBUFFERED=1
RUN apk update && apk add gcc python3-dev musl-dev
WORKDIR /app
COPY app/ .
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["./start.sh"]