FROM denoland/deno:alpine AS builder

WORKDIR /app

COPY deno.json deno.lock package.json ./
RUN deno install --allow-scripts --node-modules-dir

COPY . .
RUN deno task build

FROM caddy:latest AS runner

WORKDIR /srv/app

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /app/dist /usr/share/caddy

EXPOSE 80

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
