from random import shuffle
from private import *
from my_constants import *

import time
import random

def is_game_channel(ctx):
    return ctx.message.channel.id in game_channel_list

async def distribute_roles(s):
    shuffle(s.current_roles)
    for i, player in enumerate(s.ready_list):
        role = s.current_roles[i] = ' '.join(map(lambda part: part.capitalize(), s.current_roles[i].split(' ')))
        role_info = s.ww_roles[role]
        role_info['role'] = role

        s.player_list[player] = role_info
        del s.player_list[player]['wake up']
        del s.player_list[player]['good']
        del s.player_list[player]['description']
        if not s.player_list[player]['good']:
            await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).set_permissions(player, read_messages=True, send_messages=True)
            await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Willkommen!\nIhr seid für diese Runde die Werwölfe. Hier ist Raum für euch zum Diskutieren.')
        await player.send('Du hast folgende Rolle: ' + role)
    print(s.player_list)


def correct_roles(s):
    roles = list(map(lambda role: role.lower(), s.current_roles))
    if 'werwolf' not in roles:
        return False
    elif False in list(map(lambda role: role in list(map(lambda role: role.lower(), s.role_list)), roles)):
        return False
    if 'dieb' in roles:
        return len(roles) == len(s.ready_list) +2
    else:
        return len(roles) == len(s.ready_list)

def correct_ids(s, lst):
    for id in lst:
        if id not in map(lambda p: p.id, s.player_list.keys()):
            return False
    return True


def get_player(s, role):
    '''Get a player with the given role'''
    for key in s.player_list.keys():
        if s.player_list[key]['role'] == role:
            return key
    return -1

def get_role(s, player_id):
    return s.player_list[s.bot.get_user(player_id)]['role']

def is_alive(s, player_id):
    return s.player_list[s.bot.get_user(player_id)]['alive']

def is_bad(s, player_id):
    return not s.player_list[s.bot.get_user(player_id)]['good']

def werewolves_chosen(s):
    for p in s.player_list:
        if not p['good']:
            if p['citizen'] == "":
                return False
    return True


