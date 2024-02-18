import discord
import re
import os
from datetime import timedelta
from discord.abc import Messageable
from discord import TextChannel, Message, Thread
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, LLMResult, SystemMessage

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
CHANNEL_NAME = "wikibot"


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: Message):
    if message.channel.name == CHANNEL_NAME or message.channel.parent.name == CHANNEL_NAME:
        if message.author == client.user:
            return


        thread: Messageable
        # if it isn't in a thread, create a thread from the message content.
        if message.channel.name == CHANNEL_NAME:
            title = message.content
            thread: Thread = await message.create_thread(name=title[:100])
        else:
            thread = message.channel

        messages = [SystemMessage(content="You are a good assistant.")]
        async for thread_message in thread.history(limit=10):
            content = re.sub("<@.*>", "", thread_message.content) or re.sub("<@.*>", "", thread_message.system_content)

            if thread_message.author == client.user:
                messages.insert(1, AIMessage(content=content))
            else:
                messages.insert(1, HumanMessage(content=content))

        content = re.sub("<@.*>", "", message.content)
        messages.append(HumanMessage(content=content))

        chat = ChatOpenAI(
            model_name=os.environ["OPENAI_API_MODEL"],
            temperature=os.environ["OPENAI_API_TEMPERATURE"],
        )

        response = chat(messages)

        await thread.send(f"{message.author.mention}\n{response.content}")


if __name__ == "__main__":
    client.run(os.environ["DISCORD_TOKEN"])
