FROM node:20-alpine

WORKDIR /frontend

COPY package*.json ./
RUN npm install

COPY . .

# default is to start vite dev server
CMD ["npm", "run", "dev"]
