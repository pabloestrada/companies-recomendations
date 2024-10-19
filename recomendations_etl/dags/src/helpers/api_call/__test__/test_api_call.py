import pytest
import requests
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))  
from api_call import api_call  # Asegúrate de que la ruta sea correcta

def test_api_call_success(mocker):
    # Mockear la respuesta de requests.get
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test data"}
    
    mocker.patch("requests.get", return_value=mock_response)

    # Llamar a la función con un path y parámetros
    result = api_call("payments", {"start_payment_date": "2024-10-15", "end_payment_date": "2024-10-16"})
    
    # Verificar que el resultado sea el esperado
    assert result == mock_response.json.return_value

def test_api_call_failure(mocker):
    # Mockear la respuesta de requests.get para un error
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    
    mocker.patch("requests.get", return_value=mock_response)

    # Llamar a la función con un path y parámetros
    result = api_call("payments", {"start_payment_date": "2024-10-15", "end_payment_date": "2024-10-16"})
    
    # Verificar que el resultado sea None en caso de error
    assert result is None