async def first_night(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Die Nacht legt sich still über euer Dorf. Alle Dorfbewohner begeben sich zur Ruhe und schließen die Augen.')
    #Nur einer wird geweckt; wenn keiner in diesem Spiel vertreten ist, dann ist die erste Nacht "irrelevant"
    if 'Dieb' in s.current_roles:
        await thief(s)
    elif 'Amor' in s.current_roles:
        await amor(s)
    elif 'Wildes Kind' in s.current_roles:
        await wild_child(s)
    else:
        await play_game(s)

async def play_game(s):
    print('play game')
    if 'Heiler' in s.current_roles and is_alive(get_player(s, 'Heiler').id):
        await healer(s)
    elif 'Seherin' in s.current_roles and is_alive(get_player(s, 'Seherin').id):
        await seer(s)
    else:
        await werewolves(s)


async def thief(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Der Dieb wacht auf. Er ist sehr unzufrieden mit sich selbst und möchte sich deshalb eine der übrigen Identitäten stehlen.')
    if 'Dieb' in s.current_roles[-2:]:
        #Thief is not assigned to any player
        #Sleep so that nobody will notice that there's no thief
        time.sleep(random.randint(40, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(THIEF_FINISHED)
        if 'Amor' in s.current_roles:
            await amor(s)
        elif 'Wildes Kind' in s.current_roles:
            await wild_child(s)
        else:
            await play_game(s)
    else:
        await get_player(s,'Dieb').send('Du hast folgende Rollen zur Auswahl: ' + ', '.join(s.current_roles[-2:]))
        s.phase = "THIEF"
        # Warte auf Antwort vom Dieb

async def amor(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send('Amor wacht auf. Er hat auf einmal große Lust, zwei Leute mit seinen Liebespfeilen abzuschießen.')
    if 'Amor' in s.current_roles[-2:]:
        # Amor is not assigned to any player
        # Sleep so that nobody will notice that there's no amor
        time.sleep(random.randint(30, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(AMOR_FINISHED)
        if 'Wildes Kind' in s.current_roles:
            await wild_child(s)
        else:
            await play_game(s)
    else:
        await get_player(s, 'Amor').send(AMOR_INPUT)
        s.phase = "AMOR"
        # Warte auf Antwort vom Amor

async def wild_child(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Das wilde Kind wacht auf. Es sucht sich ein Vorbild. Wenn dieses stirbt, kehrt das wilde Kind zurück zu den Werwölfen und wird deren Verbündeter.')
    if 'Wildes Kind' in s.current_roles[-2:]:
        # Wild child is not assigned to any player
        # Sleep so that nobody will notice that there's no wild child
        time.sleep(random.randint(30, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WILD_CHILD_FINISHED)
        await play_game(s)
    else:
        await get_player(s, 'Wildes Kind').send(WILD_CHILD_INPUT)
        s.phase = "WILD CHILD"
        # Warte auf Antwort vom wildem Kind

async def healer(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Der Heiler erwacht. Er möchte diese Nacht jemanden beschützen.')
    if 'Heiler' in s.current_roles[-2:]:
        # Healer is not assigned to any player
        # Sleep so that nobody will notice that there's no healer
        time.sleep(random.randint(25, 85))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(HEALER_FINISHED)
        await play_game(s)
    else:
        await get_player(s, 'Heiler').send(HEALER_INPUT)
        s.phase = "HEALER"
        # Warte auf Antwort vom Heiler

async def seer(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Die Seherin wacht auf. Sie verdächtigt jemanden und möchte deshalb die Identität dieser Person in Erfahrung bringen.')
    if 'Seherin' in s.current_roles[-2:]:
        # Seer is not assigned to any player
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(25, 85))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(SEER_FINISHED)
        await play_game(s)
    else:
        await get_player(s, 'Seherin').send(SEER_INPUT)
        s.phase = "SEER"
        # Warte auf Antwort von der Seherin

async def werewolves(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Die Werwölfe wachen auf und haben richtig Hunger. Sie müssen sich nur noch einigen, wen sie diese Nacht fressen wollen.')
    await s.bot.get_channel(WERWOELFE_TEST_CHANNEL).send('Welche Person möchtet ihr fressen? (Taggt die Person alle bitte mit einem @)')
    s.phase = "WEREWOLVES"
    # Warte auf Antwort von den Werwölfen

async def white_werewolf(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Der weiße Werwolf erwacht. Er möchte eventuell einen seiner Werwolf-Kameraden fressen.')
    if 'Weißer Werwolf' in s.current_roles[-2:]:
        # Seer is not assigned to any player
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(25, 120))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        await play_game(s)
    else:
        await get_player(s, 'Weißer Werwolf').send(WHITE_WEREWOLF_INPUT)
        s.phase = "WHITE_WEREWOLF"
        # Warte auf Antwort vom weißen Werwolf

async def witch(s):
    await s.bot.get_channel(GAME_TEST_CHANNEL).send(
        'Die Hexe wacht durch die Geräusche auf, die die Werwölfe verursacht haben. Sie sieht sich im Dorf um.')
    if 'Hexe' in s.current_roles[-2:] or len(s.player_list[get_player(s, 'Hexe')]['tranks']) <= 0:
        # Seer is not assigned to any player
        # Sleep so that nobody will notice that there's no seer
        time.sleep(random.randint(45, 150))
        await s.bot.get_channel(GAME_TEST_CHANNEL).send(WITCH_FINISHED)
        await play_game(s)
    else:
        await get_player(s, 'Hexe').send(s.died[0].mention() + WITCH_INPUT_HEAL)
        s.phase = "WITCH_HEAL"
        # Warte auf Antwort von der Hexe

async def daytime(s):
    return 0
    s.round_no += 1