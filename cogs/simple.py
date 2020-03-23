import discord
import random
import time
import asyncio

from random import randint
from discord.ext import commands
from discord.utils import get
from private import *


class Allgemein(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        #Egal, von wem die Nachricht kommt, er soll reagieren
        hi = ['hallo', 'servus', 'guten tag', 'moin', 'hello', 'guten morgen', 'winke', 'hey yo']
        glitzer = ['glitter', 'glitzer', 'sparkle', 'stern', '✨']
        for word in hi:
            if word in message.content.lower():
                emoji = get(self.bot.emojis, id=518072805296963584)
                await message.add_reaction(emoji)
                break
        for word in glitzer:
            if word in message.content.lower():
                emoji = get(self.bot.emojis, id=524903179574575124)
                await message.add_reaction(emoji)
                break
        if 'hose' in message.content.lower():
            emoji = get(self.bot.emojis, id=518072681837494292)
            await message.add_reaction(emoji)


        # Er soll aber nicht auf sich selbst antworten
        if message.author == self.bot.user:
            return

        try:
            print(message.channel.name + '(' + message.author.name + '): ' + message.content)
        except AttributeError:
            print( message.author.name + ': ' + message.content)
        except UnicodeEncodeError:
            print('Nachricht kann nicht angezeigt werden.')



    #Wenn jemand offline geht
    async def on_member_update(self, before, after):
        server = self.bot.get_guild(id=TEST_SERVER_ID)
        if str(after.status) == 'offline':
            if after.guild.id == TEST_SERVER_ID or after not in server.members:
                msg = time.strftime('%c: ') + '{} ist von {} auf {} gegangen.'.format(after.name, before.status, after.status)
                print(msg)


    @commands.command(pass_context=True,
        hidden=True,
        brief='Hält den Bot an.',
        description='Hält den Bot an. Kann nur vom Bot-Owner gemacht werden.')
    @commands.is_owner()
    async def stop(self, ctx):
        author = ctx.message.author.name
        try:
            await ctx.send('Bot wird beendet...')
            await self.bot.logout()
            self.bot.loop.stop()
            print('{} has shut down the bot...'.format(author))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('{} has attempted to shut down the bot, but the following '
                'exception occurred;\n\t->{}'.format(author, exc))


def setup(bot):
    bot.add_cog(Allgemein(bot))