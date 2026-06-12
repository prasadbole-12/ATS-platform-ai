FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# host:true is critical - without it Vite won't accept connections from outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
