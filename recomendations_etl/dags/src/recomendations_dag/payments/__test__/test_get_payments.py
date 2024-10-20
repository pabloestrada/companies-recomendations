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
    result = get_payments(updated_date_to_find="2024-10-15")
    
    # Verificar que el resultado sea el esperado
    assert result == mock_response.json.return_value
    
    # Verificar que requests.get fue llamado con la URL correcta
    requests.get.assert_called_once_with("http://api:3000/payments", params={"updated_at": "2024-10-15", "limit": 1000, "offset": 0})

def test_get_payments_error_missing_dates(mocker):
    # Verificar que se lanza un ValueError si faltan ambos tipos de fechas
    with pytest.raises(ValueError, match="Se debe proporcionar updated_date_to_find."):
        get_payments()