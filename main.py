import asyncio
import requests 
import os
import json
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

import database.requests as rq
from database.models import async_main

load_dotenv()
TOKEN = os.getenv('TOKEN')
headers = json.loads(os.getenv('headers'))
last_nft = {}
collection = 'https://getgems.io/collection/EQBYoRP18Gr8SKUHaFDYg3pQq0i-lzkrt_OCd-yy429_tL1j'

bot = Bot(token=TOKEN)
dp = Dispatcher()


all_nfts_on_sale = []
response = requests.get(url='https://api.getgems.io/public-api/v1/nfts/on-sale/EQBYoRP18Gr8SKUHaFDYg3pQq0i-lzkrt_OCd-yy429_tL1j', headers=headers)
for i in range(len(response.json()['response']['items'])):
    name_ = response.json()['response']['items'][i]['name']
    image_ = response.json()['response']['items'][i]['image']
    price_ = response.json()['response']['items'][i]['sale']['fullPrice'][:-9]
    description_ = response.json()['response']['items'][i]['description']
    url_ = collection + response.json()['response']['items'][i]['address']
                
    all_nfts_on_sale.append({'name': name_, 'description': description_, 'image': image_, 'price': price_, 'description': description_, 'url': url_})

def get_nft_info():
    global last_nft
    global all_nfts_on_sale
    response = requests.get(url='https://api.getgems.io/public-api/v1/collection/history/EQBYoRP18Gr8SKUHaFDYg3pQq0i-lzkrt_OCd-yy429_tL1j', headers=headers)
    
    if not (response.json()['response']['items'][0]['name'] == last_nft.get('name', '') and
        response.json()['response']['items'][0]['typeData']['type'] == last_nft.get('type', '')):
        if response.json()['response']['items'][0]['typeData']['type'] == 'putUpForSale':
            nft = requests.get(url='https://api.getgems.io/public-api/v1/nfts/on-sale/EQBYoRP18Gr8SKUHaFDYg3pQq0i-lzkrt_OCd-yy429_tL1j', headers=headers)
            name = nft.json()['response']['items'][0]['name']
            image = nft.json()['response']['items'][0]['image']
            price = nft.json()['response']['items'][0]['sale']['fullPrice'][:-9]
            description = nft.json()['response']['items'][0]['description']
            url = collection + nft.json()['response']['items'][0]['address']
            
            result = []
            for i in range(len(nft.json()['response']['items'])):
                name_ = nft.json()['response']['items'][i]['name']
                image_ = nft.json()['response']['items'][i]['image']
                price_ = nft.json()['response']['items'][i]['sale']['fullPrice'][:-9]
                description_ = nft.json()['response']['items'][i]['description']
                url_ = collection + nft.json()['response']['items'][i]['address']
                
                result.append({'name': name_, 'description': description_, 'image': image_, 'price': price_, 'description': description_, 'url': url_})
            all_nfts_on_sale = result[:]
            
            last_nft = {'name': name, 'type': 'putUpForSale'}
            
            return {'name': name, 'description': description, 'type': 'putUpForSale', 'image': image, 'price': price, 'url': url}
                
        elif response.json()['response']['items'][0]['typeData']['type'] == 'sold':
            nft = requests.get(url=f'https://api.getgems.io/public-api/v1/nft/{response.json()['response']['items'][0]['address']}', headers=headers)
            name = nft.json()['response']['name']
            image = nft.json()['response']['image']
            url = collection + nft.json()['response']['address']
            
            last_nft = {'name': name, 'type': 'sold'}
            
            all_nfts_on_sale = [el for el in all_nfts_on_sale if el['name'] != name]
            
            return {'name': name, 'image': image, 'type': 'sold', 'url': url}
    else:
        return
    
 
async def parse_nfts():
    while True:
        result = get_nft_info()
        if result:
            users = await rq.get_users()
            if result['type'] == 'sold':
                for user in users:
                    await bot.send_photo(user.tg_id, result['image'], caption=f'<b><a href="{result['url']}">{result['name']}</a> продан!</b>\n\n<tg-spoiler>Шанс был у каждого😉</tg-spoiler>', parse_mode='html')
            
            if result['type'] == 'putUpForSale':
                for user in users:
                    await bot.send_photo(user.tg_id, result['image'], caption=f'<b><a href="{result['url']}">{result['name']}</a> вышел на продажу!</b>\n\n{result['description']}\n\nЦена: {result['price']} $TON', parse_mode='html')
        await asyncio.sleep(10)
            

async def main():
    await async_main()
    asyncio.create_task(parse_nfts())
    await dp.start_polling(bot)
     
     
@dp.message(Command('start')) 
async def start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer_photo('https://i.getgems.io/Es705fxShpjdEl2u_nte2bYszGB8PQ0enkCVUN0mDuY/rs:fill:1000:0:1/g:ce/czM6Ly9nZXRnZW1zLW5mdC9uZnQvYy82ODU5Mzc2OGVjMjA0MWI3MjVmZDVkODgvMTAwMDAwMC9pbWFnZS5wbmc', 
                               caption='Добро пожаловать в бота! Он предназначен для того, чтобы уведомлять о новых NFT SunSpace, которые вышли на продажу.\n\nЧтобы посмотреть список всех NFT, находящихся на продаже, просто напиши /on_sale\n\nПредупреждён - значит вооружен😉')
       
       
@dp.message(F.text.startswith('/set_nfts_amount'))
async def set_nfts_amount(message: Message):
    global on_sale_amount
    if message.from_user.id == 5038345053:
        try:
            on_sale_amount = message.text.split()[1]
            await message.answer('Количество NFT на продаже успешно изменено! ✅')
        except Exception:
            await message.answer('Произошла ошибка! ❌')
       

@dp.message(Command('on_sale'))
async def on_sale(message: Message):
    global all_nfts_on_sale
    if not all_nfts_on_sale:
        await message.answer_photo('https://i.getgems.io/tyiwg_5PWT5WtOyM8jfApna4-9rCz9SJNkHNlMoVD9o/rs:fill:1000:0:1/g:ce/czM6Ly9nZXRnZW1zLW5mdC9uZnQvYy82ODU5Mzc2OGVjMjA0MWI3MjVmZDVkODgvMzkvaW1hZ2UucG5n', 
                                   caption='На данный момент NFT в продаже нет 😕')
        return
    for nft in all_nfts_on_sale:
        await message.answer_photo(nft['image'], caption=f'<b><a href="{nft['url']}">{nft['name']}</a></b>\n\n{nft['description']}\n\nЦена: {nft['price']} $TON', parse_mode='html')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
