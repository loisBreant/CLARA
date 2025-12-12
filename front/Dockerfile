FROM denoland/deno:alpine AS builder

WORKDIR /app

# Copy configuration files
COPY deno.json deno.lock package.json ./

# Install dependencies using Deno
# We need --node-modules-dir for Next.js compatibility
RUN deno install --allow-scripts --node-modules-dir

# Copy the rest of the application code
COPY . .

# Build the Next.js application using Deno task
RUN deno task build

# Production stage
FROM denoland/deno:alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy configuration
COPY --from=builder /app/deno.json ./deno.json
COPY --from=builder /app/package.json ./package.json

# Copy artifacts from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["task", "start"]
