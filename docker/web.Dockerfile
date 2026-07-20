FROM node:22-alpine AS builder

WORKDIR /app

# Copy root configurations
COPY package.json package-lock.json turbo.json ./

# Copy workspaces
COPY apps/web ./apps/web
COPY packages ./packages

# Install dependencies
RUN npm ci

# Build the web app
RUN npm run build --filter=web

FROM node:22-alpine AS runner
WORKDIR /app

RUN addgroup -S fairlens && adduser -S fairlens -G fairlens

RUN apk --no-cache add curl

COPY --from=builder /app/apps/web/dist ./dist

RUN npm install -g serve && chown -R fairlens:fairlens /app

USER fairlens

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

CMD ["serve", "-s", "dist", "-l", "5173"]
