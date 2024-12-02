FROM node:14-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY . .

RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json && \
    npm install && \
    npm rebuild esbuild
    
EXPOSE 5173

CMD ["npm", "run", "dev"]
