FROM denoland/deno:alpine AS builder

WORKDIR /app

COPY deno.json deno.lock package.json ./

RUN deno install --allow-scripts --node-modules-dir

# Copy the rest of the application code
COPY . .

# Build the Vite application
RUN deno task build

# Production stage
FROM denoland/deno:alpine AS runner
WORKDIR /app

# Copy artifacts from builder
COPY --from=builder /app/dist ./dist

# Install 'serve' package globally or run it via npm specifier
# We'll use deno to run npm:serve
EXPOSE 3000

CMD ["run", "-A", "npm:serve", "-s", "dist", "-p", "3000"]
