# Domru Intercom API

### Описание / Description
[Обёртка API](https://pypi.org/project/domru-intercom-api/) для управления домофоном провайдера **Дом.ру**.
<br>[A wrapper](https://pypi.org/project/domru-intercom-api/) for the **Dom.ru** intercom system API.

## Установка / Installation
```bash
pip install domru-intercom-api
```
## Использование / Usage
```python
import asyncio

from domru_intercom_api import DomruIntercomAPI

LOGIN = 'your_login'
PASSWORD = 'your_password'
REFRESH_TOKEN = 'your_refresh_token'
OPERATOR_ID = 13

async def main():
    domru_api = DomruIntercomAPI(login=LOGIN, password=PASSWORD)
    print(domru_api.refresh_data) # save refresh data
    # OR
    domru_api = DomruIntercomAPI(refresh_token=REFRESH_TOKEN, operator_id=OPERATOR_ID)

    # Получение списка мест / Get subscriber places
    places = await domru_api.get_subscriber_places()
    place_id = places[0].place.id
    devices = await domru_api.get_devices(place_id=place_id)

    # Открытие всех доступных домофонов / Unlocking all available intercoms
    for device in devices:
        await domru_api.open_intercom(place_id=place_id, device_id=device.id)

    # Получение истории событий / Retrieving event history
    events = await domru_api.get_events(place_id, page=0, sort='ASC')
    for event in events:
        print(event.message)

    # Закрытие сессии / Closing the session
    await domru_api.close() 

asyncio.run(main())

```