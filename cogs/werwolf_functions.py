from random import shuffle
from private import *
from my_constants import *
from collections import Counter
from typing import Dict

import operator
import random
import discord
import asyncio
import re

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
    werewolves = []
    shuffle(s.current_roles)
    for i, player in enumerate(s.ready_list):
        role = s.current_roles[i]# = ' '.join(map(lambda part: part.capitalize(), s.current_roles[i].split(' ')))
        role_info = s.ww_roles[role].copy()
        role_info['role'] = role

        s.player_list[player] = role_info
        print(s.player_list[player])
        del s.player_list[player]['wake up']
        del s.player_list[player]['description']

        await player.send('Du hast folgende Rolle: ' + role)
        if not s.player_list[player]['good']:
            werewolves.append(player)
            await player.send('Es wurde ein neuer Kanal für dich und die anderen Werwölfe freigeschalten: <#' + str(PLAYING_WEREWOLVES_CHANNEL) + '>')
            await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).set_permissions(player, read_messages=True, send_messages=True)
    await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send('Willkommen!\n' + ' '.join([w.mention for w in werewolves]) + ', ihr seid für diese Runde die Werwölfe. Hier ist Raum für euch zum Diskutieren.')
    print(s.player_list)
    await first_night(s)


def correct_roles(s):
    """Check if the roles can be mapped to the roles in `werwolf_rollen.json`. If there is no werewolf then the function returns `False`. Also checks if there are enough roles.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    roles = [role.lower().strip() for role in s.current_roles]
    if 'werwolf' not in roles:
        print('kein werwolf')
        return False
    elif False in [r in [role.lower() for role in s.role_list] for r in roles]:
        print('kein richtiger')
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

def get_name_discriminator(player):
    return player.name + '#' + player.discriminator

def get_player(s, role):
    """Gets the player with the given role.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    role -- role whose player is to be found
    """
    for key in s.player_list.keys():
        if s.player_list[key]['role'] == role:
            return key
    return None

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
    player = discord.utils.find(lambda m: player_name.lower() in m.name.lower() , s.bot.get_guild(PLAYING_SERVER).members)
    if not player:
        player = discord.utils.find(lambda m: player_name.lower() in m.nick.lower() if m.nick else False, s.bot.get_guild(PLAYING_SERVER).members)
    return player

def is_alive(s, player_id):
    """Check if the given player is alive.

    Keyword arguments:
    s -- self of the calling class; to pass class vars

    player_id -- player's ID
    """
    return s.player_list[s.bot.get_user(player_id)]['alive']

def still_alive(s):
    """Returns a list of players who are still alive.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    return [u for u in s.player_list if s.player_list[u]['alive']]

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
    for p,v in s.player_list.items():
        if not v['good']:
            if not v['citizen']:
                return False
    return True

def citizens_chosen(s):
    """Check if all the citizens have chosen a victim.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    for p,v in s.player_list.items():
        if not v['voted for']:
            idiot = get_player(s, 'Dorfdepp')
            if p == idiot:
                if not s.player_list[idiot]['voting right']:
                    continue
            if not s.player_list[p]['alive']:
                continue
            return False
    return True

def thief_in_game(s):
    return 'Dieb' in s.current_roles


async def first_night(s):
    """Start the first night of the game. Special characters have to wake up in the first night. If there are no special characters for the first night in the game then just start the 'normal' night.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die Nacht legt sich still über euer Dorf. Alle Dorfbewohner begeben sich zur Ruhe und schließen die Augen.')
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
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Der **Dieb** wacht auf. Er ist sehr unzufrieden mit sich selbst und möchte sich deshalb eine der übrigen Identitäten stehlen.')
    if not get_player(s, 'Dieb'):
        # Kein Spieler ist Dieb
        # Sleep, sodass niemand es merkt, dass kein Dieb im Spiel ist
        await asyncio.sleep(random.randint(40, 110))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(THIEF_FINISHED)
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
            print(msg.content)
            role = ' '.join([part.capitalize() for part in role.split(' ')])
            s.player_list[msg.author]['role'] = role
            role_index = s.current_roles.index(role)
            #Tausche die Reihenfolge aus
            s.current_roles[s.current_roles.index('Dieb')] = role
            s.current_roles[role_index] = 'Dieb'
            print(s.current_roles)
            #Weise dem Spieler die neue Rolle zu
            role_info = s.ww_roles[role].copy()
            role_info['role'] = role
            s.player_list[msg.author] = role_info
            del s.player_list[msg.author]['wake up']
            del s.player_list[msg.author]['description']
            print(s.player_list)
            #Phase ist beendet; Entscheidung, was als nächstes passiert
            s.phase = ''
            await msg.author.send('Okay, du hast nun folgende Identität: ' + role)
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(THIEF_FINISHED)
            if 'Amor' in s.current_roles:
                await wake_amor(s)
            elif 'Wildes Kind' in s.current_roles:
                await wake_wild_child(s)
            else:
                await standard_night(s)
            return
    await msg.author.send('Das war keine der zur Wahl stehenden Identitäten. Bitte wähle noch einmal.')

