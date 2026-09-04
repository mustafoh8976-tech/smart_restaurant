from aiogram import Router, types, F


router = Router()


@router.message(F.text == 'AI-помощник')
async def ai_handler(message: types.Message):
    await message.answer('AI-помощник временно отключен')