import numpy as np
import pandas as pd
import annoy
import json
# Cargar el dataset
json_file_path = '../../../dataset/payments_dataset.json'
with open(json_file_path, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Definir el tamaño del vector (el mismo que usaste al crear el índice)
vector_dimension = 1350  # Asegúrate de usar el mismo valor que usaste para el índice

# Crear el índice Annoy con la misma métrica
index = annoy.AnnoyIndex(vector_dimension, 'angular')

# Cargar el índice guardado
index_file_path = './payments_index_with_embeddings.ann'
index.load(index_file_path)

def recomendar_empresas_para_cliente(client_id, num_recommendations=5):
    # Obtener las empresas que ha pagado el cliente
    empresas_cliente = df[df['external_client_id'] == client_id]['company_id'].unique()
    
    if len(empresas_cliente) == 0:
        print(f"El cliente con ID {client_id} no ha realizado pagos.")
        return []
    
    # Obtener las categorías de las empresas que el cliente ya ha pagado
    categorias_cliente = df[df['company_id'].isin(empresas_cliente)]['category_id'].unique()
    
    # Obtener los embeddings de esas empresas desde el índice
    embeddings = []
    for company_id in empresas_cliente:
        try:
            embedding = np.array(index.get_item_vector(company_id))
            embeddings.append(embedding)
        except KeyError:
            print(f"Empresa con ID {company_id} no encontrada en el índice.")
    
    if len(embeddings) == 0:
        print(f"No se encontraron empresas en el índice para el cliente {client_id}.")
        return []
    
    # Calcular el embedding promedio del cliente basado en las empresas que pagó
    embedding_cliente = np.mean(embeddings, axis=0)
    
    # Buscar las empresas más cercanas al embedding del cliente
    recommended_companies = index.get_nns_by_vector(embedding_cliente, num_recommendations * 3)  # Buscar más para filtrar
    
    # Filtrar las recomendaciones para excluir empresas de las mismas categorías
    empresas_recomendadas_filtradas = []
    for company_id in recommended_companies:
        categoria_empresa = df[df['company_id'] == company_id]['category_id'].values[0]
        
        # Solo añadir empresas si son de una categoría distinta a las que ya pagó el cliente
        if categoria_empresa not in categorias_cliente:
            empresas_recomendadas_filtradas.append(company_id)
        
        # Terminar cuando se alcanza el número de recomendaciones deseado (sin contar las ya pagadas)
        if len(empresas_recomendadas_filtradas) >= num_recommendations:
            break
    
    # Convertir los IDs a enteros estándar de Python (int)
    empresas_cliente = [int(emp) for emp in empresas_cliente]
    empresas_recomendadas_filtradas = [int(emp) for emp in empresas_recomendadas_filtradas]
    
    # Combinar las empresas que ya pagó el cliente con las nuevas recomendaciones
    empresas_finales = empresas_cliente + empresas_recomendadas_filtradas
    
    return empresas_finales

# Ejemplo de uso: Recomendar empresas para un cliente con su ID
cliente_id = 'wD96rTtxvgcXvTFhIYaX8jie'  # Cambia esto por el ID del cliente que quieras probar
empresas_recomendadas = recomendar_empresas_para_cliente(cliente_id, num_recommendations=5)

print(f"Empresas recomendadas para el cliente {cliente_id}: {empresas_recomendadas}")
