# Frontend Dockerfile for AML Transaction Monitoring
# Multi-stage build: Node.js build stage + nginx runtime stage

# Build stage
FROM node:22-slim AS build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy shared config (needed by api-client.ts at build time)
COPY shared_config.json /app/shared_config.json

# Copy application source
COPY frontend/ ./

# Build the application
RUN npm run build

# Runtime stage
FROM nginx:1.27-alpine

# Accept BACKEND_HOST as build arg and set as env var for nginx template
ARG BACKEND_HOST=backend
ENV BACKEND_HOST=${BACKEND_HOST}

# Copy nginx template
COPY frontend/.nginx-template.conf /etc/nginx/templates/default.conf.template

# Copy built frontend from build stage
COPY --from=build /app/frontend/dist /usr/share/nginx/html

# Expose frontend port
EXPOSE 80

# nginx starts automatically via CMD in base image and processes templates
