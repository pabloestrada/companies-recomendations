import pytest
import requests
from requests.exceptions import HTTPError
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
    result = api_call("payments", {"updated_at": "2024-10-15"})
    
    # Verificar que el resultado sea el esperado
    assert result == mock_response.json.return_value

def test_api_call_failure(mocker):
    # Mock the requests.get response to simulate an error
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError("404 Error")

    # Patch requests.get to return the mocked response
    mocker.patch("requests.get", return_value=mock_response)

    # Expect an HTTPError to be raised when calling the function
    with pytest.raises(HTTPError, match="404 Error"):
        api_call("payments", {"updated_at": "2024-10-15"})