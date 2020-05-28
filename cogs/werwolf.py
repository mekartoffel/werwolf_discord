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
        self.round_no = 3


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
        game.current_roles = ['Heiler', 'Hexe', 'Seherin']
        game.ready_list.append(ctx.message.author)
        game.playing = True
        for i in range(len(game.current_roles) - 2):
            role = game.current_roles[i] = ' '.join([part.capitalize() for part in game.current_roles[i].split(' ')])
            role_info = self.ww_roles[role].copy()
            role_info['role'] = role

            game.player_list[ctx.message.author] = role_info
            del game.player_list[ctx.message.author]['wake up']
            del game.player_list[ctx.message.author]['description']
            print(game)
        await wake_healer(game)

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
            await ctx.send(WHICH_ROLES.format(role_list=', '.join(self.role_list)))


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
            await ctx.send(READY.format(player=ctx.message.author.mention))
        elif game.playing:
            await ctx.send(ALREADY_PLAYING)
        elif ctx.message.author in game.ready_list:
            await ctx.send(ALREADY_READY)
        else:
            await ctx.send(ALREADY_SOMEWHERE)


    @commands.command(pass_context=True,
                      hidden=True,
                      description='Bereit für Werwolf.',
                      brief='Bereit für Werwolf.')
    @commands.check(is_game_channel)
    async def bereit(self, ctx):
        await self.ready.invoke(ctx)


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
            await ctx.send(NOT_READY.format(player=ctx.message.author.mention))
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
            await ctx.send(WHOS_READY.format(players='\n'.join([player.mention for player in game.ready_list])))
        else:
            await ctx.send(NO_ONE_READY)


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
            await ctx.send(READY.format(player=player.mention))
        if len(game.ready_list) >= self.PLAYER_MIN and not game.playing:
            # Starte das Spiel nur, wenn genügend Spieler bereit sind
            other_players = ''
            for s in game.ready_list:
                other_players = other_players + '\n' + s.mention
            game.playerID = player.id
            print(still_alive(game))
            await ctx.send(GAME_STARTED.format(player=player.mention, other_players=other_players))
            await ctx.send(WAITING_FOR_ROLES.format(player=player.mention, number_players=str(len(game.ready_list))))
            game.playing = True
            game.game_status['waiting for selection'] = True
            game.phase = 'SELECTION'
        elif game.playing:
            await ctx.send(ALREADY_PLAYING)
        else:
            await ctx.send(NOT_ENOUGH_PLAYERS.format(missing=str(self.PLAYER_MIN - len(game.ready_list))))


    @commands.command(pass_context=True,
                      description='Liste von Spielern, die noch am Leben sind.',
                      brief='Liste von Spielern, die noch am Leben sind.')
    @commands.check(is_game_channel_or_dm)
    async def alive(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if game.playing:
            await ctx.send(STILL_ALIVE.format(alive='\n'.join([player.mention for player in game.player_list if is_alive(game, player.id)])))
        else:
            await ctx.send(NO_INFO)


    @commands.command(pass_context=True,
                      description='Liste von Spielern, die noch nicht abgestimmt haben.',
                      brief='Liste von Spielern, die noch nicht abgestimmt haben.')
    @commands.check(is_game_channel)
    async def missing_vote(self, ctx):
        game: Game = self.games[ctx.guild.id]
        if game.playing and game.phase == 'VOTING':
            await ctx.send(MISSING_VOTES.format(players='\n'.join([player.mention for player in game.player_list if is_alive(game, player.id) and not game.player_list[player]['voted for']])))
        elif not game.playing:
            await ctx.send(NO_INFO)
        else:
            await ctx.send(NOT_VOTING)


    @commands.command(pass_context=True,
                      description='Liste von Spielern, die noch nicht abgestimmt haben.',
                      brief='Liste von Spielern, die noch nicht abgestimmt haben.')
    @commands.check(is_game_channel)
    async def missing_votes(self, ctx):
        await self.missing_vote.invoke(ctx)


    @commands.command(pass_context=True,
                      description='Liste von Spielern und wie viele Leute schon gegen sie gestimmt haben.',
                      brief='Wer hat schon wie viele Stimmen?')
    @commands.check(is_game_channel)
    async def votes(self, ctx):
        game: Game = self.games[ctx.guild.id]
        candidates = []
        for c, v in game.player_list.items():
            candidates.append(v['voted for'])
        count_cand = {k: v for k, v in sorted(dict(Counter(candidates)).items(), key=lambda item: item[1], reverse=True)}
        await self.bot.get_channel(game.game_channel).send(VOTED.format(votes='\n'.join([u.mention + ': ' + str(c) for u, c in count_cand.items() if u])))


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
                        if message.content.startswith('?'):
                            pass
                        elif not correct_roles(game, self.role_list):
                            await message.channel.send(SOMETHING_WRONG.format(player=message.author.mention,number_players=str(len(game.ready_list))))
                        else:
                            await message.channel.send(ROLES.format(roles='\n'.join(game.current_roles)))
                            game.game_status['waiting for selection'] = False
                            game.game_status['selecting'] = True
                    elif game.game_status['selecting']:
                        if message.content.lower().strip() == 'ja':
                            await message.channel.send(DISTRIBUTING_ROLES)
                            # Schicke Rolle an jeden Spieler einzeln, nachdem die Rollen verteilt wurden
                            await distribute_roles(game, self.ww_roles)
                        elif message.content.lower().strip() == 'nein':
                            await message.channel.send(ROLES_AGAIN)
                            game.game_status['waiting for selection'] = True
                            game.game_status['selecting'] = False
                elif message.author == get_player(game, HUNTER_ROLE) and (game.phase == HUNTER_PHASE_NIGHT or game.phase == HUNTER_PHASE_VOTE):
                    await choosing_hunter(game, message)
                elif game.phase == VOTING_PHASE:
                    await voting(game, message)

            if isinstance(message.channel, discord.DMChannel):
                print(game)
                if message.author == get_player(game, THIEF_ROLE) and game.phase == THIEF_PHASE:
                    await choosing_thief(game, message, self.ww_roles)
                elif message.author == get_player(game, CUPID_ROLE) and game.phase == CUPID_PHASE:
                    await choosing_cupid(game, message)
                elif message.author == get_player(game, WILD_CHILD_ROLE) and game.phase == WILD_CHILD_PHASE:
                    await choosing_wild_child(game, message)
                elif message.author == get_player(game, HEALER_ROLE) and game.phase == HEALER_PHASE:
                    await choosing_healer(game, message)
                elif message.author == get_player(game, SEER_ROLE) and game.phase == SEER_PHASE:
                    await choosing_seer(game, message)
                elif message.author == get_player(game, JUDGE_ROLE) and game.phase == VOTING_PHASE and 'ABSTIMMUNG' in message.content:
                    if game.player_list[message.author]['new vote']:
                        game.new_vote = True
                        game.player_list[message.author]['new vote'] = 0
                        await message.author.send(NEW_VOTE_ANSWER)
                #Werewolves
                elif message.author == get_player(game, WHITE_WEREWOLF_ROLE) and game.phase == WHITE_WEREWOLF_PHASE:
                    await choosing_white_werewolf(game, message)
                elif message.author == get_player(game, WITCH_ROLE):
                    if game.phase == WITCH_PHASE_HEAL:
                        await choosing_witch_heal(game, message)
                    elif game.phase == WITCH_PHASE_KILL:
                        await choosing_witch_kill(game, message)
            elif message.channel.id == game.werewolf_channel:
                if is_bad(game, message.author.id):
                    if game.phase == WEREWOLVES_PHASE:
                        await choosing_werewolves(game, message)
                    elif game.phase == WEREWOLVES_PHASE_CONFIRM:
                        await confirming_werewolves(game, message)
            


def setup(bot):
    bot.add_cog(Werwolf(bot))
