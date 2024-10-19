import sys
import os
import pytest
import requests
from unittest.mock import patch
# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))  
from get_payments import get_payments  # Asegúrate de que la ruta sea correcta

# Configurar la variable de entorno para las pruebas
os.environ["API_URL"] = "http://api:3000"

def test_get_payments_success_with_payment_date(mocker):
    # Mockear la respuesta de requests.get
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"data": "test data"}]
    
    # Mockear requests.get para que devuelva el mock_response
    mocker.patch("requests.get", return_value=mock_response)

    # Llamar a la función get_payments con payment_date
    result = get_payments(payment_date="2024-10-15")
    
    # Verificar que el resultado sea el esperado
    assert result == mock_response.json.return_value
    
    # Verificar que requests.get fue llamado con la URL correcta
    requests.get.assert_called_once_with("http://api:3000/payments", params={"payment_date": "2024-10-15", "limit": 1000, "offset": 0})

def test_get_payments_success_with_date_range(mocker):
    # Mockear la respuesta de requests.get
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"data": "test data"}]
    
    # Mockear requests.get para que devuelva el mock_response
    mocker.patch("requests.get", return_value=mock_response)

    # Llamar a la función get_payments con start_payment_date y end_payment_date
    result = get_payments(start_payment_date="2024-10-15", end_payment_date="2024-10-16")
    
    # Verificar que el resultado sea el esperado
    assert result == mock_response.json.return_value
    
    # Verificar que requests.get fue llamado con la URL correcta y los parámetros
    requests.get.assert_called_once_with("http://api:3000/payments", params={"start_payment_date": "2024-10-15", "end_payment_date": "2024-10-16", "limit": 1000, "offset": 0})
    
def test_get_payments_error_both_dates(mocker):
    # Verificar que se lanza un ValueError si se proporcionan ambos tipos de fechas
    with pytest.raises(ValueError, match="Solo se puede proporcionar payment_date o start_payment_date y end_payment_date, no ambos."):
        get_payments(payment_date="2024-10-15", start_payment_date="2024-10-15")

def test_get_payments_error_missing_dates(mocker):
    # Verificar que se lanza un ValueError si faltan ambos tipos de fechas
    with pytest.raises(ValueError, match="Se debe proporcionar payment_date o ambos start_payment_date y end_payment_date."):
        get_payments()