async def wake_amor(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('**Amor** wacht auf. Er hat auf einmal große Lust, zwei Leute mit seinen Liebespfeilen abzuschießen.')
    if not get_player(s, 'Amor'):
        # Kein Spieler ist Amor
        # Sleep, sodass es nicht auffällt, dass kein Amor im Spiel ist
        await asyncio.sleep(random.randint(30, 100))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(AMOR_FINISHED)
        if 'Wildes Kind' in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await get_player(s, 'Amor').send(AMOR_INPUT)
        s.phase = "AMOR"
        # Warte auf Antwort vom Amor

async def choosing_amor(s, msg):
    chosen = [get_player_by_name(s, p.strip()) for p in msg.content.split(',')]
    if len(chosen) >= 2 and in_playerlist(s, chosen):
        # Wer sind die Verliebten?
        s.player_list[msg.author]['loving'] = chosen[:2]
        await msg.author.send('Okay, die beiden sind nun verliebt: ' + ' und '.join([user.mention + ' ({})'.format(get_name_discriminator(user)) for user in s.player_list[msg.author]['loving']]))
        # Die Verliebten informieren
        lover1 = s.player_list[msg.author]['loving'][0]
        lover2 = s.player_list[msg.author]['loving'][1]
        # Phase ist beendet; Entscheidung, was als nächstes passiert
        s.phase = ''
        await lover1.send('Du bist jetzt verliebt in ' + lover2.mention + ' ({}) '.format(get_name_discriminator(lover2)) + str(discord.utils.get(s.bot.emojis, id=524903179574575124)))
        await lover2.send('Du bist jetzt verliebt in ' + lover1.mention + ' ({}) '.format(get_name_discriminator(lover1)) + str(discord.utils.get(s.bot.emojis, id=524903179574575124)))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(AMOR_FINISHED)
        if 'Wildes Kind' in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await msg.author.send(NOT_UNDERSTAND + AMOR_INPUT)

async def wake_wild_child(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Das **wilde Kind** wacht auf. Es sucht sich ein Vorbild. Wenn dieses stirbt, kehrt das wilde Kind zurück zu den Werwölfen und wird deren Verbündeter.')
    if not get_player(s, 'Wildes Kind'):
        # Kein Spieler ist das wilde Kind
        # Sleep, sodass es nicht auffällt, dass kein wildes Kind im Spiel ist
        await asyncio.sleep(random.randint(30, 100))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WILD_CHILD_FINISHED)
        await standard_night(s)
    else:
        await get_player(s, 'Wildes Kind').send(WILD_CHILD_INPUT)
        s.phase = "WILD CHILD"
        # Warte auf Antwort vom wildem Kind

async def choosing_wild_child(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen.id != msg.author.id:
        s.player_list[msg.author]['role model'] = chosen
        # Phase beendet; Die Spezialrollen für die erste Nacht sind fertig.
        s.phase = ''
        await msg.author.send('Okay, diese Person ist nun dein Vorbild: ' + chosen.mention + ' ({})'.format(get_name_discriminator(chosen)))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WILD_CHILD_FINISHED)
        await standard_night(s)
    else:
        await msg.author.send(NOT_UNDERSTAND + WILD_CHILD_INPUT)

async def wake_healer(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Der **Heiler** erwacht. Er hat ein ganz ungutes Gefühl und möchte deshalb diese Nacht jemanden beschützen.')
    if not get_player(s, 'Heiler'):
        # Kein Spieler ist der Heiler
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(25, 75))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(HEALER_FINISHED)
        if 'Seherin' in s.current_roles:
            await wake_seer(s)
        else:
            await wake_werewolves(s)
    elif not is_alive(s, get_player(s, 'Heiler').id):
        # Heiler ist schon tot
        # Sleep, sodass es nicht auffällt, dass er tot ist
        await asyncio.sleep(random.randint(25, 60))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(SEER_FINISHED)
        if 'Seherin' in s.current_roles:
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
        # Wen will er beschützen?
        if is_alive(s, chosen.id):
            # Lebt die Person noch?
            if chosen != s.player_list[msg.author]['chosen']:
                # Wurde die Person in der vorherigen Runde auch schon gewählt?
                s.player_list[msg.author]['chosen'] = chosen
                # Phase beendet; Entscheidung, was als nächstes passiert
                s.phase = ''
                await msg.author.send('Okay, diese Person beschützt du heute Nacht: ' + chosen.mention + ' ({})'.format(get_name_discriminator(chosen)))
                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(HEALER_FINISHED)
                if 'Seherin' in s.current_roles:
                    await wake_seer(s)
                else:
                    await wake_werewolves(s)
            else:
                await msg.author.send('Du kannst nicht zwei Mal hintereinander dieselbe Person schützen. Wähle bitte jemand anderes.')
        else:
            await msg.author.send(NOT_ALIVE + HEALER_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + HEALER_INPUT)

async def wake_seer(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die **Seherin** wacht auf. Sie verdächtigt jemanden und möchte deshalb die Identität dieser Person in Erfahrung bringen.')
    if not get_player(s, 'Seherin'):
        # Kein Spieler ist die Seherin
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(25, 75))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(SEER_FINISHED)
        await wake_werewolves(s)
    elif not is_alive(s, get_player(s, 'Seherin').id):
        # Die Seherin ist schon tot
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(25, 60))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(SEER_FINISHED)
        await wake_werewolves(s)
    else:
        await get_player(s, 'Seherin').send(SEER_INPUT)
        s.phase = "SEER"
        # Warte auf Antwort von der Seherin

