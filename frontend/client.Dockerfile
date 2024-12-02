FROM node:14-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm cache clean --force && \
    rm -rf node_modules && \
    npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
