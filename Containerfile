FROM python:3.14-alpine

WORKDIR /var/lib/agent-browser-mcp

COPY main.py main.py

RUN apk add --no-cache nodejs npm

RUN pip install fastmcp

RUN npm install -g agent-browser

EXPOSE 8000

ENTRYPOINT python main.py
