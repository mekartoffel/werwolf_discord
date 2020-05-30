import asyncio
import discord
import datetime

from discord.ext import commands


class Allgemein(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        # Er soll aber nicht auf sich selbst reagieren
        if message.author == self.bot.user:
            return

        try:
            print(message.channel.name + '(' + message.author.name + '): ' + message.content)
        except AttributeError:
            print( message.author.name + ': ' + message.content)
        except UnicodeEncodeError:
            print('Nachricht kann nicht angezeigt werden.')


    @commands.command(pass_context=True,
                      hidden=True,
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


    @commands.command(name='ping',
                      pass_context=True,
                      hidden=True)
    async def ping(self, ctx):
        t_diff: datetime.timedelta = abs(ctx.message.created_at - datetime.datetime.utcnow())
        e = discord.Embed(title='Pong!', description='Ping-Pong innerhalb von {} ms'.format(round(t_diff.total_seconds() * 1000, 2)),
                          colour=discord.Colour.blurple())
        await ctx.message.channel.send(embed=e)


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