# ---- Python backend image ----
FROM python:3.11-slim AS bot
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]

# ---- Frontend image ----
FROM node:20 AS web
WORKDIR /app
COPY flang-bot-web/package.json flang-bot-web/pnpm-lock.yaml ./flang-bot-web/
RUN npm install -g pnpm && cd flang-bot-web && pnpm install
COPY flang-bot-web ./flang-bot-web
WORKDIR /app/flang-bot-web
RUN pnpm run build
CMD ["pnpm", "start"]
