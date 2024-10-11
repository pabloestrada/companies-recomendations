# Comando para levantar los servicios
init:
	echo -e "AIRFLOW_UID=$(id -u)" > .env
	docker network create --driver bridge local || true
	docker-compose up airflow-init

# Comando para levantar los servicios
up:
	docker-compose up -d

# Comando para detener los servicios
down:
	docker-compose down

# Comando para reiniciar los servicios
restart:
	docker-compose restart

# Comando para ver los logs
logs:
	docker-compose logs -f


# Comando para limpiar imágenes y contenedores
clean:
	docker-compose down --rmi all --volumes --remove-orphans