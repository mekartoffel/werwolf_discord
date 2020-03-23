# -*- coding: utf8 -*-

from discord.ext import commands
from private import *

import discord
import time
import locale
import logging



bot = commands.Bot(command_prefix='+', description='Der Tingeltangelbot')


startup_extensions = ['cogs.simple',
                      'cogs.werwolf']

for ext in startup_extensions:
    bot.load_extension(ext)

l = locale.setlocale(locale.LC_ALL, 'deu_deu')

"""Logging"""
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# -----------------------------------------------------------------------------

# Fuer Pings: <@ID> oder member.mention

# user = discord.utils.get(bot.get_all_members(), id='ID')
# await (self.)bot.send_message(user, msg)

# emoji = get((self.)bot.get_all_emojis(), name='EMOJINAME')
# await (self.)bot.say(emoji)

# -----------------------------------------------------------------------------


@bot.event
async def on_connect():
    print('Bot connected!')

@bot.event
async def on_ready():
    print(time.strftime('%c: '))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    #channels = [TEST_SERVER_ID]
    #for channel in channels:
        #await bot.get_channel(channel).send('Hallo, ich bin neu hier!')
    await bot.change_presence(activity=discord.Game(name='Werwolf'))

@bot.event
async def on_resumed():
    print('Bot resumed.')

try:
    bot.loop.run_until_complete(bot.start(TOKEN))
except KeyboardInterrupt:
    bot.loop.run_until_complete(bot.logout())
    # cancel all tasks lingering
finally:
    bot.loop.close()

#bot.run(TOKEN)

#bot.loop.close()
