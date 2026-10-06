FROM node:20-alpine AS build

WORKDIR /app

# Copia pacotes e instala usando cache otimizado
COPY package*.json ./
RUN npm ci

COPY . .

# Aceita a URL da API como argumento no build para poder substituir no ambiente de prod (opcional mas boa prática)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Usando imagem Nginx oficial que roda sem root (segurança K8s)
FROM nginxinc/nginx-unprivileged:alpine

COPY --from=build /app/dist /usr/share/nginx/html

USER root
# Substitui o conf default do Nginx para lidar com rotas SPA e escutar na porta 8080 (não-root)
RUN echo 'server { \
    listen 8080; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Volta para o usuário nginx não-privilegiado
USER nginx

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