async def choosing_seer(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will die Seherin überprüfen?
        if is_alive(s, chosen.id):
            # Lebt die Person noch?
            checked_person = chosen
            # Phase beendet; Werwölfe sind als nächstes dran
            s.phase = ''
            await msg.author.send(checked_person.mention + ' ({})'.format(get_name_discriminator(checked_person)) + ' hat folgende Identität: ' + s.player_list[checked_person]['role'])
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(SEER_FINISHED)
            await wake_werewolves(s)
        else:
            await msg.author.send(NOT_ALIVE + SEER_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + SEER_INPUT)

async def wake_werewolves(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die **Werwölfe** wachen auf und haben richtig Hunger. Sie müssen sich nur noch einigen, wen sie diese Nacht fressen wollen.')
    await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send(WEREWOLVES_INPUT)
    s.phase = "WEREWOLVES"
    # Warte auf Antwort von den Werwölfen

async def choosing_werewolves(s, msg):
    if 'enthaltung' in msg.content.lower():
        s.player_list[msg.author]['citizen'] = {'name': 'Enthaltung', 'discriminator': '0000'}
        await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send(msg.author.mention + ' ist es egal.')
        return
    citizen = get_player_by_name(s, msg.content.strip())
    print(citizen)
    if citizen in s.player_list.keys():
        # Wen wollen die Werwölfe fressen?
        if not is_bad(s, citizen.id) and is_alive(s, citizen.id):
            # Ist diese Person überhaupt ein Dorfbewohner? Und lebt sie noch?
            amor = get_player(s, 'Amor')
            if amor:
                if msg.author in s.player_list[amor]['loving'] and citizen in s.player_list[amor]['loving']:
                    #Wenn ein Werwolf seinen Liebespartner fressen will, halte ihn davon ab
                    await msg.delete()
                    await msg.author.send('Du kannst deinen Liebespartner doch nicht fressen! 💔')
                    return
            s.player_list[msg.author]['citizen'] = citizen
            await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send(msg.author.mention + ' möchte folgende Person fressen: ' + get_name_discriminator(citizen))
            if werewolves_chosen(s):
                # Erst, wenn alle gewählt haben, wird gefragt, ob sie mit der Wahl einverstanden sind.
                citizens = []
                for p,v in s.player_list.items():
                    if not v['good']:
                        citizens.append(v['citizen'])
                s.died[0] = max(dict(Counter(citizens)).items(), key=operator.itemgetter(1))[0]
                await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send('Wollt ihr folgende Person fressen: ' + get_name_discriminator(s.died[0]) + '? (Es reicht, wenn einer von euch \"Ja\" bzw. \"Nein\" antwortet, sprecht euch also ab!)')
                s.phase = "WEREWOLVES_VALIDATING"
        else:
            await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send(msg.author.mention + ', diesen Spieler kannst du nicht wählen.')
    # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich

async def confirming_werewolves(s, msg):
    if msg.content.lower().strip() == 'ja':
        # Phase beendet; Entscheidung, was als nächstes passiert
        s.phase = ''
        # Die Werwölfe haben sich entschieden, die Person zu fressen
        await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send('Ihr habt folgende Person gefressen: ' + get_name_discriminator(s.died[0]))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WEREWOLVES_FINISHED)
        if get_player(s, 'Heiler'):
            # Wenn der Heiler diese Person schützt, wird sie aber nicht sterben
            if s.died[0] == s.player_list[get_player(s, 'Heiler')]['chosen']:
                s.died[0] = None
        for c, v in s.player_list.items():
            if is_alive(s, c.id) and is_bad(s, c.id):
                v['citizen'] = None
        if 'Weißer Werwolf' in s.current_roles and (s.round_no % 2 == 0):
            await wake_white_werewolf(s)
        elif 'Hexe' in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
    elif msg.content.lower().strip() == 'nein':
        await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).send('Okay, wen möchtet ihr fressen? (Nur, wer seine Meinung ändert, sollte nochmal seine Stimme ändern.)')
        s.phase = "WEREWOLVES"
    # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich

