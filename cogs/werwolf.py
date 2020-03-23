import discord
import json
import re
import operator

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

    PLAYER_MIN = 1
    ready_list = []
    player_list = {}
    role_list = list(ww_roles.keys())
    current_roles = []
    died = [None, None, None]  # [von werwölfen, von weißer werwolf, von hexe]

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
        self.current_roles = ['Wildes Kind', 'Hexe', 'Seherin']
        self.playing = True
        for i in range(len(self.current_roles) - 2):
            role = self.current_roles[i] = ' '.join(
                map(lambda part: part.capitalize(), self.current_roles[i].split(' ')))
            role_info = self.ww_roles[role]
            role_info['role'] = role

            self.player_list[ctx.message.author] = role_info
            del self.player_list[ctx.message.author]['wake up']
            del self.player_list[ctx.message.author]['good']
            del self.player_list[ctx.message.author]['description']
        await wild_child(self)

    @commands.command(pass_context=True,
                      description='Beschreibung der verschiedenen Rollen.',
                      brief='Beschreibung der verschiedenen Rollen.')
    @commands.check(is_game_channel)
    async def rollen(self, ctx):
        await ctx.send('\n'.join(self.role_list))  # TODO Werwolfrollen beschreiben

    @commands.command(pass_context=True,
                      description='Bereit für Werwolf.',
                      brief='Bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def ready(self, ctx):
        if ctx.message.author not in self.ready_list and not self.playing:
            self.ready_list.append(ctx.message.author)
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
            await ctx.send('Bereit sind:\n' + '\n'.join(map(lambda spieler: spieler.mention, self.ready_list)))
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
            await ctx.send(
                spieler.mention + ' hat das Spiel gestartet und wählt somit, welche Rollen dabei sind. Mitspieler sind:' + mitspieler)
            await ctx.send(spieler.mention + ', gib ' + str(len(self.ready_list)) + ' Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Trenne mit einem Komma, z.B. \"Rolle1, Rolle2, Rolle3\"')
            self.playing = True
            self.game_status['waiting for selection'] = True
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        elif self.playing:
            if message.author.id == self.playerID and message.channel.id in game_channel_list:
                if self.game_status['waiting for selection']:
                    self.current_roles = message.content.split(',')
                    print(self.current_roles)
                    if not correct_roles(self):
                        await message.channel.send('Da stimmt etwas nicht. Gib ' + str(len(self.ready_list)) + ' Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Vergiss die Werwölfe nicht!')
                    else:
                        role_string = '\n'.join(self.current_roles)
                        await message.channel.send('Die Rollen sind also \n' + role_string + '\nIst das so richtig?')
                        self.game_status['waiting for selection'] = False
                        self.game_status['selecting'] = True
                elif self.game_status['selecting'] and message.content.lower().strip() == 'ja':
                    await message.channel.send('Okay, dann verteile ich jetzt die Rollen.')
                    # Schicke Rolle an jeden Spieler einzeln, nachdem die Rollen verteilt wurden
                    await distribute_roles(self)
                    await first_night(self)
                elif self.game_status['selecting'] and message.content.lower().strip() == 'nein':
                    await message.channel.send('Gib die Rollen noch einmal ein. Trenne mit einem Komma.')
                    self.game_status['waiting for selection'] = True
                    self.game_status['selecting'] = False

            if message.author == get_player(self, 'Dieb') and isinstance(message.channel,discord.DMChannel) and self.phase == "THIEF":
                for role in self.current_roles[-2:]:
                    if message.content.lower().strip() == role.lower():
                        self.player_list[message.author]['role'] = role
                        role_index = self.current_roles.index(role)
                        self.current_roles[self.current_roles.index('Dieb')] = role
                        self.current_roles[role_index] = 'Dieb'
                        print(self.current_roles)
                        await message.author.send('Okay, du hast nun folgende Identität: ' + role)
                        await self.bot.get_channel(GAME_TEST_CHANNEL).send(THIEF_FINISHED)
                        if 'Amor' in self.current_roles:
                            await amor(self)
                        elif 'Wildes Kind' in self.current_roles:
                            await wild_child(self)
                        else:
                            await play_game(self)
                        return
                await message.author.send('Das war keine der zur Wahl stehenden Identitäten. Bitte wähle noch einmal.')
            elif message.author == get_player(self, 'Amor') and isinstance(message.channel, discord.DMChannel) and self.phase == "AMOR":
                users = re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)
                users = [int(users[i]) for i in range(len(users)) if i == users.index(users[i])]
                if len(users) >= 2 and correct_ids(self, users):
                    self.player_list[message.author]['loving'] = list(map(lambda user: self.bot.get_user(user), users[:2]))
                    await message.author.send('Okay, die beiden sind nun verliebt: ' + ' und '.join(list(map(lambda user: user.mention(), self.player_list[message.author]['loving']))))
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send(AMOR_FINISHED)
                    if 'Wildes Kind' in self.current_roles:
                        await wild_child(self)
                    else:
                        await play_game(self)
                else:
                    await message.author.send(NOT_UNDERSTAND + AMOR_INPUT)
            elif message.author == get_player(self, 'Wildes Kind') and isinstance(message.channel, discord.DMChannel) and self.phase == "WILD CHILD":
                user_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)[0])
                if user_id in map(lambda p: p.id, self.player_list.keys()) and user_id != message.author.id:
                    self.player_list[message.author]['role model'] = self.bot.get_user(user_id)
                    await message.author.send('Okay, diese Person ist nun dein Vorbild: ' + self.player_list[message.author]['role model'].mention())
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send(WILD_CHILD_FINISHED)
                    await play_game(self)
                else:
                    await message.author.send(NOT_UNDERSTAND + WILD_CHILD_INPUT)
            elif message.author == get_player(self, 'Heiler') and isinstance(message.channel, discord.DMChannel) and self.phase == "HEALER":
                user_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)[0])
                if user_id in map(lambda p: p.id, self.player_list.keys()) and user_id != message.author.id and is_alive(self, user_id):
                    self.player_list[message.author]['chosen'] = self.bot.get_user(user_id)
                    await message.author.send('Okay, diese Person beschützt du heute Nacht: ' + self.player_list[message.author]['chosen'].mention())
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send(HEALER_FINISHED)
                    if 'Seherin' in self.current_roles and is_alive(self, get_player(self, 'Seherin').id):
                        await seer(self)
                    else:
                        await werewolves(self)
                elif not is_alive(self, user_id):
                    await message.author.send( NOT_ALIVE + HEALER_INPUT )
                else:
                    await message.author.send(NOT_UNDERSTAND + HEALER_INPUT)
            elif message.author == get_player(self, 'Seherin') and isinstance(message.channel, discord.DMChannel) and self.phase == "SEER":
                user_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)[0])
                if user_id in map(lambda p: p.id, self.player_list.keys()) and user_id != message.author.id and is_alive(self, user_id):
                    checked_person = self.bot.get_user(user_id)
                    await message.author.send(self.player_list[checked_person].mention() + ' hat folgende Identität: ' + self.player_list[checked_person]['role'])
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send(SEER_FINISHED)
                    await werewolves(self)
                elif not is_alive(self, user_id):
                    await message.author.send(NOT_ALIVE + SEER_INPUT)
                else:
                    await message.author.send(NOT_UNDERSTAND + SEER_INPUT)
            elif is_bad(message.author.id) and message.channel.id == WERWOELFE_TEST_CHANNEL and self.phase == "WEREWOLVES":
                user_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)[0])
                if user_id in map(lambda p: p.id, self.player_list.keys()) and user_id != message.author.id and is_alive(self, user_id):
                    self.player_list[message.author]['citizen'] = self.bot.get_user(user_id)
                    await self.bot.get_channel(WERWOELFE_TEST_CHANNEL).send(message.author.mention() + ' möchte folgende Person fressen: ' + self.player_list[message.author]['citizen'].mention())
                    if werewolves_chosen(self):
                        citizens = []
                        for p in self.player_list:
                            if not p['good']:
                                citizens.append(p['citizen'])
                        self.died[0] = max(dict(Counter(citizens)).items(), key=operator.itemgetter(1))[0]
                        await self.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Wollt ihr folgende Person fressen: ' + self.died[0].mention() + '? (Es reicht, wenn einer von euch \"Ja\" bzw. \"Nein\" antwortet, sprecht euch also ab!))')
                        self.phase = "WEREWOLVES_VALIDATING"
                # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich
            elif is_bad(message.author.id) and message.channel.id == WERWOELFE_TEST_CHANNEL and self.phase == "WEREWOLVES_VALIDATING":
                if message.content.lower().strip() == 'ja':
                    await self.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Ihr habt folgende Person gefressen: ' + self.died[0].mention())
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send( WEREWOLVES_FINISHED )
                    if 'Weißer Werwolf' in self.current_roles and is_alive(self, get_player(self, 'Weißer Werwolf').id) and (self.round_no % 2 == 0):
                        await white_werewolf(self)
                    elif 'Hexe' in self.current_roles and is_alive(self, get_player(self, 'Hexe').id):
                        await witch(self)
                    else:
                        await daytime(self)
                elif message.content.lower().strip() == 'nein':
                    await self.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Okay, wen möchtet ihr fressen? (Nur, wer seine Meinung ändert, sollte nochmal seine Stimme ändern.)')
                    self.phase = "WEREWOLVES"
                # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich
            elif message.author == get_player(self, 'Weißer Werwolf') and isinstance(message.channel, discord.DMChannel) and self.phase == "WHITE_WEREWOLF":
                try:
                    user_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)[0])
                except AttributeError:
                    if message.content.lower().split() == 'niemanden':
                        await self.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
                    else:
                        await message.author.send( NOT_UNDERSTAND + WHITE_WEREWOLF_INPUT)
                    return
                if user_id in map(lambda p: p.id, self.player_list.keys()) and user_id != message.author.id and is_alive(self, user_id) and is_bad(self, user_id):
                    comrade = self.bot.get_user(user_id)
                    await message.author.send('Du hast folgende Person gefressen' + self.player_list[comrade].mention())
                    self.died[1] = comrade
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
                    if 'Hexe' in self.current_roles and is_alive(self, get_player(self, 'Hexe').id):
                        await witch(self)
                    else:
                        await daytime(self)
                elif not is_alive(self, user_id):
                    await message.author.send( NOT_ALIVE + WHITE_WEREWOLF_INPUT)
                elif not is_bad(self, user_id):
                    await message.author.send('Die Person ist keiner deiner Kameraden...\n' + WHITE_WEREWOLF_INPUT)
                else:
                    await message.author.send(NOT_UNDERSTAND + WHITE_WEREWOLF_INPUT)
            elif message.author == get_player(self, 'Hexe') and isinstance(message.channel, discord.DMChannel) and self.phase == "WITCH_HEAL":
                if message.content.lower().strip() == 'ja':
                    del self.player_list[get_player(self, 'Hexe')]['tranks'][self.player_list[get_player(self, 'Hexe')]['tranks'].index('Heiltrank')]
                    await message.author.send(self.died[0].mention() + ' wurde von dir gerettet!')
                    self.died[0] = None
                elif message.content.lower().strip() == 'nein':
                    await message.author.send(self.died[0].mention() + ' wurde nicht von dir gerettet.')
                else:
                    await message.author.send(NOT_UNDERSTAND + self.died[0].mention() + WITCH_INPUT_HEAL)
                    return
                self.phase = "WITCH_DEATH"
                await message.author.send(WITCH_INPUT_KILL)
            elif message.author == get_player(self, 'Hexe') and isinstance(message.channel, discord.DMChannel) and self.phase == "WITCH_DEATH":
                try:
                    user_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', message.content)[0])
                except AttributeError:
                    if message.content.lower().strip() == 'nein':
                        await message.author.send('Du hast niemanden vergiftet.')
                        await self.bot.get_channel(GAME_TEST_CHANNEL).send(WITCH_FINISHED)
                        self.phase = "DAYTIME"
                        await daytime(self)
                    return
                if user_id in map(lambda p: p.id, self.player_list.keys()) and user_id != message.author.id and is_alive(self, user_id):
                    del self.player_list[get_player(self, 'Hexe')]['tranks'][self.player_list[get_player(self, 'Hexe')]['tranks'].index('Gifttrank')]
                    killed_person = self.bot.get_user(user_id)
                    await message.author.send('Du hast folgende Person vergiftet: ' + self.player_list[killed_person].mention())
                    self.died[2] = killed_person
                    await self.bot.get_channel(GAME_TEST_CHANNEL).send(WITCH_FINISHED)
                    await daytime(self)
                elif not is_alive(self, user_id):
                    await message.author.send(NOT_ALIVE + WITCH_INPUT_KILL)
                else:
                    await message.author.send( NOT_UNDERSTAND + WITCH_INPUT_KILL)


def setup(bot):
    bot.add_cog(Werwolf(bot))
