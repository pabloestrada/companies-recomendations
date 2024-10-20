# Usa una imagen base de Python 3.12
FROM python:3.12-slim

# Instala g++, PostgreSQL dev libraries y otras herramientas necesarias para compilar paquetes
RUN apt-get update && apt-get install -y build-essential g++ libpq-dev && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /usr/src/app

# Copia los archivos de dependencias para instalar antes de copiar el resto
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Expone el puerto en el que correrá la aplicación (ajustar si tu app usa otro puerto)
EXPOSE 5001

# Establece las variables de entorno necesarias (ajústalas según tu app)
ENV FLASK_ENV=development

# Comando para ejecutar la aplicación (ajusta según el framework de tu app)
CMD ["python", "index.py"]