# Comando para levantar los servicios
init:
	cd recomendations_etl && \
	if grep -q "^AIRFLOW_UID=" .env; then \
	  sed -i '' "s/^AIRFLOW_UID=.*/AIRFLOW_UID=$$(id -u)/" .env; \
	else \
	  (echo ""; echo "AIRFLOW_UID=$$(id -u)"; cat .env) > .env.tmp && mv .env.tmp .env; \
	fi && \
	docker network create --driver bridge local || true && \
	docker-compose up -d && \
	cd ../demo_resources/api && \
	npm run migrate:up && npm run seeds
# Comando para levantar los servicios
migrations:
	cd ../demo_resources/api && npm run migrate:up && npm run seeds

test:
	pytest ./recomendations_etl/dags/src/
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