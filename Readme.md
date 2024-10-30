# Python Data Applications - TP

Se realizo un MVP que la función principal es procesar y analizar los datos de pagos realizados por los clientes a diferentes empresas con el objetivo de generar recomendaciones personalizadas basadas en el comportamiento pasado de los clientes.

Funcionalidades a alto nivel:

1.	Carga y análisis de pagos:  
Carga un conjunto de datos que incluye información sobre pagos de clientes a empresas y calcula métricas clave como el monto promedio por empresa y la frecuencia de pagos por cada cliente.

2.	Creación de una matriz de co-ocurrencias:  
Genera una matriz que muestra las empresas que son “similares” en función de los clientes que han realizado pagos a ambas, lo que ayuda a identificar patrones de comportamiento entre las empresas.

3.	Construcción de un vector de características:  
Combina las métricas calculadas y las co-ocurrencias en un vector de características que luego es utilizado para construir un modelo que puede hacer recomendaciones de empresas a los clientes, basándose en su historial de pagos.
   

## Instrucciones para iniciar el proyecto

1. Asegúrate de tener Docker y Docker Compose instalados en tu máquina.

2. Navega al directorio del proyecto

3. Crear el archivo .env en la carpeta: recomendations_etl

4. Inicializar el entorno:
   ```bash
    make init
   ```
5. Acceder a la interfaz web:
Una vez que Airflow esté en funcionamiento, puedes acceder a la interfaz web en http://localhost:8080 utilizando las credenciales predeterminadas (usuario: airflow, contraseña: airflow).

6. Ejecutar el DAG Companies

7. Ejecutar el DAG Recomendations.  


## Detalle del DAG Recomendations

Este DAG de Airflow está diseñado para gestionar un flujo de trabajo relacionado con el procesamiento de pagos. A continuación se detallan sus principales funciones:

1. **Verificación del Bucket**: Comienza verificando la existencia de un bucket en la nube donde se almacenan los pagos.

2. **Verificación de Empresas**: Asegura que las empresas relevantes existan en el sistema.

3. **Obtención de la Última Actualización de Pagos**: Recupera la fecha de la última actualización de pagos.

4. **Guardar Pagos en el Bucket**: Guarda los pagos en el bucket, utilizando la fecha de actualización obtenida previamente.

5. **Actualizar la Última Fecha de Pagos**: Actualiza la fecha de la última actualización de pagos en el sistema.

6. **Guardar Pagos en la Base de Datos**: Guarda los archivos de pagos en la base de datos, utilizando la información obtenida del paso anterior. La tabla de pagos es una tabla de hechos (fact table), que almacena los eventos transaccionales que ocurren en el sistema, como pagos realizados, montos y fechas. También se maneja como una tabla SCD (Slowly Changing Dimension). 

7. **Crear Índice de Pagos**: Genera un índice de los pagos desde una fecha específica.

8. **Validar el Índice de Pagos**: Valida el índice de pagos creado, asegurándose de que sea correcto y esté en el formato adecuado.

## Detalle del DAG Companies

El DAG companies en Airflow es una secuencia de tareas que se ejecutan semanalmente para procesar y actualizar información relacionada con empresas. Está diseñado para automatizar dos pasos principales: guardar información de empresas en una base de datos y actualizar la última fecha de actualización de datos.
  
	1.	save_companies_to_db_task:
	•	Esta tarea ejecuta la función save_companies_to_db, que obtiene datos de una API y los guarda en una base de datos local. La tabla de empresas (companies_l0) sería una tabla de tipo dimensión, ya que contiene información descriptiva sobre las empresas, como su nombre, código y otras características relevantes para el contexto de los pagos o transacciones.
	•	Se encarga de la ingestión y almacenamiento de información actualizada de empresas.
	2.	update_last_companies_update_task:
	•	Esta tarea ejecuta la función update_last_companies_update, que actualiza un registro en la base de datos para mantener control de la última fecha de actualización de empresas.
	•	Esto es útil para mantener un seguimiento de cuándo fue la última vez que se actualizaron los datos.
  

# Concideraciones


## API de Pagos y Empresas
Creé una pequeña API en Node.js debido a que los datos utilizados para el proyecto no están disponibles de forma pública. Esta API permite cargar los datos en una base de datos PostgreSQL local. La base de datos se utiliza para almacenar y gestionar la información necesaria para realizar las operaciones del proyecto, asegurando así un entorno controlado para el procesamiento de los datos. 

