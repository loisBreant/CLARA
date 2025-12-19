FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM caddy:latest AS runner

WORKDIR /srv/app

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /app/dist /usr/share/caddy

EXPOSE 80

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]