async def wake_white_werewolf(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Der **weiße Werwolf** erwacht. Er möchte eventuell einen seiner Werwolf-Kameraden fressen.')
    if not get_player(s, 'Weißer Werwolf'):
        # Kein Spieler ist der weiße Werwolf
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(25, 110))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        if get_player(s, 'Heiler'):
            # Wenn der Heiler diese Person schützt, wird sie aber nicht sterben
            if s.died[1] == s.player_list[get_player(s, 'Heiler')]['chosen']:
                s.died[1] = None
        if 'Hexe' in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
    elif not is_alive(s, get_player(s, 'Weißer Werwolf').id):
        # Der weiße Werwolf ist schon tot
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(25, 100))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        if 'Hexe' in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
    else:
        await get_player(s, 'Weißer Werwolf').send(WHITE_WEREWOLF_INPUT)
        s.phase = "WHITE_WEREWOLF"
        # Warte auf Antwort vom weißen Werwolf

async def choosing_white_werewolf(s, msg):
    if msg.content.lower().strip() == 'niemanden':
        # Wenn der weiße Werwolf niemanden fressen will, dann geht es einfach weiter
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
        return

    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will der weiße Werwolf fressen?
        if is_alive(s, chosen.id) and is_bad(s, chosen.id):
            # Lebt die Person noch? Ist das überhaupt einer seiner Werwolfkameraden?
            amor = get_player(s, 'Amor')
            if amor:
                if msg.author in s.player_list[amor]['loving'] and chosen in s.player_list[amor]['loving']:
                    # Wenn ein Werwolf seinen Liebespartner fressen will, halte ihn davon ab
                    await msg.author.send('Du kannst deinen Liebespartner doch nicht fressen! 💔')
                    return
            comrade = chosen
            # Phase beendet; Entscheidung, was als nächstes passiert
            s.phase = ''
            await msg.author.send('Du hast folgende Person gefressen' + comrade.mention + ' ({})'.format(get_name_discriminator(comrade)))
            s.died[1] = comrade
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WHITE_WEREWOLF_FINISHED)
            if 'Hexe' in s.current_roles:
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
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die **Hexe** wacht durch die Geräusche auf, die die Werwölfe verursacht haben. Sie sieht sich im Dorf um.')
    witch = get_player(s, 'Hexe')
    if not witch:
        # Kein Spieler ist die Hexe
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(45, 110))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WITCH_FINISHED)
        await daytime(s)
    elif not is_alive(s, witch.id):
        # Die Hexe ist schon tot
        # Sleep, sodass es nicht auffällt
        await asyncio.sleep(random.randint(45, 100))
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WITCH_FINISHED)
        await daytime(s)
    else:
        tranks = s.player_list[witch]['tranks']
        if len(tranks) <= 0:
            # Die Hexe hat keine Tränke mehr und kann nichts machen
            await witch.send('Du hast keine Tränke mehr, die du verwenden kannst. (Wir warten jetzt pseudomäßig trotzdem 😈)')
            await asyncio.sleep(random.randint(30, 60))
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WITCH_FINISHED)
            await daytime(s)
        else:
            # Sie hat noch Tränke
            try:
                tranks.index('Heiltrank')
                # Wenn sie noch einen Heiltrank hat, dann soll sie diesen benutzen können
                if s.died[0]:
                    s.phase = "WITCH_HEAL"
                    await witch.send(s.died[0].mention + ' ({}) '.format(get_name_discriminator(s.died[0])) + WITCH_INPUT_HEAL)
                    # Warte auf Antwort von der Hexe
                    return
                else:
                    await witch.send('Es ist niemand gestorben!')
            except ValueError:
                await witch.send('Du hast deinen Heiltrank schon benutzt.')
            try:
                # Wenn sie keinen Heiltrank mehr hat oder niemand gestorben ist, soll sie direkt den Gifttrank benutzen können
                tranks.index('Gifttrank')
                s.phase = "WITCH_DEATH"
                await witch.send(WITCH_INPUT_KILL)
            except ValueError:
                print('Irgendwas ist schief gelaufen bei der Hexe...')


