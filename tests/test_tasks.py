import uuid
import requests
from unittest.mock import patch
from django.conf import settings
from lamb.exc import ServerError

from api.models import ExchangeRatesRecord
from api.tasks import store_exchanges_rates_task


def test_store_exchanges_rates_task_success():
    actor_id = uuid.uuid4()
    response_json = {
        "rates": {
            "USD": 1.2345
        }
    }
    with patch("requests.get") as mock_get, patch("lamb.db.context.lamb_db_context") as mock_db_context:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = response_json

        store_exchanges_rates_task(actor_id)

        mock_get.assert_called_once_with(settings.APP_EXCHANGE_RATES_API_URL)
        mock_db_context().__enter__().add.assert_called_once()
        mock_db_context().__enter__().commit.assert_called_once()

        recorded_instance = mock_db_context().__enter__().add.call_args[0][0]
        assert isinstance(recorded_instance, ExchangeRatesRecord)
        assert recorded_instance.actor_id == actor_id
        assert recorded_instance.rate == response_json["rates"]["USD"]


def test_store_exchanges_rates_task_error():
    actor_id = uuid.uuid4()
    with patch("requests.get") as mock_get, patch("lamb.db.context.lamb_db_context") as mock_db_context:
        mock_get.return_value.status_code = 500

        try:
            store_exchanges_rates_task(actor_id)
        except Exception as e:
            assert isinstance(e, ServerError)

        mock_get.assert_called_once_with(settings.APP_EXCHANGE_RATES_API_URL)
        mock_db_context().__enter__().add.assert_not_called()
        mock_db_context().__enter__().commit.assert_not_called()
