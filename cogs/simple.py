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
                print(emoji)
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
        
        #print(discord.utils.find(lambda m: message.content in m.name , self.bot.get_guild(TEST_SERVER_ID).members))

        # Er soll aber nicht auf sich selbst antworten
        if message.author == self.bot.user:
            return

        try:
            print(message.channel.name + '(' + message.author.name + '): ' + message.content)
        except AttributeError:
            print( message.author.name + ': ' + message.content)
        except UnicodeEncodeError:
            print('Nachricht kann nicht angezeigt werden.')

    @commands.command(pass_context=True,
        description='Ist wie ein Echo: Gibt die gleiche Nachricht aus wie eingegeben wurde.',
        brief='Wiederholt die eingegebene Nachricht.')
    async def echo(self, ctx, *, argument):
        print(argument)
        await ctx.send(argument)
        await ctx.message.delete()

    @echo.error
    async def echo_on_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await asyncio.sleep(0.5)
            await ctx.send('Was soll ich wiederholen?')


    #Wenn jemand offline geht
    async def on_member_update(self, before, after):
        if str(after.status) == 'offline' or str(before.status) == 'online':
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