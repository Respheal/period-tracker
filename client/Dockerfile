FROM node:24-alpine AS builder
WORKDIR /client
COPY package*.json ./
RUN npm i
COPY . .
RUN npm run build

# Production stage
FROM nginx:stable-alpine AS production
COPY --from=builder /client/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 80