async def choosing_witch_heal(s, msg):
    if msg.content.lower().strip() == 'ja':
        # Sie möchte das Opfer retten
        del s.player_list[get_player(s, 'Hexe')]['tranks'][s.player_list[get_player(s, 'Hexe')]['tranks'].index('Heiltrank')]
        await msg.author.send(s.died[0].mention + ' ({}) '.format(get_name_discriminator(s.died[0])) + ' wurde von dir gerettet!')
        s.died[0] = None
    elif msg.content.lower().strip() == 'nein':
        # Sie möchte das Opfer nicht retten
        await msg.author.send(s.died[0].mention + ' ({})'.format(get_name_discriminator(s.died[0])) + ' wurde nicht von dir gerettet.')
    else:
        await msg.author.send(NOT_UNDERSTAND + s.died[0].mention + ' ({}) '.format(get_name_discriminator(s.died[0])) + WITCH_INPUT_HEAL)
        return
    s.phase = ''
    try:
        # Hat sie noch einen Gifttrank, soll sie ihn benutzen können
        s.player_list[get_player(s, 'Hexe')]['tranks'].index('Gifttrank')
        s.phase = "WITCH_DEATH"
        await msg.author.send(WITCH_INPUT_KILL)
    except ValueError:
        await msg.author.send('Du hast deinen Gifttrank schon benutzt. Also gehst du wieder schlafen.')

async def choosing_witch_kill(s, msg):
    if msg.content.lower().strip() == 'nein':
        # Sie will niemanden vergiften
        s.phase = ''
        await msg.author.send('Du willst niemanden vergiftet und gehst wieder schlafen.')
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WITCH_FINISHED)
        await daytime(s)
        return

    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will sie vergiften?
        if is_alive(s, chosen.id):
            # Lebt diese Person überhaupt noch?
            amor = get_player(s, 'Amor')
            if amor:
                if msg.author in s.player_list[amor]['loving'] and chosen in s.player_list[amor]['loving']:
                    # Wenn die Hexe ihren Liebespartner vergiften will, halte sie davon ab
                    await msg.author.send('Du kannst deinen Liebespartner doch nicht vergiften! 💔')
                    return
            del s.player_list[get_player(s, 'Hexe')]['tranks'][s.player_list[get_player(s, 'Hexe')]['tranks'].index('Gifttrank')]
            killed_person = chosen
            await msg.author.send('Du hast folgende Person vergiftet: ' + killed_person.mention + ' ({})'.format(get_name_discriminator(killed_person)))
            s.died[2] = killed_person
            # Phase beendet; der Tag bricht an
            s.phase = ''
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(WITCH_FINISHED)
            await daytime(s)
        elif not is_alive(s, chosen.id):
            await msg.author.send(NOT_ALIVE + WITCH_INPUT_KILL)
    else:
        await msg.author.send( NOT_UNDERSTAND + WITCH_INPUT_KILL)


