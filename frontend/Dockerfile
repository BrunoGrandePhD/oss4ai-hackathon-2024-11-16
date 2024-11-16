FROM node:16-alpine

# Make it easier to debug, enabling /bin/bash
RUN apk update && apk add bash

WORKDIR /app

COPY package.json ./
COPY yarn.lock ./
RUN yarn install --registry https://registry.npmjs.org

COPY . .

EXPOSE 3000

CMD ["yarn", "start"]