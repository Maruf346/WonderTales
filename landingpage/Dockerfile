# Stage 1: Build the React Application
FROM node:22-alpine AS build

WORKDIR /app

# Copy dependency definitions and install
COPY package*.json ./
RUN npm ci

# Copy application source code and build
COPY . .
RUN npm run build

# Stage 2: Serve the Built Application with Nginx
FROM nginx:stable-alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets from build stage to Nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
