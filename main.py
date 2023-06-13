from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import asyncio
from decouple import config
class TodoBot:
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.dp.register_message_handler(self.cmd_start, commands=["start"])
        self.dp.register_message_handler(self.cmd_add, commands=["add"])
        self.dp.register_message_handler(self.cmd_list, commands=["list"])
        self.dp.register_message_handler(self.cmd_update, commands=["update"])
        self.dp.register_message_handler(self.cmd_delete, commands=["delete"])

        self.tasks = {}  # Словарь для хранения задач, где ключами являются номера задач

    async def cmd_start(self, message: types.Message, state: FSMContext):
        await message.reply("Привет! Я TODO-бот. Чем я могу тебе помочь?")
        await state.finish()

    async def cmd_add(self, message: types.Message):
        await message.reply("Введите новую задачу:")
        self.dp.register_message_handler(self.process_new_task)

    async def process_new_task(self, message: types.Message):
        task = message.text

        task_index = len(self.tasks) + 1
        self.tasks[task_index] = task  # Добавляем задачу в словарь

        await message.reply(f"Задача '{task}' успешно добавлена с номером '{task_index}'!")

        self.dp.message_handlers.unregister(self.process_new_task)  # Удаляем обработчик

    async def cmd_list(self, message: types.Message):
        if self.tasks:
            tasks_list = "\n".join([f"{index}. {task}" for index, task in self.tasks.items()])
            await message.reply(f"Список задач:\n{tasks_list}")
        else:
            await message.reply("Список задач пуст!")

    async def cmd_update(self, message: types.Message):
        if not self.tasks:
            await message.reply("Список задач пуст!")
            return

        await message.reply("Выберите номер задачи, которую хотите обновить:")
        self.dp.register_message_handler(self.process_update_task)

    async def process_update_task(self, message: types.Message):
        try:
            self.current_task_index = int(message.text)
            if self.current_task_index not in self.tasks:
                raise ValueError
        except ValueError:
            await message.reply("Некорректный номер задачи. Попробуйте ещё раз.")
            return

        await message.reply("Введите новое значение для задачи:")
        self.dp.message_handlers.unregister(self.process_update_task)
        self.dp.register_message_handler(self.process_update_task_value, state="*")

    async def process_update_task_value(self, message: types.Message):
        new_task_value = message.text

        self.tasks[self.current_task_index] = new_task_value  # Обновляем значение задачи

        await message.reply(f"Задача с номером '{self.current_task_index}' успешно обновлена!")

        self.dp.message_handlers.unregister(self.process_update_task_value)

    async def cmd_delete(self, message: types.Message):
        if not self.tasks:
            await message.reply("Список задач пуст!")
            return

        await message.reply("Выберите номер задачи, которую хотите удалить:")
        self.dp.register_message_handler(self.process_delete_task)

    async def process_delete_task(self, message: types.Message):
        try:
            task_index = int(message.text)
            if task_index not in self.tasks:
                raise ValueError
        except ValueError:
            await message.reply("Некорректный номер задачи. Попробуйте ещё раз.")
            return

        deleted_task = self.tasks.pop(task_index)  # Удаляем задачу из словаря
        await message.reply(f"Задача '{deleted_task}' с номером '{task_index}' успешно удалена!")

        self.dp.message_handlers.unregister(self.process_delete_task)

    async def start(self):
        await self.dp.start_polling(reset_webhook=True)


if __name__ == '__main__':
    bot_token = config('TOKEN')
    todo_bot = TodoBot(bot_token)
    asyncio.run(todo_bot.start())