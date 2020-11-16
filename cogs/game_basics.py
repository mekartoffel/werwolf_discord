import discord

from private import *
from discord.ext import commands


def is_ww_game_channel(ctx):
    """Check if channel of context is the channel where you can play.
    :param ctx: Context
    :return: `True` if the channel is a ww game channel otherwise `False`
    """
    return ctx.message.channel.id in ww_game_channel_list

def is_game_channel(ctx):
    return is_ww_game_channel(ctx)

class GameBasics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      hidden=True,
                      description='Channel zu meinem Server hinzufügen. *Der Bot braucht dafür die Berechtigung, Kanäle zu verwalten!*',
                      brief='Channel zu meinem Server hinzufügen.')
    @commands.is_owner()
    async def addchannel(self, ctx):
        with open('private.json', 'w', encoding='utf-8') as server_data:
            # Kann man datenschutztechnisch sicher besser loesen, aber da der Bot eh nur privat genutzt wird, spielt das erst mal nur eine kleinere Rolle
            if not server_dict[str(ctx.guild.id)]:
                server_dict[str(ctx.guild.id)] = {}
            test_cat = await ctx.guild.create_category('Test')
            test_channel = await ctx.guild.create_text_channel('test_chan', category=test_cat)
            server_dict[str(ctx.guild.id)]['test channel'] = test_channel.id
            json.dump(server_dict, server_data, ensure_ascii=False)
            get_server_info()


    @commands.command(pass_context=True,
                      name='description',
                      aliases=['beschreibung'],
                      description='Beschreibung des Spiels.',
                      brief='Beschreibung des Spiels.')
    @commands.check(is_game_channel)
    async def descr(self, ctx):
        if is_ww_game_channel(ctx):
            await ctx.send('Thematisch geht es darum, dass das kleine Dörfchen Düsterwald von Werwölfen heimgesucht wird. Die Gruppe der Bürger versucht die Wölfe, die sich als Bürger getarnt haben, zu entlarven. Dagegen versuchen die Wölfe, als einzige zu überleben und Widersacher auszuschalten. Darüber hinaus gibt es Charaktere mit eigenen Zielen. ||(Geklaut von Wikipedia)||\n(Für Infos, was für Charaktere es gibt, sende `?roles` und für Infos zu einem speziellen Charakter sende `?roles [Charaktername]`.)')

    @commands.command(pass_context=True,
                      description='Beschreibung, wie das Spiel gespielt wird.',
                      brief='Wie wird das Spiel gespielt?')
    @commands.check(is_game_channel)
    async def howtoplay(self, ctx):
        if is_ww_game_channel(ctx):
            embed = discord.Embed(title="How To Play", description="Werwolf")
            embed.add_field(name="1. Schritt",
                            value=" Wenn du mitspielen willst, gib `?ready` ein.\nWenn du dich umentscheiden solltest und doch nicht spielen willst, gib `?unready` ein.",
                            inline=False)
            embed.add_field(name="2. Schritt",
                            value="Wenn die Spielgruppe vollständig ist, gibt einer der Spieler `?start` ein. Das Spiel beginnt.",
                            inline=False)
            embed.add_field(name="3. Schritt",
                            value="Diejenige Person, die das Spiel gestartet hat, wählt nun die Rollen für diese Spielrunde aus.\nWelche Rollen gibt es? - `?roles`\nWas ist das für eine Rolle? - `?roles *Rollenname*`",
                            inline=False)
            embed.add_field(name="4. Schritt", value="Das Spiel startet!",
                            inline=False)
            embed.set_footer(
                text="Ich hoffe, ab hier ist alles gut erklärt. Wenn nicht, dann kontaktiere bitte den Bot-Besitzer, damit er diese Anleitung erweitert.")
            await ctx.message.channel.send(embed=embed)

    @commands.command(pass_context=True,
                      name='ready',
                      aliases=['bereit'],
                      description='Bereitmelden, um zu spielen.',
                      brief='Bereitmelden, um zu spielen.')
    @commands.check(is_game_channel)
    async def ready(self, ctx):
        if is_ww_game_channel(ctx):
            await self.bot.cogs['Werwolf'].ready(ctx)

    @commands.command(pass_context=True,
                      name='unready',
                      aliases=['nichtbereit'],
                      description='Nicht mehr bereit für Werwolf.',
                      brief='Nicht mehr bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def unready(self, ctx):
        if is_ww_game_channel(ctx):
            await self.bot.cogs['Werwolf'].unready(ctx)

    @commands.command(pass_context=True,
                      name='readylist',
                      aliases=['bereitliste'],
                      description='Liste von Spielern, die bereit sind.',
                      brief='Liste von Spielern, die bereit sind.')
    @commands.check(is_game_channel)
    async def readylist(self, ctx):
        if is_ww_game_channel(ctx):
            await self.bot.cogs['Werwolf'].readylist(ctx)


    @commands.command(pass_context=True,
                      name='start',
                      description='Starte das Spiel.',
                      brief='Starte das Spiel.')
    @commands.check(is_game_channel)
    async def start(self, ctx):
        if is_ww_game_channel(ctx):
            await self.bot.cogs['Werwolf'].start(ctx)


    @commands.command(pass_context=True,
                      hidden=True,
                      name='resetreadylist',
                      aliases=['resetrl','reset_rl','reset_readylist'],
                      description='Setzt die Ready-Liste zurück.',
                      brief='Setzt die Ready-Liste zurück.')
    @commands.check(is_game_channel)
    @commands.is_owner()
    async def reset_readylist(self, ctx):
        if is_ww_game_channel(ctx):
            await self.bot.cogs['Werwolf'].reset_readylist(ctx)


def setup(bot):
    bot.add_cog(GameBasics(bot))