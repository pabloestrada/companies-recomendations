# Usa una imagen base de Node.js
FROM node:20

# Instala netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /usr/src/app

# Copia el archivo de configuración de dependencias
COPY package*.json ./

# Instala las dependencias
RUN npm install

# Copia el resto de la aplicación
COPY . .

# Expone el puerto que usa la aplicación
EXPOSE 3000

# Establece la variable de entorno NODE_ENV
ENV NODE_ENV=development


# Comando para ejecutar la migración y las semillas antes de iniciar la aplicación
CMD ["sh", "-c", "until nc -z postgres 5432; do echo 'Esperando a que la base de datos esté disponible...'; sleep 5; done && npm run migrate:up && npm run seeds && node index.mjs"]