import annoy
import json
import pandas as pd

# Ruta del archivo JSON (que contiene los datos de las empresas)
json_file_path = '../../../dataset/payments_dataset.json'

# Cargar los datos desde el archivo JSON
with open(json_file_path, 'r') as f:
    data = json.load(f)

# Crear un DataFrame a partir de los datos
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Calcular el monto promedio pagado por empresa
average_payment_by_company = df.groupby('company_id')['amount'].mean().reset_index()
average_payment_by_company.columns = ['company_id', 'average_amount']

print("Monto promedio pagado por empresa:")
print(average_payment_by_company)

# Ordenar por empresa y fecha para calcular la frecuencia de pagos
df = df.sort_values(by=['company_id', 'date'])
df['days_since_last_payment'] = df.groupby('company_id')['date'].diff().dt.days

# Calcular la frecuencia media de pagos por empresa
payment_frequency_by_company = df.groupby('company_id')['days_since_last_payment'].mean().reset_index().fillna(0)
payment_frequency_by_company.columns = ['company_id', 'average_frequency']

print("Frecuencia de pagos por empresa:")
print(payment_frequency_by_company)

# Crear la matriz de co-ocurrencias
co_occurrence_matrix = pd.crosstab(df['external_client_id'], df['company_id'])

# Calcular la co-ocurrencia entre empresas
company_co_occurrence = co_occurrence_matrix.T.dot(co_occurrence_matrix)

# Asegurarse de que la diagonal (co-ocurrencia consigo misma) sea cero
for company_id in company_co_occurrence.columns:
    company_co_occurrence.loc[company_id, company_id] = 0 

print("Matriz de co-ocurrencias:")
print(company_co_occurrence)

# Combinar la información
df_combined = pd.merge(average_payment_by_company, payment_frequency_by_company, on='company_id')
df_combined['category_id'] = df.groupby('company_id')['category_id'].first().reset_index(drop=True)
df_combined['is_top_biller'] = df.groupby('company_id')['is_top_biller'].first().reset_index(drop=True)
df_combined['co_occurrence_vector'] = company_co_occurrence.values.tolist()

# Dimensión del embedding (category_id + co_occurrence_vector + average_amount + average_frequency + is_top_biller)
vector_dimension = len(df_combined['co_occurrence_vector'][0]) + 4  # 4 es category_id + average_amount + average_frequency + is_top_biller
print(f"Dimensión del vector utilizado al crear el índice: {vector_dimension}")

# Crear el índice Annoy
index = annoy.AnnoyIndex(vector_dimension, 'angular')

# Modificar la lógica para agregar los embeddings, evitando que se sumen empresas de la misma categoría
for _, row in df_combined.iterrows():
    # Verificar si ya hay otras empresas de la misma categoría
    embedding = [
        row['category_id'], 
        *row['co_occurrence_vector'], 
        row['average_amount'], 
        row['average_frequency'], 
        int(row['is_top_biller'])
    ]
    
    # Aquí puedes aplicar una lógica para evitar que se recomienden empresas de la misma categoría
    # Puedes modificar el embedding o aplicar un filtro aquí si ya tienes una empresa de la misma categoría
    
    index.add_item(row['company_id'], embedding)

# Construir el índice con 10 árboles
index.build(10)

# Guardar el índice localmente
index_file_path = './payments_index_with_embeddings.ann'
index.save(index_file_path)

print(f"Índice guardado en: {index_file_path}")