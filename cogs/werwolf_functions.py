from random import shuffle
from private import *
from my_constants import *
from collections import Counter

import time
import random
import discord

def is_game_channel(ctx):
    """Check if channel of context is the channel where you can play.

    Keyword arguments:
    ctx -- Context
    """
    return ctx.message.channel.id in game_channel_list

async def distribute_roles(s):
    """Distribute roles and start the game.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    shuffle(s.current_roles)
    for i, player in enumerate(s.ready_list):
        role = s.current_roles[i] = ' '.join(map(lambda part: part.capitalize(), s.current_roles[i].split(' ')))
        role_info = s.ww_roles[role]
        role_info['role'] = role

        s.player_list[player] = role_info
        del s.player_list[player]['wake up']
        del s.player_list[player]['description']
        if not s.player_list[player]['good']:
            await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).set_permissions(player, read_messages=True, send_messages=True)
            await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Willkommen!\nIhr seid für diese Runde die Werwölfe. Hier ist Raum für euch zum Diskutieren.')
        await player.send('Du hast folgende Rolle: ' + role)
    print(s.player_list)
    await first_night(s)


def correct_roles(s):
    """Check if the roles can be mapped to the roles in `werwolf_rollen.json`. If there is no werewolf then the function returns `False`. Also checks if there are enough roles.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    roles = list(map(lambda role: role.lower(), s.current_roles))
    if 'werwolf' not in roles:
        return False
    elif False in list(map(lambda role: role in list(map(lambda role: role.lower(), s.role_list)), roles)):
        return False
    if 'dieb' in roles:
        return len(roles) == len(s.ready_list) +2
    else:
        return len(roles) == len(s.ready_list)

def in_playerlist(s, lst):
    """Check if the players in the list are all players in the player list.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    lst -- list of players
    """
    for player in lst:
        if player not in s.player_list.keys():
            return False
    return True


def get_player(s, role):
    """Gets the player with the given role.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    role -- role whose player is to be found
    """
    for key in s.player_list.keys():
        if s.player_list[key]['role'] == role:
            return key
    return -1

def get_role(s, player_id):
    """Gets the role of a given player ID.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    player_id -- player's ID
    """
    return s.player_list[s.bot.get_user(player_id)]['role']

def get_player_by_name(s, player_name):
    """Get Member object by given player name.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    player_name -- player's name
    """
    player = discord.utils.find(lambda m: player_name.lower() in m.name.lower() , s.bot.get_guild(TEST_SERVER_ID).members)
    if not player:
        player = discord.utils.find(lambda m: player_name.lower() in m.name.lower() , s.bot.get_guild(TEST_SERVER_ID).members)
    return player

def is_alive(s, player_id):
    """Check if the given player is alive.

    Keyword arguments:
    s -- self of the calling class; to pass class vars

    player_id -- player's ID
    """
    return s.player_list[s.bot.get_user(player_id)]['alive']

def is_bad(s, player_id):
    """Check if the given player is bad.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    player_id -- player's ID
    """
    return not s.player_list[s.bot.get_user(player_id)]['good']

def werewolves_chosen(s):
    """Check if all the werewolves have chosen a victim.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    for p in s.player_list:
        if not p['good']:
            if p['citizen'] == "":
                return False
    return True


async def first_night(s):
    """Start the first night of the game. Special characters have to wake up in the first night. If there are no special characters for the first night in the game then just start the 'normal' night.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Die Nacht legt sich still über euer Dorf. Alle Dorfbewohner begeben sich zur Ruhe und schließen die Augen.')
    #Nur einer wird geweckt; wenn keiner in diesem Spiel vertreten ist, dann ist die erste Nacht "irrelevant"
    if 'Dieb' in s.current_roles:
        await wake_thief(s)
    elif 'Amor' in s.current_roles:
        await wake_amor(s)
    elif 'Wildes Kind' in s.current_roles:
        await wake_wild_child(s)
    else:
        await standard_night(s)

