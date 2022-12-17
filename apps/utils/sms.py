import asyncio
import httpx
from celery import shared_task
from root import settings as st

async def auth_login():
    payload = {
        'email': st.ESKIZ_EMAIL,
        'password': st.ESKIZ_SECRET_KEY
    }

    response = httpx.post(st.ESKIZ_AUTH_URL, data=payload)
    if response.status_code == 200:
        return response.json()['data']['token']

    await asyncio.sleep(5)
    st.ESKIZ_TOKEN = await auth_login()


@shared_task
async def send_sms(phone: str):
    headers = {
        'Authorization': f'Bearer {st.ESKIZ_TOKEN}'
    }

    payload = {
        'mobile_phone': phone,
        'message': 'Salom dasturchilar'
    }

    response = httpx.post(st.ESKIZ_SEND_URL, headers=headers, data=payload)
    if response.status_code == 200:
        status_id = response.json()['id']
        print(status_id)
        print(response.status_code)
    else:
        await auth_login()
        print('Xatolik')