async def daytime(s):
    print(s.player_list)
    print(s.died)
    substract_lives(s)
    if [u.mention for u in s.died if u]:
        amor = get_player(s, 'Amor')
        if amor:
            # Wenn einer der Liebenden stirbt, sterben beide
            if s.player_list[amor]['loving'][0] in s.died and s.player_list[amor]['loving'][1] not in s.died:
                s.died.append(s.player_list[amor]['loving'][1])
            elif s.player_list[amor]['loving'][1] in s.died and s.player_list[amor]['loving'][1] not in s.died:
                s.died.append(s.player_list[amor]['loving'][0])
        await wake_up_with_dead(s)
    else:
        # Niemand ist gestorben
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die Sonne geht auf und der Tag bricht an. Alle wachen auf. *Niemand ist gestorben!* 🎉')
        await angry_mob(s)

async def wake_up_with_dead(s):
    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die Sonne geht auf und der Tag bricht an. Alle wachen auf.\nEs ist gestorben: ' + ', '.join([u.mention for u in s.died if u]))
    old_man = get_player(s, 'Alter Mann')
    if old_man:
        if old_man in s.died and old_man != s.died[0] and old_man != s.died[1]:
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Während der Nacht hat einer der Dorfbewohner' + OLD_MAN_DIED)
            old_man_died(s)
    hunter = get_player(s, 'Jäger')
    if hunter:
        if hunter in s.died:
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(HUNTER_DIED + hunter.mention + HUNTER_INPUT)
            s.phase = 'HUNTER_NIGHT'
            # Warte auf die Nachricht des Jägers
    if s.phase == 'HUNTER_NIGHT':
        return
    await good_to_wild(s)
    await angry_mob(s)

async def good_to_wild(s):
    wild_child = get_player(s, 'Wildes Kind')
    if wild_child:
        if is_alive(s, wild_child.id) and s.player_list[wild_child]['good']:
            if not is_alive(s, s.player_list[wild_child]['role model'].id):
                s.player_list[wild_child]['good'] = 0
                await wild_child.send('Dein Vorbild ist gestorben. Du agierst jetzt als Werwolf.')
                await wild_child.send('Es wurde ein neuer Kanal für dich und die anderen Werwölfe freigeschalten: <#' + str(
                    PLAYING_WEREWOLVES_CHANNEL) + '>')
                await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).set_permissions(wild_child, read_messages=True, send_messages=True)