La API tiene dos endpoints principales:

1.	Endpoint /payments: Este endpoint permite recuperar los registros de pagos desde la base de datos. Requiere el parámetro updated_at para filtrar los pagos que fueron actualizados después de esa fecha. Además, se pueden utilizar los parámetros opcionales limit y offset para paginar los resultados. Los datos se obtienen de la tabla payments, y el resultado final es una lista de pagos ordenados por id.  

2.	Endpoint /companies: Este endpoint permite recuperar los registros de compañías desde la base de datos. Similar al endpoint de pagos, también soporta paginación mediante los parámetros limit y offset. Los datos se obtienen de la tabla companies y también se ordenan por id.


## API de Entrenamiento y Testeo

Desarrollé una API en Python para entrenar el modelo de recomendaciones utilizando la librería Annoy. La razón principal de crear esta API fue que integrar Annoy directamente dentro de Airflow resultó ser más complejo de lo esperado debido a las limitaciones de compatibilidad y la necesidad de manejar archivos de gran tamaño y estructuras complejas, como los índices Annoy, que no se pueden gestionar fácilmente dentro del flujo de tareas típico de Airflow.

Al implementar la API en un entorno separado, puedo gestionar de manera eficiente el proceso de entrenamiento del modelo, generar y guardar los índices en S3, y luego utilizar esos índices para realizar consultas rápidas de recomendaciones sin comprometer el flujo de Airflow. De esta forma, delego la tarea intensiva de cálculos en la API mientras mantengo la arquitectura de Airflow enfocada en la orquestación y el control de los procesos de ETL.

La API tiene dos principales endpoints:

1. /create_index (POST)

Este endpoint se utiliza para procesar un archivo de datos y crear un índice utilizando Annoy. El proceso sigue estos pasos:

	•	Recibe una solicitud POST con el nombre del archivo que contiene los datos y el bucket de S3 donde se almacenan.
	•	Carga los datos desde S3 y crea un índice Annoy basado en la información de pagos y empresas, generando embeddings para representar a cada empresa.
	•	El índice se guarda en un archivo temporal y luego se sube a S3 para su uso futuro.

Ejemplo de uso:
Este endpoint es útil cuando se necesita actualizar o generar un nuevo índice de recomendaciones basado en los últimos datos de pagos.

2. /recommend_companies (POST)

Este endpoint permite obtener recomendaciones de empresas para un cliente basado en sus pagos anteriores. Funciona de la siguiente manera:

	•	Recibe el client_id del cliente, el número de recomendaciones deseadas, y las ubicaciones del índice y los datos en S3.
	•	Carga el índice de Annoy desde S3 y los datos del cliente desde la base de datos PostgreSQL.
	•	Utiliza el índice para buscar empresas similares a aquellas con las que el cliente ha interactuado (pagado) y genera una lista de recomendaciones.
	•	Retorna una lista con los detalles de las empresas recomendadas, como su nombre y código.

Ejemplo de uso:
Este endpoint es útil para ofrecer recomendaciones personalizadas basadas en el historial de pagos del cliente, mejorando la experiencia de usuario al mostrarle empresas relacionadas.


## Creacion de tabla SCD - Funcion insert_payments
El propósito de esta función es implementar una tabla de Slowly Changing Dimension (SCD) tipo 2 para manejar los pagos. El proceso que sigue la función se puede dividir en dos pasos principales:

1. Verificación de Cambios (SCD - Slowly Changing Dimension)

	•	Se verifica cada pago en la tabla payments_l0 usando el payment_id y el company_code.
	•	Si el pago ya existe y está marcado como is_current (TRUE), se compara cada campo relevante (payment_at, status, amount, external_client_id) del pago actual con el nuevo registro.
	•	Si se detecta algún cambio en los datos (diferencias en las fechas, montos, estado, o external_client_id), se ejecuta una actualización en la tabla:
	•	Se marca el registro anterior como no actual (FALSE) y se establece una fecha de fin (end_date) para indicar cuándo dejó de estar vigente.

2. Inserción de Nuevos Registros o Actualizaciones

	•	Si es un nuevo registro o si el registro existente fue marcado como no actual, se inserta una nueva versión del pago con la nueva información.
	•	El nuevo registro se marca como actual (is_current TRUE), y los campos start_date y end_date se actualizan para reflejar el periodo en el que es válido.

