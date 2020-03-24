import discord
import json
import re
import operator
import asyncio

from discord.ext import commands
from private import *
from cogs.werwolf_functions import *
from typing import Dict, Any
from collections import Counter
from my_constants import *

class Werwolf(commands.Cog):
    ww_data = {}
    ww_roles = {}
    with open('werwolf_rollen.json', 'r', encoding='utf-8') as ww_data:
        ww_roles = json.load(ww_data)

    PLAYER_MIN = 7
    ready_list = []
    player_list = {}
    role_list = list(ww_roles.keys())
    current_roles = []
    died = [None, None, None]  # [von werwölfen, von weißer werwolf, von hexe]
    new_vote = False

    playerID = None  # welcher Spieler hat das Spiel gestartet?
    playing = False  # läuft ein Spiel?
    phase = ''  # Was passiert gerade?

    game_status: Dict[str, bool] = {'waiting for selection': False, 'selecting': False, 'playing': False}
    round_no = 1

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True,
                      description='Beschreibung des Spiels Werwolf.',
                      brief='Beschreibung des Spiels Werwolf.')
    @commands.check(is_game_channel)
    async def beschreibung(self, ctx):
        await ctx.send('TODO')  # TODO Werwolf beschreiben

    @commands.command(pass_context=True,
                      description='TEST',
                      brief='TEST')
    async def test(self, ctx):
        self.current_roles = ['Dieb', 'Hexe', 'Seherin']
        self.playing = True
        for i in range(len(self.current_roles) - 2):
            role = self.current_roles[i] = ' '.join([part.capitalize() for part in self.current_roles[i].split(' ')])
            role_info = self.ww_roles[role]
            role_info['role'] = role

            self.player_list[ctx.message.author] = role_info
            del self.player_list[ctx.message.author]['wake up']
            del self.player_list[ctx.message.author]['description']
            print(self.player_list)
        await wake_thief(self)

    @commands.command(pass_context=True,
                      description='Beschreibung der verschiedenen Rollen.',
                      brief='Beschreibung der verschiedenen Rollen.')
    @commands.check(is_game_channel)
    async def rollen(self, ctx, *, argument):
        arg = ' '.join([part.capitalize() for part in argument.split(' ')])
        print(arg)
        print(self.ww_roles[arg])
        await ctx.send(self.ww_roles[arg]['description'])

    @rollen.error
    async def echo_on_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await asyncio.sleep(0.5)
            await ctx.send('Es gibt folgende Rollen: ' + ', '.join(self.role_list))

    @commands.command(pass_context=True,
                      description='Bereit für Werwolf.',
                      brief='Bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def ready(self, ctx):
        if ctx.message.author not in self.ready_list and not self.playing:
            self.ready_list.append(ctx.message.author)
            print(self.ready_list)
            await ctx.message.delete()
            await ctx.send(ctx.message.author.mention + ' ist bereit!')
        elif self.playing:
            await ctx.send('Es findet gerade ein Spiel statt. Du kannst danach mitspielen.')
        else:
            await ctx.send('Du bist schon bereit.')

    @commands.command(pass_context=True,
                      description='Nicht mehr bereit für Werwolf.',
                      brief='Nicht mehr bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def unready(self, ctx):
        if ctx.message.author in self.ready_list and not self.playing:
            self.ready_list.remove(ctx.message.author)
            await ctx.message.delete()
            await ctx.send(ctx.message.author.mention + ' ist nicht mehr bereit!')
        elif self.playing:
            await ctx.send('Das Spiel läuft schon. Du musst gar nicht bereit sein, spiel einfach mit! :)')
        else:
            await ctx.send('Du warst eh nicht bereit.')

    @commands.command(pass_context=True,
                      description='Liste von Spielern, die bereit sind.',
                      brief='Liste von Spielern, die bereit sind.')
    @commands.check(is_game_channel)
    async def readylist(self, ctx):
        if self.ready_list:
            await ctx.send('Bereit sind:\n' + '\n'.join([spieler.mention for spieler in self.ready_list]))
        else:
            await ctx.send('Es ist noch keiner bereit.')

    @commands.command(pass_context=True,
                      description='Starte Werwolf. Derjenige, der startet, bestimmt, welche Rollen mit dabei sind.',
                      brief='Starte Werwolf.')
    @commands.check(is_game_channel)
    async def start(self, ctx):
        if ctx.message.author not in self.ready_list:
            # Der Starter muss auch in der ready_list sein
            self.ready_list.append(ctx.message.author)
            await ctx.send(ctx.message.author.mention + ' ist bereit!')
        if len(self.ready_list) >= self.PLAYER_MIN:
            # Starte das Spiel nur, wenn genügend Spieler bereit sind
            spieler = ctx.message.author
            mitspieler = ''
            for s in self.ready_list:
                mitspieler = mitspieler + '\n' + s.mention
            self.playerID = spieler.id
            print(still_alive(self))
            await ctx.send(
                spieler.mention + ' hat das Spiel gestartet und wählt somit, welche Rollen dabei sind. Mitspieler sind:' + mitspieler)
            await ctx.send(spieler.mention + ', gib ' + str(len(self.ready_list)) + ' Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Trenne mit einem Komma, z.B. \"Rolle1, Rolle2, Rolle3\"')
            self.playing = True
            self.game_status['waiting for selection'] = True
            self.phase = 'SELECTION'
        else:
            await ctx.send('Es sind noch nicht genügend Spieler. Es sollte(n) noch mindestens ' + str(self.PLAYER_MIN - len(self.ready_list)) + ' Spieler dazukommen.')

    @commands.command(pass_context=True,
                      hidden=True,
                      description='Setzt die Ready-Liste für Werwolf zurück. Das kann aber nur der Bot-Owner.',
                      brief='Setzt die Ready-Liste für Werwolf zurück.')
    @commands.is_owner()
    async def reset(self, ctx):
        if not self.playing:
            self.ready_list = []
            await ctx.send('Die Bereit-Liste wurde zurückgesetzt. Sie ist nun wieder leer.')

    @commands.command(pass_context=True,
                      hidden=True,
                      description='Setzt die Ready-Liste für Werwolf zurück. Das kann aber nur der Bot-Owner.',
                      brief='Setzt die Ready-Liste für Werwolf zurück.')
    @commands.is_owner()
    async def reset_game(self, ctx):
        if self.playing:
            reset_vars(self)
            await ctx.send('Das Spiel wurde zurückgesetzt.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        elif self.playing:
            print(self.phase)
            if message.channel.id in game_channel_list:
                if  message.author.id == self.playerID and self.phase == "SELECTION":
                    if self.game_status['waiting for selection']:
                        self.current_roles = [r.strip() for r in message.content.split(',')]
                        print(self.current_roles)
                        self.current_roles = [' '.join([part.capitalize() for part in r.split(' ')]) for r in self.current_roles]
                        print(self.current_roles)
                        if not correct_roles(self):
                            await message.channel.send('Da stimmt etwas nicht. Gib ' + str(len(self.ready_list)) + ' Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Vergiss die Werwölfe nicht!')
                        else:
                            role_string = '\n'.join(self.current_roles)
                            await message.channel.send('Die Rollen sind also \n' + role_string + '\nIst das so richtig?')
                            self.game_status['waiting for selection'] = False
                            self.game_status['selecting'] = True
                    elif self.game_status['selecting']:
                        if message.content.lower().strip() == 'ja':
                            await message.channel.send('Okay, dann verteile ich jetzt die Rollen.')
                            # Schicke Rolle an jeden Spieler einzeln, nachdem die Rollen verteilt wurden
                            await distribute_roles(self)
                        elif message.content.lower().strip() == 'nein':
                            await message.channel.send('Gib die Rollen noch einmal ein. Trenne mit einem Komma.')
                            self.game_status['waiting for selection'] = True
                            self.game_status['selecting'] = False
                elif message.author == get_player(self, 'Jäger') and (self.phase == "HUNTER_NIGHT" or self.phase == "HUNTER_VOTE"):
                    await choosing_hunter(self, message)
                elif self.phase == "VOTING":
                    await voting(self, message)

            if isinstance(message.channel, discord.DMChannel):
                if message.author == get_player(self, 'Dieb') and self.phase == "THIEF":
                    await choosing_thief(self, message)
                elif message.author == get_player(self, 'Amor') and self.phase == "AMOR":
                    await choosing_amor(self, message)
                elif message.author == get_player(self, 'Wildes Kind') and self.phase == "WILD CHILD":
                    await choosing_wild_child(self, message)
                elif message.author == get_player(self, 'Heiler') and self.phase == "HEALER":
                    await choosing_healer(self, message)
                elif message.author == get_player(self, 'Seherin') and self.phase == "SEER":
                    await choosing_seer(self, message)
                elif message.author == get_player(self, 'Stotternder Richter') and self.phase == "VOTING" and 'ABSTIMMUNG' in message.content:
                    if self.player_list[message.author]['new vote']:
                        self.new_vote = True
                        self.player_list[message.author]['new vote'] = 0
                        message.author.send('Okay, es wird eine zweite Abstimmung geben.')
                #Werewolves
                elif message.author == get_player(self, 'Weißer Werwolf') and self.phase == "WHITE_WEREWOLF":
                    await choosing_white_werewolf(self, message)
                elif message.author == get_player(self, 'Hexe'):
                    if self.phase == "WITCH_HEAL":
                        await choosing_witch_heal(self, message)
                    elif self.phase == "WITCH_DEATH":
                        await choosing_witch_kill(self, message)
            elif message.channel.id == WERWOELFE_TEST_CHANNEL:
                if is_bad(self, message.author.id):
                    if self.phase == "WEREWOLVES":
                        await choosing_werewolves(self, message)
                    elif self.phase == "WEREWOLVES_VALIDATING":
                        await confirming_werewolves(self, message)
            


def setup(bot):
    bot.add_cog(Werwolf(bot))
