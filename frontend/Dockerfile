FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
# Since we have peer dependency issues, we can force install or legacy
RUN npm ci --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
