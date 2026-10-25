# ============================================================
# BUILD STAGE
# ============================================================

FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY . .

# Build React application
RUN npm run build


# ============================================================
# PRODUCTION STAGE
# ============================================================

FROM nginx:alpine

# Remove default Nginx files
RUN rm -rf /usr/share/nginx/html/*

# Copy React production build
COPY --from=build /app/dist /usr/share/nginx/html

# Expose Nginx
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]