async def standard_night(s):
    """Start the standard night of the game.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    print('standard night')
    if 'Heiler' in s.current_roles:
        await wake_healer(s)
    elif 'Seherin' in s.current_roles:
        await wake_seer(s)
    else:
        await wake_werewolves(s)


async def wake_thief(s):
    """Wake up the thief. If there is no thief in the game but in the rest of the chosen character roles then pretend as if there is a thief.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Der Dieb wacht auf. Er ist sehr unzufrieden mit sich selbst und möchte sich deshalb eine der übrigen Identitäten stehlen.')
    if 'Dieb' in s.current_roles[-2:]:
        #Thief is not assigned to any player
        #Sleep so that nobody will notice that there's no thief
        time.sleep(random.randint(40, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(THIEF_FINISHED)
        if 'Amor' in s.current_roles:
            await wake_amor(s)
        elif 'Wildes Kind' in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await get_player(s,'Dieb').send('Du hast folgende Rollen zur Auswahl: ' + ', '.join(s.current_roles[-2:]))
        s.phase = "THIEF"
        # Warte auf Antwort vom Dieb

async def choosing_thief(s, msg):
    for role in s.current_roles[-2:]:
        if msg.content.lower().strip() == role.lower():
            s.player_list[msg.author]['role'] = role
            role_index = s.current_roles.index(role)
            s.current_roles[s.current_roles.index('Dieb')] = role
            s.current_roles[role_index] = 'Dieb'
            print(s.current_roles)
            role_info = s.ww_roles[role]
            role_info['role'] = role
            s.player_list[msg.author] = role_info
            del s.player_list[msg.author]['wake up']
            del s.player_list[msg.author]['good']
            del s.player_list[msg.author]['description']
            print(s.player_list)
            await msg.author.send('Okay, du hast nun folgende Identität: ' + role)
            await s.bot.get_channel(GAME_TEST_CHANNEL).send(THIEF_FINISHED)
            if 'Amor' in s.current_roles:
                await wake_amor(s)
            elif 'Wildes Kind' in s.current_roles:
                await wake_wild_child(s)
            else:
                await standard_night(s)
            return
    await msg.author.send('Das war keine der zur Wahl stehenden Identitäten. Bitte wähle noch einmal.')

async def wake_amor(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Amor wacht auf. Er hat auf einmal große Lust, zwei Leute mit seinen Liebespfeilen abzuschießen.')
    if 'Amor' in s.current_roles[-2:]:
        # Amor is not assigned to any player
        # Sleep so that nobody will notice that there's no amor
        time.sleep(random.randint(30, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(AMOR_FINISHED)
        if 'Wildes Kind' in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await get_player(s, 'Amor').send(AMOR_INPUT)
        s.phase = "AMOR"
        # Warte auf Antwort vom Amor

async def choosing_amor(s, msg):
    chosen = list(map(lambda p: get_player_by_name(s, p.strip()), msg.content.split(',')))
    if len(chosen) >= 2 and in_playerlist(s, chosen):
        s.player_list[msg.author]['loving'] = list(map(lambda n: get_player_by_name(s, n), chosen[:2]))
        await msg.author.send('Okay, die beiden sind nun verliebt: ' + ' und '.join(list(map(lambda user: user.mention, s.player_list[msg.author]['loving']))))
        lover1 = s.player_list[msg.author]['loving'][0]
        lover2 = s.player_list[msg.author]['loving'][1]
        await lover1.send('Du bist jetzt verliebt in ' + lover2.mention + ' ' + discord.utils.get(s.bot.emojis, id=524903179574575124))
        await lover2.send('Du bist jetzt verliebt in ' + lover1.mention + ' ' + discord.utils.get(s.bot.emojis, id=524903179574575124))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(AMOR_FINISHED)
        if 'Wildes Kind' in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await msg.author.send(NOT_UNDERSTAND + AMOR_INPUT)

async def wake_wild_child(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Das wilde Kind wacht auf. Es sucht sich ein Vorbild. Wenn dieses stirbt, kehrt das wilde Kind zurück zu den Werwölfen und wird deren Verbündeter.')
    if 'Wildes Kind' in s.current_roles[-2:]:
        # Wild child is not assigned to any player
        # Sleep so that nobody will notice that there's no wild child
        time.sleep(random.randint(30, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WILD_CHILD_FINISHED)
        await standard_night(s)
    else:
        await get_player(s, 'Wildes Kind').send(WILD_CHILD_INPUT)
        s.phase = "WILD CHILD"
        # Warte auf Antwort vom wildem Kind

async def choosing_wild_child(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in list(map(lambda p: p, s.player_list.keys())) and chosen.id != msg.author.id:
        s.player_list[msg.author]['role model'] = chosen
        await msg.author.send('Okay, diese Person ist nun dein Vorbild: ' + s.player_list[msg.author]['role model'].mention)
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WILD_CHILD_FINISHED)
        await standard_night(s)
    else:
        await msg.author.send(NOT_UNDERSTAND + WILD_CHILD_INPUT)

async def wake_healer(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Der Heiler erwacht. Er möchte diese Nacht jemanden beschützen.')
    if 'Heiler' in s.current_roles[-2:]:
        # Healer is not assigned to any player
        # Sleep so that nobody will notice that there's no healer
        time.sleep(random.randint(25, 85))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(HEALER_FINISHED)
        if 'Seherin' in s.current_roles and is_alive(get_player(s, 'Seherin').id):
            await wake_seer(s)
        else:
            await wake_werewolves(s)
    elif not is_alive(s, get_player(s, 'Heiler').id):
        # Healer is already dead
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(25, 85))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(SEER_FINISHED)
        if 'Seherin' in s.current_roles and is_alive(get_player(s, 'Seherin').id):
            await wake_seer(s)
        else:
            await wake_werewolves(s)
    else:
        await get_player(s, 'Heiler').send(HEALER_INPUT)
        s.phase = "HEALER"
        # Warte auf Antwort vom Heiler

async def choosing_healer(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys():
        if is_alive(s, chosen.id):
            s.player_list[msg.author]['chosen'] = chosen
            await msg.author.send('Okay, diese Person beschützt du heute Nacht: ' + s.player_list[msg.author]['chosen'].mention)
            await s.bot.get_channel(GAME_TEST_CHANNEL).send(HEALER_FINISHED)
            if 'Seherin' in s.current_roles:
                await wake_seer(s)
            else:
                await wake_werewolves(s)
        else:
            await msg.author.send( NOT_ALIVE + HEALER_INPUT )
    else:
        await msg.author.send(NOT_UNDERSTAND + HEALER_INPUT)

async def wake_seer(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Die Seherin wacht auf. Sie verdächtigt jemanden und möchte deshalb die Identität dieser Person in Erfahrung bringen.')
    if 'Seherin' in s.current_roles[-2:]:
        # Seer is not assigned to any player
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(25, 85))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(SEER_FINISHED)
        await wake_werewolves(s)
    elif not is_alive(s, get_player(s, 'Seherin').id):
        # Seer is already dead
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(25, 85))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(SEER_FINISHED)
        await wake_werewolves(s)
    else:
        await get_player(s, 'Seherin').send(SEER_INPUT)
        s.phase = "SEER"
        # Warte auf Antwort von der Seherin

async def choose_seer(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        if is_alive(s, chosen.id):
            checked_person = chosen
            await msg.author.send(s.player_list[checked_person].mention + ' hat folgende Identität: ' + s.player_list[checked_person]['role'])
            await s.bot.get_channel(GAME_TEST_CHANNEL).send(SEER_FINISHED)
            await wake_werewolves(s)
        else:
            await msg.author.send(NOT_ALIVE + SEER_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + SEER_INPUT)

async def wake_werewolves(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Die Werwölfe wachen auf und haben richtig Hunger. Sie müssen sich nur noch einigen, wen sie diese Nacht fressen wollen.')
    await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Welche Person möchtet ihr fressen? (Taggt die Person alle bitte mit einem @)')
    s.phase = "WEREWOLVES"
    # Warte auf Antwort von den Werwölfen

async def choose_werewolves(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys():
        if not is_bad(s, chosen.id) and is_alive(s, chosen.id):
            s.player_list[msg.author]['citizen'] = chosen.id
            await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send(msg.author.mention + ' möchte folgende Person fressen: ' + s.player_list[msg.author]['citizen'].mention)
            if werewolves_chosen(s):
                citizens = []
                for p in s.player_list:
                    if not p['good']:
                        citizens.append(p['citizen'])
                s.died[0] = max(dict(Counter(citizens)).items(), key=operator.itemgetter(1))[0]
                await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Wollt ihr folgende Person fressen: ' + s.died[0].mention + '? (Es reicht, wenn einer von euch \"Ja\" bzw. \"Nein\" antwortet, sprecht euch also ab!))')
                s.phase = "WEREWOLVES_VALIDATING"
        else:
            await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send(msg.author.mention + ' Diesen Spieler kannst du nicht wählen.')
    # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich

async def validating_werewolves(s, msg):
    if msg.content.lower().strip() == 'ja':
        await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Ihr habt folgende Person gefressen: ' + s.died[0].mention)
        await s.bot.get_channel(GAME_TEST_CHANNEL).send( WEREWOLVES_FINISHED )
        if 'Weißer Werwolf' in s.current_roles and is_alive(s, get_player(s, 'Weißer Werwolf').id) and (s.round_no % 2 == 0):
            await wake_white_werewolf(s)
        elif 'Hexe' in s.current_roles and is_alive(s, get_player(s, 'Hexe').id):
            await wake_witch(s)
        else:
            await daytime(s)
    elif msg.content.lower().strip() == 'nein':
        await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Okay, wen möchtet ihr fressen? (Nur, wer seine Meinung ändert, sollte nochmal seine Stimme ändern.)')
        s.phase = "WEREWOLVES"
    # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich

async def wake_white_werewolf(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Der weiße Werwolf erwacht. Er möchte eventuell einen seiner Werwolf-Kameraden fressen.')
    if 'Weißer Werwolf' in s.current_roles[-2:]:
        # Seer is not assigned to any player
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(25, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        await standard_night(s)
    else:
        await get_player(s, 'Weißer Werwolf').send(WHITE_WEREWOLF_INPUT)
        s.phase = "WHITE_WEREWOLF"
        # Warte auf Antwort vom weißen Werwolf

async def choose_white_werewolf(s, msg):
    if msg.content.lower().split() == 'niemanden':
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        return

    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)        
    if chosen in s.player_list.keys() and chosen != msg.author:
        if is_alive(s, chosen.id) and is_bad(s, chosen.id):
            comrade = chosen
            await msg.author.send('Du hast folgende Person gefressen' + s.player_list[comrade].mention)
            s.died[1] = comrade
            await s.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
            if 'Hexe' in s.current_roles and is_alive(s, get_player(s, 'Hexe').id):
                await wake_witch(s)
            else:
                await daytime(s)
        elif not is_bad(s, chosen.id):
            await msg.author.send('Die Person ist keiner deiner Kameraden...\n' + WHITE_WEREWOLF_INPUT)
        elif not is_alive(s, chosen.id):
            await msg.author.send( NOT_ALIVE + WHITE_WEREWOLF_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + WHITE_WEREWOLF_INPUT)

async def wake_witch(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Die Hexe wacht durch die Geräusche auf, die die Werwölfe verursacht haben. Sie sieht sich im Dorf um.')
    if 'Hexe' in s.current_roles[-2:] or len(s.player_list[get_player(s, 'Hexe')]['tranks']) <= 0:
        # Seer is not assigned to any player
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(45, 150))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WITCH_FINISHED)
        await standard_night(s)
    else:
        await get_player(s, 'Hexe').send(s.died[0].mention() + WITCH_INPUT_HEAL)
        s.phase = "WITCH_HEAL"
        # Warte auf Antwort von der Hexe

async def choose_witch_heal(s, msg):
    if msg.content.lower().strip() == 'ja':
        del s.player_list[get_player(s, 'Hexe')]['tranks'][s.player_list[get_player(s, 'Hexe')]['tranks'].index('Heiltrank')]
        await msg.author.send(s.died[0].mention + ' wurde von dir gerettet!')
        s.died[0] = None
    elif msg.content.lower().strip() == 'nein':
        await msg.author.send(s.died[0].mention + ' wurde nicht von dir gerettet.')
    else:
        await msg.author.send(NOT_UNDERSTAND + s.died[0].mention + WITCH_INPUT_HEAL)
        return
    s.phase = "WITCH_DEATH"
    await msg.author.send(WITCH_INPUT_KILL)

async def choose_witch_kill(s, msg):
    if msg.content.lower().split() == 'niemanden':
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        return

    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author and is_alive(s, chosen.id):
        del s.player_list[get_player(s, 'Hexe')]['tranks'][s.player_list[get_player(s, 'Hexe')]['tranks'].index('Gifttrank')]
        killed_person = chosen
        await msg.author.send('Du hast folgende Person vergiftet: ' + s.player_list[killed_person].mention)
        s.died[2] = killed_person
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WITCH_FINISHED)
        await daytime(s)
    elif not is_alive(s, chosen.id):
        await msg.author.send(NOT_ALIVE + WITCH_INPUT_KILL)
    else:
        await msg.author.send( NOT_UNDERSTAND + WITCH_INPUT_KILL)

async def daytime(s):
    return 0
    s.round_no += 1