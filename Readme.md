# Python Data Applications - TP



## Requisitos Previos

- Python 3.x instalado
- `venv` para entornos virtuales

## Configurar el entorno virtual

Para evitar conflictos con las dependencias de otros proyectos, es recomendable usar un entorno virtual. Aquí te explicamos cómo configurarlo:

1. **Crear el entorno virtual**

   En la raíz de tu proyecto, ejecuta el siguiente comando para crear un entorno virtual llamado `venv`:

   ```bash
   python3 -m venv venv

   source venv/bin/activate

## Instrucciones para iniciar el proyecto

1. Asegúrate de tener Docker y Docker Compose instalados en tu máquina.

2. Navega al directorio del proyecto

3. Inicializar el entorno:
   ```bash
    make init
   ```
4. Ejecuta el siguiente comando para iniciar los servicios utilizando el archivo Make:
   ```bash
    make up
   ```
5. Para detener los servicios, puedes usar:
   ```bash
    make down
   ```
6. Acceder a la interfaz web:
Una vez que Airflow esté en funcionamiento, puedes acceder a la interfaz web en http://localhost:8080 utilizando las credenciales predeterminadas (usuario: airflow, contraseña: airflow).
