# Build stage
FROM node:22-slim AS builder

WORKDIR /app/frontend

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . ./

# Build the application
RUN npm run build

# Runtime stage
FROM nginx:1.27-alpine

# Copy nginx template configuration
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Copy built files from builder
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Set default backend host
ARG BACKEND_HOST=backend
ENV BACKEND_HOST=${BACKEND_HOST}

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