async def choosing_hunter(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will er mit in den Tod reißen?
        if is_alive(s, chosen.id):
            # Lebt diese Person überhaupt noch?
            s.player_list[chosen]['alive'] = 0
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Der Jäger hat folgende Person mit sich in den Tod gerissen: ' + chosen.mention)
            old_man = get_player(s, 'Alter Mann')
            if old_man:
                if old_man == chosen:
                    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Der Jäger hat' + OLD_MAN_DIED)
                    old_man_died(s)
            # Phase beendet; Der Tag beginnt
            s.phase = ''
            if s.phase == "HUNTER_NIGHT":
                await good_to_wild(s)
                await angry_mob(s)
                return
            elif s.phase == "HUNTER_VOTE":
                await after_voting(s)
                return
        elif not is_alive(s, chosen.id):
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(NOT_ALIVE + msg.author.mention + HUNTER_INPUT)
    else:
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(NOT_UNDERSTAND + msg.author.mention + HUNTER_INPUT)

def old_man_died(s):
    for p in s.player_list:
        if not is_bad(s, p):
            #Wenn der alte Mann stirbt, wird jeder gute Mensch zum gewöhnlichen Dorfbewohner
            s.player_list[p]['role'] = 'Dorfbewohner'

async def angry_mob(s):
    if not await game_over(s):
        judge = get_player(s, 'Stotternder Richter')
        if judge:
            if is_alive(s, judge.id) and s.player_list[judge]['new vote']:
                await judge.send('Bis zum Ende der ersten Abstimmung kannst du mir mit der Nachricht `ABSTIMMUNG` sagen, dass du noch eine zweite Abstimmung direkt nach der ersten Abstimmung möchtest')
        # Abstimmung beginnt
        s.phase = 'VOTING'
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('In eurer Stadt passieren seltsame Dinge und ihr seid alle ein wütender Mob mit Fackeln 🔥 und Mistgabeln 🍴. Ihr wollt jemanden wählen, den ihr hinrichten könnt. (Wenn sich jemand entschieden hat, die gewünschte Person bitte mit einem `@` taggen.)\nACHTUNG: Es gibt nur eine Wahlrunde, also entscheidet weise (und denkt an den Dorfdepp und den Sündenbock)!')
    else:
        await reset_vars(s)

async def voting(s, msg):
    idiot = get_player(s, 'Dorfdepp')
    if idiot:
        if not s.player_list[idiot]['voting right']:
            # Wenn der Dorfdepp kein Stimmrecht mehr hat, dann ignorieren
            return
    if not s.player_list[msg.author]['alive']:
        return
    try:
        try:
            chosen_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', msg.content)[0])
        except IndexError:
            try:
                chosen_id = int(re.findall(r'(?<=<@)\d{18}(?=>)', msg.content)[0])
            except IndexError:
                return
        chosen = s.bot.get_user(chosen_id)
        if chosen in s.player_list.keys():
            # Wen will ein Spieler töten?
            if is_alive(s, chosen_id):
                # Lebt die Person noch?
                amor = get_player(s, 'Amor')
                if amor:
                    if msg.author in s.player_list[amor]['loving'] and chosen in s.player_list[amor]['loving']:
                        # Wenn jemand gegen seinen Liebespartner stimmen will, halte ihn davon ab
                        await msg.delete()
                        await msg.author.send('Du kannst doch nicht gegen deinen Liebespartner stimmen! 💔')
                        return
                s.player_list[msg.author]['voted for'] = chosen
                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(msg.author.mention + ' hat abgestimmt!')
                if citizens_chosen(s):
                    # Alle haben gewählt, Abstimmungsrunde beendet
                    s.phase = ''
                    judge = get_player(s, 'Stotternder Richter')
                    if judge and s.player_list[judge]['new vote']:
                        if is_alive(s, judge.id):
                            await judge.send('Die Abstimmung ist beendet und du kannst diese Runde keine zweite Abstimmung herbeiführen.')
                    candidates = []
                    for c, v in s.player_list.items():
                        candidates.append(v['voted for'])
                        v['voted for'] = None
                    count_cand = {k: v for k, v in sorted(dict(Counter(candidates)).items(), key=lambda item: item[1], reverse=True)}
                    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('So habt ihr abgestimmt:\n' + '\n'.join([u.mention + ': ' + str(c) for u,c in count_cand.items() if u]))
                    to_die = list(count_cand.keys())
                    for c, v in count_cand.items():
                        if v < count_cand[to_die[0]] or not c:
                            del to_die[to_die.index(c)]

                    if len(to_die) > 1:
                        scapegoat = get_player(s, 'Sündenbock')
                        if scapegoat:
                            if is_alive(s, scapegoat.id):
                                s.player_list[scapegoat]['alive'] = 0
                                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Ihr konntet euch nicht einig werden. Deshalb muss der Sündenbock, also ' + to_die[0].mention + ' sterben.')
                                await after_voting(s)
                                return
                        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Ihr konntet euch nicht einig werden und da es keinen Sündenbock gibt, stirbt heute niemand mehr.')
                    elif len(to_die) == 1:
                        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die Abstimmung hat ergeben, ' + to_die[0].mention + ' zu töten.')
                        if idiot:
                            if idiot == to_die[0] and s.player_list[idiot]['voting right']:
                                s.player_list[idiot]['voting right'] = 0
                                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Ihr habt den Dorfdeppen erwischt! Er stirbt nicht, verliert aber ab jetzt sein Stimmrecht.')
                                await after_voting(s)
                                return
                        s.player_list[to_die[0]]['alive'] = 0
                        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(to_die[0].mention + ' ist gestorben.')
                        old_man = get_player(s, 'Alter Mann')
                        if old_man:
                            if old_man == to_die[0]:
                                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Die Dorfbewohner haben' + OLD_MAN_DIED)
                                old_man_died(s)
                        hunter = get_player(s, 'Jäger')
                        if hunter:
                            if hunter == to_die[0]:
                                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(HUNTER_DIED + hunter.mention + HUNTER_INPUT)
                                s.phase = 'HUNTER_VOTE'
                                # Warte auf die Nachricht des Jägers
                                return

                    await after_voting(s)
                    return

            else:
                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(
                    msg.author.mention + ', dieser Spieler ist schon tot. Du kannst ihn nicht wählen.')
    except AttributeError:
        return

async def after_voting(s):
    await good_to_wild(s)
    if not await game_over(s):
        if s.new_vote:
            s.new_vote = False
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Der stotternde Richter hat eine neue Abstimmungsrunde angeordnet! Ihr müsst also sofort erneut jemanden wählen, den ihr hinrichten wollt. (Wenn sich jemand entschieden hat, die gewünschte Person bitte mit einem `@` taggen.)')
            # Neue Abstimmung beginnt
            s.phase = 'VOTING'
        else:
            await s.bot.get_channel(PLAYING_GAME_CHANNEL).send('Nach diesem anstrengenden Tag gehen alle wieder schlafen.')
            s.died = [None, None, None]
            s.round_no += 1
            await standard_night(s)
    else:
        await reset_vars(s)

def substract_lives(s):
    for d in s.died:
        if d:
            s.player_list[d]['lives'] -= 1  # Jeder verliert ein Leben
            if s.player_list[d]['lives'] > 0 and d == s.died[0] or d == s.died[1]:
                # Wenn der Spieler noch Leben übrig hat, dann stirbt er nicht;
                # aber nur, wenn er von einem Werwolf gefressen wurde
                s.died[s.died.index(d)] = None
            else:
                # Der Spieler lebt nicht mehr
                s.player_list[d]['alive'] = 0

async def game_over(s):
    print(s.player_list)
    if not still_alive(s):
        # Alle sind tot
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(GAME_OVER + NOONE_WON)
        # await reset_vars(s)
        return True
    elif True in [s.player_list[x]['good'] for x in still_alive(s)] and False in [s.player_list[x]['good'] for x in still_alive(s)]:
        amor = get_player(s, 'Amor')
        if amor:
            if len(still_alive(s)) == 2 and s.player_list[amor]['loving'][0] in still_alive(s) and s.player_list[amor]['loving'][1] in still_alive(s):
                #Das Liebespaar gewinnt
                await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(GAME_OVER + COUPLE_WON)
                #await reset_vars(s)
                return True
    elif True not in [s.player_list[x]['good'] for x in still_alive(s)]:
        # Die Dorfbewohner haben verloren
        white_werewolf = get_player(s, 'Weißer Werwolf')
        if len(still_alive(s)) == 1:
            if white_werewolf:
                if s.player_list[white_werewolf] in still_alive(s):
                    await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(GAME_OVER + WHITE_WEREWOLF_WON)
                    return True
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(GAME_OVER + BAD_WON)
        #await reset_vars(s)
        return True
    elif False not in [s.player_list[x]['good'] for x in still_alive(s)]:
        # Die Werwölfe haben verloren
        await s.bot.get_channel(PLAYING_GAME_CHANNEL).send(GAME_OVER + GOOD_WON)
        #reset_vars(s)
        return True
    return False

async def reset_vars(s):
    for player in s.player_list:
        await s.bot.get_channel(PLAYING_WEREWOLVES_CHANNEL).set_permissions(player, read_messages=False, send_messages=False)
    s.ready_list = []
    s.player_list = {}
    s.current_roles = []
    s.died = [None, None, None]
    s.new_vote = False

    s.playerID = None
    s.playing = False
    s.phase = ''

    s.game_status: Dict[str, bool] = {'waiting for selection': False, 'selecting': False, 'playing': False}
    s.round_no = 1