Para este proyecto, se decidió utilizar PostgreSQL como base de datos en lugar de Amazon Redshift debido a que no se dispone de un clúster de Redshift en el entorno donde va a ejecutarse el proceso. PostgreSQL fue elegida como una alternativa viable y de código abierto que cumple con las necesidades del sistema para almacenar y gestionar los datos. Además, su implementación es sencilla dentro de un entorno de desarrollo local.

La base de datos de PostgreSQL se despliega utilizando Docker Compose, lo que facilita la creación y configuración de la base de datos en contenedores de forma rápida y eficiente. Esto permite una infraestructura local replicable, eliminando la necesidad de gestionar manualmente la instalación de la base de datos y ofreciendo un entorno limpio y aislado para la ejecución del proceso

## Manejo de archivos con S3
Para manejar eficientemente el volumen de datos entre los pasos de los DAGs, se utilizó Amazon S3 como sistema de almacenamiento. Al tratarse de grandes volúmenes de datos que se generan y procesan, S3 permite almacenar los datos de forma escalable y accesible entre distintos procesos. Los datos obtenidos desde la API se almacenan en formato Parquet, lo que facilita su almacenamiento y consulta debido a que es un formato optimizado para el análisis y manipulación de datos. Este formato reduce el tamaño de los archivos y mejora la velocidad de lectura.

Además, en el entorno de desarrollo, S3 fue implementado localmente utilizando Localstack con Docker Compose, simulando un entorno S3 real sin necesidad de depender directamente de los servicios en la nube, permitiendo así pruebas y desarrollos más rápidos. De esta manera, cada paso del flujo de trabajo en el DAG puede leer o escribir directamente en los archivos almacenados en S3, asegurando una integración fluida entre etapas.

## Datos para entrenamiento del modelo de prediccion
Para obtener los datos de pago necesarios para entrenar el modelo, se utilizó una consulta directa a la base de datos en lugar de replicar los datos que ya están almacenados en la misma. Esto asegura que siempre se obtienen los datos más actualizados, evitando redundancias y duplicación de almacenamiento, lo que optimiza el uso de recursos.

La función get_payments_for_recomendations permite extraer los pagos desde la tabla de pagos existente en la base de datos, filtrando por la fecha de creación (created_at) y solo seleccionando los pagos que están activos (is_current = true). La consulta se puede limitar opcionalmente en cantidad de registros con un parámetro limit, lo que permite controlar el volumen de datos que se devuelve para procesos de entrenamiento o análisis.

Este enfoque evita tener que almacenar los mismos datos en distintos formatos o ubicaciones, aprovechando directamente la estructura de la base de datos y asegurando la consistencia de los datos a lo largo del proceso de entrenamiento.

## Manejo de actualizacion de datos
La función get_last_payments_update se utiliza para determinar la fecha desde la cual se deben buscar actualizaciones en los pagos y controlar las fechas de procesamiento. Su objetivo principal es obtener las actualizaciones de pagos a partir de una fecha determinada y asegurarse de no procesar pagos futuros ni duplicar actualizaciones pasadas.

Explicación de su funcionalidad:

	1.	Calculo de fechas:
	•	La función calcula la fecha actual (new_last_date_update) y también establece una fecha límite de búsqueda, que por defecto es 30 días atrás (updated_date_to_find). Esta fecha límite es la fecha mínima desde la cual se buscarán pagos actualizados.
	2.	Última actualización registrada:
	•	Se llama a una función auxiliar (get_last_update) para obtener la última fecha de actualización registrada para los pagos, almacenada en alguna tabla o servicio de control de actualizaciones.
	3.	Verificación de la última actualización:
	•	Si se encuentra un valor para last_date_update, la función compara esta fecha con la fecha actual:
	•	Fechas futuras: Si la última actualización es mayor a la fecha actual, la función lanza un error para evitar procesar pagos con fechas futuras.
	•	Fechas anteriores: Si la última actualización es anterior a la fecha actual, la función establece el nuevo límite de búsqueda un día después de la última actualización, para no repetir pagos ya procesados.
	4.	Devolución:
	•	Finalmente, devuelve dos valores clave:
	•	updated_date_to_find: La fecha a partir de la cual se buscarán pagos actualizados.
	•	proccess_date: La fecha de procesamiento actual, que puede usarse para actualizar registros o seguir el flujo de actualización.

Este enfoque asegura que las actualizaciones de los pagos se manejan de manera eficiente y sin procesar datos duplicados o futuros.