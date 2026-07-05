# ── 构建阶段 ──
FROM node:20-alpine AS builder

LABEL maintainer="陈坚卓"
LABEL org.opencontainers.image.authors="陈坚卓"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="MZVTC-2023"

WORKDIR /app

COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com && npm install

COPY . .
RUN npm run build

# ── 生产阶段 ──
FROM nginx:1.25-alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
