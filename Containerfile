FROM python:3.14-alpine

RUN apk add --no-cache nodejs npm

RUN pip install fastmcp

RUN npm install -g agent-browser

WORKDIR /var/lib/agent-browser-mcp

COPY main.py main.py

EXPOSE 8000

ENTRYPOINT python main.py
