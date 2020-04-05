import json

from discord.ext import commands
from cogs.werwolf_functions import *
from typing import Dict

class Game():

    def __init__(self, server_id, game_channel, werewolf_channel, bot, ww):
        self.ww = ww
        self.bot = bot
        self.server_id = server_id
        self.game_channel = game_channel
        self.werewolf_channel = werewolf_channel

        self.ready_list = []
        self.player_list = {}
        self.current_roles = []
        self.died = [None, None, None] # [von werwölfen, von weißer werwolf, von hexe]
        self.new_vote = False

        self.playerID = None  # welcher Spieler hat das Spiel gestartet?
        self.playing = False  # läuft ein Spiel?
        self.phase = ''  # Was passiert gerade?

        self.game_status: Dict[str, bool] = {'waiting for selection': False, 'selecting': False, 'playing': False}
        self.round_no = 1


class Werwolf(commands.Cog):
    ww_data = {}
    ww_roles = {}
    with open('werwolf_rollen.json', 'r', encoding='utf-8') as ww_data:
        ww_roles = json.load(ww_data)

    role_list = list(ww_roles.keys())

    PLAYER_MIN = 1
    global_playerlist = []
    #player_list = {}
    #current_roles = []
    #died = [None, None, None]  # [von werwölfen, von weißer werwolf, von hexe]
    #new_vote = False

    #playerID = None  # welcher Spieler hat das Spiel gestartet?
    #playing = False  # läuft ein Spiel?
    #phase = ''  # Was passiert gerade?

    #game_status: Dict[str, bool] = {'waiting for selection': False, 'selecting': False, 'playing': False}
    #round_no = 1

    def __init__(self, bot):
        self.bot = bot
        self.games = {v: Game(v, k['game channel'], k['werewolf channel'], bot, self) for v, k in server_dict.copy().items()}


    @commands.command(pass_context=True,
                      description='Beschreibung des Spiels Werwolf.',
                      brief='Beschreibung des Spiels Werwolf.')
    @commands.check(is_game_channel_or_dm)
    async def descr(self, ctx):
        await ctx.send('TODO')  # TODO Werwolf beschreiben

    @commands.command(pass_context=True,
                      hidden=True,
                      description='TEST',
                      brief='TEST')
    @commands.is_owner()
    async def test(self, ctx):
        game: Game = self.games[ctx.guild.id]
        game.current_roles = ['Dieb', 'Hexe', 'Seherin']
        game.playing = True
        for i in range(len(game.current_roles) - 2):
            role = game.current_roles[i] = ' '.join([part.capitalize() for part in game.current_roles[i].split(' ')])
            role_info = self.ww_roles[role].copy()
            role_info['role'] = role

            game.player_list[ctx.message.author] = role_info
            del game.player_list[ctx.message.author]['wake up']
            del game.player_list[ctx.message.author]['description']
            print(game.player_list)
        await wake_thief(game)

    @commands.command(pass_context=True,
                      description='Beschreibung der verschiedenen Rollen.',
                      brief='Beschreibung der verschiedenen Rollen.')
    @commands.check(is_game_channel_or_dm)
    async def roles(self, ctx, *, argument):
        arg = ' '.join([part.capitalize() for part in argument.split(' ')])
        print(arg)
        print(self.ww_roles[arg])
        await ctx.send(self.ww_roles[arg]['description'])

    @roles.error
    async def roles_on_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await asyncio.sleep(0.5)
            await ctx.send('Es gibt folgende Rollen: ' + ', '.join(self.role_list))

    @commands.command(pass_context=True,
                      description='Bereit für Werwolf.',
                      brief='Bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def ready(self, ctx):
        print(ctx.guild.id)
        game: Game = self.games[ctx.guild.id]
        if ctx.message.author not in self.global_playerlist and ctx.message.author not in game.ready_list and not game.playing:
            self.global_playerlist.append(ctx.message.author)
            print(self.global_playerlist)
            game.ready_list.append(ctx.message.author)
            print(game.ready_list)
            await ctx.message.delete()
            await ctx.send(ctx.message.author.mention + ' ist bereit!')
        elif game.playing:
            await ctx.send('Es findet gerade ein Spiel statt. Du kannst danach mitspielen. :)')
        elif ctx.message.author in game.ready_list:
            await ctx.send('Du bist schon bereit.')
        else:
            await ctx.send('Du bist schon in einem anderen Server dabei.')

    @commands.command(pass_context=True,
                      description='Nicht mehr bereit für Werwolf.',
                      brief='Nicht mehr bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def unready(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if ctx.message.author in self.global_playerlist and ctx.message.author in game.ready_list and not game.playing:
            self.global_playerlist.remove(ctx.message.author)
            game.ready_list.remove(ctx.message.author)
            print(game.ready_list)
            await ctx.message.delete()
            await ctx.send(ctx.message.author.mention + ' ist nicht mehr bereit!')
        elif game.playing:
            await ctx.send('Das Spiel läuft schon. Du musst gar nicht bereit sein, spiel einfach mit! ~~(Und lass dich im Zweifel umbringen, dann musst du nicht mehr mitspielen.)~~')
        else:
            await ctx.send('Du warst eh nicht bereit.')

    @commands.command(pass_context=True,
                      description='Liste von Spielern, die bereit sind.',
                      brief='Liste von Spielern, die bereit sind.')
    @commands.check(is_game_channel)
    async def readylist(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if game.ready_list:
            await ctx.send('Bereit sind:\n' + '\n'.join([player.mention for player in game.ready_list]))
        else:
            await ctx.send('Es ist noch keiner bereit.')

    @commands.command(pass_context=True,
                      description='Starte Werwolf. Derjenige, der startet, bestimmt, welche Rollen mit dabei sind.',
                      brief='Starte Werwolf.')
    @commands.check(is_game_channel)
    async def start(self, ctx):
        game: Game = self.games[ctx.guild.id]
        player = ctx.message.author
        if player not in game.ready_list:
            # Der Starter muss auch in der ready_list sein
            self.global_playerlist.append(player)
            game.ready_list.append(player)
            await ctx.send(player.mention + ' ist bereit!')
        if len(game.ready_list) >= self.PLAYER_MIN and not game.playing:
            # Starte das Spiel nur, wenn genügend Spieler bereit sind
            other_players = ''
            for s in game.ready_list:
                other_players = other_players + '\n' + s.mention
            game.playerID = player.id
            print(still_alive(game))
            await ctx.send(player.mention + ' hat das Spiel gestartet und wählt somit, welche Rollen dabei sind. Mitspieler sind:' + other_players)
            await ctx.send(player.mention + ', gib ' + str(len(game.ready_list)) + ' Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Trenne mit einem Komma, z.B. \"Rolle1, Rolle2, Rolle3\"')
            game.playing = True
            game.game_status['waiting for selection'] = True
            game.phase = 'SELECTION'
        elif game.playing:
            await ctx.send('Es findet gerade ein Spiel statt.')
        else:
            await ctx.send('Es sind noch nicht genügend Spieler. Es sollte(n) noch mindestens ' + str(self.PLAYER_MIN - len(game.ready_list)) + ' Spieler dazukommen.')

    @commands.command(pass_context=True,
                      description='Liste von Spielern, die noch am Leben sind.',
                      brief='Liste von Spielern, die noch am Leben sind.')
    @commands.check(is_game_channel_or_dm)
    async def alive(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if game.playing:
            await ctx.send('Es leben noch:\n' + '\n'.join([player.mention for player in game.player_list if is_alive(game, player.id)]))
        else:
            await ctx.send('Darüber kann ich dir keine Auskunft geben, wenn niemand spielt. :)')

    @commands.command(pass_context=True,
                      description='Liste von Spielern, die noch nicht abgestimmt haben.',
                      brief='Liste von Spielern, die noch nicht abgestimmt haben.')
    @commands.check(is_game_channel)
    async def missing_vote(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if game.playing and game.phase == 'VOTING':
            await ctx.send('Noch nicht abgestimmt haben:\n' + '\n'.join(
                [player.mention for player in game.player_list if is_alive(game, player.id) and not game.player_list[player]['voted for']]))
        elif not game.playing:
            await ctx.send('Darüber kann ich dir keine Auskunft geben, wenn niemand spielt. :)')
        else:
            await ctx.send('Es wird gerade gar nicht abgestimmt. :)')

    @commands.command(pass_context=True,
                      hidden=True,
                      description='Setzt die Ready-Liste für Werwolf zurück. Das kann aber nur der Bot-Owner.',
                      brief='Setzt die Ready-Liste für Werwolf zurück.')
    @commands.is_owner()
    async def reset(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if not game.playing:
            game.ready_list = []
            await ctx.send('Die Bereit-Liste wurde zurückgesetzt. Sie ist nun wieder leer.')

    @commands.command(pass_context=True,
                      hidden=True,
                      description='Setzt die Ready-Liste für Werwolf zurück. Das kann aber nur der Bot-Owner.',
                      brief='Setzt die Ready-Liste für Werwolf zurück.')
    @commands.is_owner()
    async def reset_game(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if game.playing:
            await reset_vars(game)
            await ctx.send('Das Spiel wurde zurückgesetzt.')

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            player = message.author
            server_id = [server_id for server_id in self.games.keys() if player in self.games[server_id].ready_list][0]
            game: Game = self.games[server_id]
        except IndexError:
            return

        if message.author == self.bot.user:
            return

        elif game.playing:
            print(game.phase)
            if message.channel.id in game_channel_list:
                if  message.author.id == game.playerID and game.phase == "SELECTION":
                    if game.game_status['waiting for selection']:
                        game.current_roles = [r.strip() for r in message.content.split(',')]
                        game.current_roles = [' '.join([part.capitalize() for part in r.split(' ')]) for r in game.current_roles]
                        print('Rollen: ' + str(game.current_roles))
                        if not correct_roles(game, self.role_list):
                            await message.channel.send('Da stimmt etwas nicht. Gib ' + str(len(game.ready_list)) + ' Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Vergiss die Werwölfe nicht!')
                        else:
                            await message.channel.send('Die Rollen sind also ```\n' + '\n'.join(game.current_roles) + '\n```Ist das so richtig?')
                            game.game_status['waiting for selection'] = False
                            game.game_status['selecting'] = True
                    elif game.game_status['selecting']:
                        if message.content.lower().strip() == 'ja':
                            await message.channel.send('Okay, dann verteile ich jetzt die Rollen.')
                            # Schicke Rolle an jeden Spieler einzeln, nachdem die Rollen verteilt wurden
                            await distribute_roles(game, self.ww_roles)
                        elif message.content.lower().strip() == 'nein':
                            await message.channel.send('Gib die Rollen noch einmal ein. Trenne mit einem Komma.')
                            game.game_status['waiting for selection'] = True
                            game.game_status['selecting'] = False
                elif message.author == get_player(game, 'Jäger') and (game.phase == "HUNTER_NIGHT" or game.phase == "HUNTER_VOTE"):
                    await choosing_hunter(game, message)
                elif game.phase == "VOTING":
                    await voting(game, message)

            if isinstance(message.channel, discord.DMChannel):
                print(game)
                if message.author == get_player(game, 'Dieb') and game.phase == "THIEF":
                    await choosing_thief(game, message, self.ww_roles)
                elif message.author == get_player(game, 'Amor') and game.phase == "AMOR":
                    await choosing_amor(game, message)
                elif message.author == get_player(game, 'Wildes Kind') and game.phase == "WILD CHILD":
                    await choosing_wild_child(game, message)
                elif message.author == get_player(game, 'Heiler') and game.phase == "HEALER":
                    await choosing_healer(game, message)
                elif message.author == get_player(game, 'Seherin') and game.phase == "SEER":
                    await choosing_seer(game, message)
                elif message.author == get_player(game, 'Stotternder Richter') and game.phase == "VOTING" and 'ABSTIMMUNG' in message.content:
                    if game.player_list[message.author]['new vote']:
                        game.new_vote = True
                        game.player_list[message.author]['new vote'] = 0
                        await message.author.send('Okay, es wird eine zweite Abstimmung geben.')
                #Werewolves
                elif message.author == get_player(game, 'Weißer Werwolf') and game.phase == "WHITE_WEREWOLF":
                    await choosing_white_werewolf(game, message)
                elif message.author == get_player(game, 'Hexe'):
                    if game.phase == "WITCH_HEAL":
                        await choosing_witch_heal(game, message)
                    elif game.phase == "WITCH_DEATH":
                        await choosing_witch_kill(game, message)
            elif message.channel.id == game.werewolf_channel:
                if is_bad(game, message.author.id):
                    if game.phase == "WEREWOLVES":
                        await choosing_werewolves(game, message)
                    elif game.phase == "WEREWOLVES_VALIDATING":
                        await confirming_werewolves(game, message)
            


def setup(bot):
    bot.add_cog(Werwolf(bot))
