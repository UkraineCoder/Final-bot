async def delete_markup(message, state):
    data = await state.get_data()
    msg = data['msg']
    await message.bot.edit_message_reply_markup(message_id=msg, chat_id=message.chat.id)