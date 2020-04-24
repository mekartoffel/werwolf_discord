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


def is_game_channel_or_dm(ctx):
    """Check if channel of context is the channel where you can play.

    Keyword arguments:
    ctx -- Context
    """
    return is_game_channel(ctx) or isinstance(ctx.message.channel, discord.DMChannel)


async def distribute_roles(s, ww_roles):
    """Distribute roles and start the game.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    werewolves = []
    shuffle(s.current_roles)
    for i, player in enumerate(s.ready_list):
        role = s.current_roles[i]
        role_info = ww_roles[role].copy()
        role_info['role'] = role

        s.player_list[player] = role_info
        print(s.player_list[player])
        del s.player_list[player]['wake up']
        del s.player_list[player]['description']

        await player.send(ROLE_FOR_PLAYER.format(role=role))
        if role == WITCH_ROLE:
            s.player_list[player]['tranks'] = ["Heiltrank", "Gifttrank"]
        if not s.player_list[player]['good']:
            werewolves.append(player)
            await player.send(NEW_WW_CHANNEL.format(channel_id=str(s.werewolf_channel)))
            await s.bot.get_channel(s.werewolf_channel).set_permissions(player, read_messages=True, send_messages=True)
    await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_WELCOME.format(werewolves=' '.join([w.mention for w in werewolves])))
    print(s.player_list)
    await first_night(s)


def correct_roles(s, role_list):
    """Check if the roles can be mapped to the roles in `werwolf_rollen.json`. If there is no werewolf then the function returns `False`. Also checks if there are enough roles.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    roles = [role.lower().strip() for role in s.current_roles]
    if 'werwolf' not in roles:
        print('kein werwolf')
        return False
    elif False in [r in [role.lower() for role in role_list] for r in roles]:
        print('kein richtiger')
        return False
    if 'dieb' in roles:
        return len(roles) == len(s.ready_list) + 2
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
    player = discord.utils.find(lambda m: player_name.lower() in m.name.lower(), s.bot.get_guild(s.server_id).members)
    if not player:
        player = discord.utils.find(lambda m: player_name.lower() in m.nick.lower() if m.nick else False, s.bot.get_guild(s.server_id).members)
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
    for p, v in s.player_list.items():
        if not v['good']:
            if not v['citizen']:
                if v['alive']:
                    return False
    return True


def citizens_chosen(s):
    """Check if all the citizens have chosen a victim.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    for p, v in s.player_list.items():
        if not v['voted for']:
            idiot = get_player(s, IDIOT_ROLE)
            if p == idiot:
                if not s.player_list[idiot]['voting right']:
                    continue
            if not s.player_list[p]['alive']:
                continue
            return False
    return True


def thief_in_game(s):
    return THIEF_ROLE in s.current_roles



async def first_night(s):
    """Start the first night of the game. Special characters have to wake up in the first night. If there are no special characters for the first night in the game then just start the 'normal' night.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    await s.bot.get_channel(s.game_channel).send(GOING_TO_SLEEP)
    # Nur einer wird geweckt; wenn keiner in diesem Spiel vertreten ist, dann ist die erste Nacht "irrelevant"
    if THIEF_ROLE in s.current_roles:
        await wake_thief(s)
    elif CUPID_ROLE in s.current_roles:
        await wake_amor(s)
    elif WILD_CHILD_ROLE in s.current_roles:
        await wake_wild_child(s)
    else:
        await standard_night(s)


async def standard_night(s):
    """Start the standard night of the game.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    print('standard night')
    print(s.current_roles)
    if HEALER_ROLE in s.current_roles:
        await wake_healer(s)
    elif SEER_ROLE in s.current_roles:
        await wake_seer(s)
    else:
        await wake_werewolves(s)


async def wake_thief(s):
    """Wake up the thief. If there is no thief in the game but in the rest of the chosen character roles then pretend as if there is a thief.

    Keyword arguments:
    s -- self of the calling class; to pass class vars
    """
    await s.bot.get_channel(s.game_channel).send(THIEF_WAKE)
    if not get_player(s, THIEF_ROLE):
        # Kein Spieler ist Dieb
        # Sleep, sodass niemand es merkt, dass kein Dieb im Spiel ist
        await asyncio.sleep(random.randint(15, 40))
        await s.bot.get_channel(s.game_channel).send(THIEF_FINISHED)
        if CUPID_ROLE in s.current_roles:
            await wake_amor(s)
        elif WILD_CHILD_ROLE in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await get_player(s, THIEF_ROLE).send(THIEF_OPTIONS.format(roles=', '.join(s.current_roles[-2:])))
        s.phase = THIEF_PHASE
        # Warte auf Antwort vom Dieb


async def choosing_thief(s, msg, ww_roles):
    for role in s.current_roles[-2:]:
        if msg.content.lower().strip() == role.lower():
            print(msg.content)
            role = ' '.join([part.capitalize() for part in role.split(' ')])
            s.player_list[msg.author]['role'] = role
            role_index = s.current_roles.index(role)
            # Tausche die Reihenfolge aus
            s.current_roles[s.current_roles.index(THIEF_ROLE)] = role
            s.current_roles[role_index] = THIEF_ROLE
            print(s.current_roles)
            # Weise dem Spieler die neue Rolle zu
            role_info = ww_roles[role].copy()
            role_info['role'] = role
            s.player_list[msg.author] = role_info
            del s.player_list[msg.author]['wake up']
            del s.player_list[msg.author]['description']
            print(s.player_list)
            await msg.author.send(THIEF_CHOSE.format(role=role))
            if 'werwolf' in msg.content.lower():
                await s.bot.get_channel(s.werewolf_channel).set_permissions(msg.author, read_messages=True, send_messages=True)
                await msg.author.send(NEW_WW_CHANNEL.format(channel_id=str(s.werewolf_channel)))
                await s.bot.get_channel(s.werewolf_channel).send(NEW_WW.format(player=msg.author.mention))
            # Phase ist beendet; Entscheidung, was als nächstes passiert
            s.phase = ''
            await s.bot.get_channel(s.game_channel).send(THIEF_FINISHED)
            if CUPID_ROLE in s.current_roles:
                await wake_amor(s)
            elif WILD_CHILD_ROLE in s.current_roles:
                await wake_wild_child(s)
            else:
                await standard_night(s)
            return
    await msg.author.send(THIEF_CHOSE_WRONG)


async def wake_amor(s):
    await s.bot.get_channel(s.game_channel).send(CUPID_WAKE)
    if not get_player(s, CUPID_ROLE):
        # Kein Spieler ist Amor
        # Sleep, sodass es nicht auffällt, dass kein Amor im Spiel ist
        await asyncio.sleep(random.randint(30, 60))
        await s.bot.get_channel(s.game_channel).send(CUPID_FINISHED)
        if WILD_CHILD_ROLE in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await get_player(s, CUPID_ROLE).send(CUPID_INPUT)
        s.phase = CUPID_PHASE
        # Warte auf Antwort vom Amor


async def choosing_amor(s, msg):
    chosen = [get_player_by_name(s, p.strip()) for p in msg.content.split(',')]
    if len(chosen) >= 2 and in_playerlist(s, chosen) and chosen[0] != chosen[1]:
        # Wer sind die Verliebten?
        s.player_list[msg.author]['loving'] = chosen[:2]
        await msg.author.send(CUPID_CHOSE_COUPLE.format(couple=' und '.join([user.mention + ' ({})'.format(get_name_discriminator(user)) for user in s.player_list[msg.author]['loving']])))
        # Die Verliebten informieren
        lover1 = s.player_list[msg.author]['loving'][0]
        lover2 = s.player_list[msg.author]['loving'][1]
        await lover1.send(NOTIFY_LOVER.format(other_lover=lover2.mention + ' ({}) '.format(get_name_discriminator(lover2))))
        await lover2.send(NOTIFY_LOVER.format(other_lover=lover1.mention + ' ({}) '.format(get_name_discriminator(lover1))))
        # Phase ist beendet; Entscheidung, was als nächstes passiert
        s.phase = ''
        await s.bot.get_channel(s.game_channel).send(CUPID_FINISHED)
        if WILD_CHILD_ROLE in s.current_roles:
            await wake_wild_child(s)
        else:
            await standard_night(s)
    else:
        await msg.author.send(NOT_UNDERSTAND + CUPID_INPUT)


async def wake_wild_child(s):
    await s.bot.get_channel(s.game_channel).send(WILD_CHILD_WAKE)
    wild_child = get_player(s, WILD_CHILD_ROLE)
    if not wild_child:
        # Kein Spieler ist das wilde Kind
        # Sleep, sodass es nicht auffällt, dass kein wildes Kind im Spiel ist
        await asyncio.sleep(random.randint(30, 70))
        await s.bot.get_channel(s.game_channel).send(WILD_CHILD_FINISHED)
        await standard_night(s)
    else:
        await wild_child.send(WILD_CHILD_INPUT)
        s.phase = WILD_CHILD_PHASE
        # Warte auf Antwort vom wildem Kind


async def choosing_wild_child(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen.id != msg.author.id:
        s.player_list[msg.author]['role model'] = chosen
        await msg.author.send(WILD_CHILD_CHOSE.format(player=chosen.mention + ' ({})'.format(get_name_discriminator(chosen))))
        # Phase beendet; Die Spezialrollen für die erste Nacht sind fertig.
        s.phase = ''
        await s.bot.get_channel(s.game_channel).send(WILD_CHILD_FINISHED)
        await standard_night(s)
    else:
        await msg.author.send(NOT_UNDERSTAND + WILD_CHILD_INPUT)


async def wake_healer(s):
    healer = get_player(s, HEALER_ROLE)
    if not healer:
        # Kein Spieler ist der Heiler
        # Sleep, sodass es nicht auffällt
        await s.bot.get_channel(s.game_channel).send(HEALER_WAKE)
        await asyncio.sleep(random.randint(25, 45))
        await s.bot.get_channel(s.game_channel).send(HEALER_FINISHED)
        if SEER_ROLE in s.current_roles:
            await wake_seer(s)
        else:
            await wake_werewolves(s)
    elif not is_alive(s, healer.id):
        # Heiler ist schon tot
        if SEER_ROLE in s.current_roles:
            await wake_seer(s)
        else:
            await wake_werewolves(s)
    else:
        await s.bot.get_channel(s.game_channel).send(HEALER_WAKE)
        await healer.send(HEALER_INPUT)
        s.phase = HEALER_PHASE
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
                await msg.author.send(HEALER_CHOSE.format(player=chosen.mention + ' ({})'.format(get_name_discriminator(chosen))))
                # Phase beendet; Entscheidung, was als nächstes passiert
                s.phase = ''
                await s.bot.get_channel(s.game_channel).send(HEALER_FINISHED)
                if SEER_ROLE in s.current_roles:
                    await wake_seer(s)
                else:
                    await wake_werewolves(s)
            else:
                await msg.author.send(HEALER_SAME_IN_ROW)
        else:
            await msg.author.send(NOT_ALIVE + HEALER_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + HEALER_INPUT)


async def wake_seer(s):
    seer = get_player(s, SEER_ROLE)
    if not seer:
        # Kein Spieler ist die Seherin
        # Sleep, sodass es nicht auffällt
        await s.bot.get_channel(s.game_channel).send(SEER_WAKE)
        await asyncio.sleep(random.randint(7, 30))
        await s.bot.get_channel(s.game_channel).send(SEER_FINISHED)
        await wake_werewolves(s)
    elif not is_alive(s, seer.id):
        # Die Seherin ist schon tot
        await wake_werewolves(s)
    else:
        await s.bot.get_channel(s.game_channel).send(SEER_WAKE)
        await seer.send(SEER_INPUT)
        s.phase = SEER_PHASE
        # Warte auf Antwort von der Seherin


async def choosing_seer(s, msg):
    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will die Seherin überprüfen?
        if is_alive(s, chosen.id):
            # Lebt die Person noch?
            checked_person = chosen
            await msg.author.send(SEER_SEE_ROLE.format(player=checked_person.mention + ' ({})'.format(get_name_discriminator(checked_person)), role=s.player_list[checked_person]['role']))
            # Phase beendet; Werwölfe sind als nächstes dran
            s.phase = ''
            await s.bot.get_channel(s.game_channel).send(SEER_FINISHED)
            await wake_werewolves(s)
        else:
            await msg.author.send(NOT_ALIVE + SEER_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + SEER_INPUT)


async def wake_werewolves(s):
    await s.bot.get_channel(s.game_channel).send(WEREWOLVES_WAKE)
    werewolves = [x for x in s.player_list.keys() if not s.player_list[x]['good'] and s.player_list[x]['alive']]
    await s.bot.get_channel(s.werewolf_channel).send(' '.join([w.mention for w in werewolves]) + WEREWOLVES_INPUT)
    s.phase = WEREWOLVES_PHASE
    # Warte auf Antwort von den Werwölfen


async def choosing_werewolves(s, msg):
    if 'enthaltung' in msg.content.lower() and is_alive(s, msg.author.id):
        s.player_list[msg.author]['citizen'] = msg.guild.get_member(BOT_ID)
        await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_DONT_CARE.format(player=msg.author.mention))
        if werewolves_chosen(s):
            # Erst, wenn alle gewählt haben, wird gefragt, ob sie mit der Wahl einverstanden sind.
            citizens = []
            for p, v in s.player_list.items():
                if not v['good'] and v['citizen'] != msg.guild.get_member(BOT_ID):
                    citizens.append(v['citizen'])
            s.died[0] = max(dict(Counter(citizens)).items(), key=operator.itemgetter(1))[0]
            if not s.died[0]:
                await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_WHO_TO_KILL)
                return
            await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_CONFIRM.format(victim=get_name_discriminator(s.died[0])))
            s.phase = WEREWOLVES_PHASE_CONFIRM
        return
    citizen = get_player_by_name(s, msg.content.strip())
    print(citizen)
    if citizen in s.player_list.keys():
        # Wen wollen die Werwölfe fressen?
        if not is_bad(s, citizen.id) and is_alive(s, citizen.id) and is_alive(s, msg.author.id):
            # Ist diese Person überhaupt ein Dorfbewohner? Und lebt sie noch? Und lebt der Werwolf überhaupt?
            amor = get_player(s, CUPID_ROLE)
            if amor:
                if msg.author in s.player_list[amor]['loving'] and citizen in s.player_list[amor]['loving']:
                    #Wenn ein Werwolf seinen Liebespartner fressen will, halte ihn davon ab
                    await msg.delete()
                    await msg.author.send(WEREWOLVES_LOVE)
                    return
            s.player_list[msg.author]['citizen'] = citizen
            await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_CHOSE.format(player=msg.author.mention, victim=get_name_discriminator(citizen)))
            if werewolves_chosen(s):
                # Erst, wenn alle gewählt haben, wird gefragt, ob sie mit der Wahl einverstanden sind.
                citizens = []
                for p, v in s.player_list.items():
                    if not v['good'] and v['citizen'] != msg.guild.get_member(BOT_ID):
                        citizens.append(v['citizen'])
                s.died[0] = max(dict(Counter(citizens)).items(), key=operator.itemgetter(1))[0]
                if not s.died[0]:
                    s.died[0] = citizen
                await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_CONFIRM.format(victim=get_name_discriminator(s.died[0])))
                s.phase = WEREWOLVES_PHASE_CONFIRM
        elif not is_alive(s, msg.author.id):
            await s.bot.get_channel(s.werewolf_channel).send(CANT_VOTE.format(player=msg.author.mention))
        else:
            await s.bot.get_channel(s.werewolf_channel).send(NOT_ALLOWED.format(player=msg.author.mention))
    # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich


async def confirming_werewolves(s, msg):
    if msg.content.lower().strip() == 'ja':
        # Die Werwölfe haben sich entschieden, die Person zu fressen
        await s.bot.get_channel(s.werewolf_channel).send(ATE.format(victim=get_name_discriminator(s.died[0])))
        # Phase beendet; Entscheidung, was als nächstes passiert
        s.phase = ''
        await s.bot.get_channel(s.game_channel).send(WEREWOLVES_FINISHED)
        healer = get_player(s, HEALER_ROLE)
        if get_player(s, HEALER_ROLE):
            # Wenn der Heiler diese Person schützt, wird sie aber nicht sterben
            if s.died[0] == s.player_list[healer]['chosen']:
                s.died[0] = None
        for c, v in s.player_list.items():
            if is_alive(s, c.id) and is_bad(s, c.id):
                v['citizen'] = None
        if WHITE_WEREWOLF_ROLE in s.current_roles and (s.round_no % 2 == 0):
            await wake_white_werewolf(s)
        elif WITCH_ROLE in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
    elif msg.content.lower().strip() == 'nein':
        await s.bot.get_channel(s.werewolf_channel).send(WEREWOLVES_VOTE_AGAIN)
        s.phase = WEREWOLVES_PHASE
    # Wenn es eine komische Nachricht ist, dann diskutieren sie wahrscheinlich


async def wake_white_werewolf(s):
    white_werewolf = get_player(s, WHITE_WEREWOLF_ROLE)
    if not white_werewolf:
        # Kein Spieler ist der weiße Werwolf
        await s.bot.get_channel(s.game_channel).send(WHITE_WEREWOLF_WAKE)
        await asyncio.sleep(random.randint(15, 45))
        await s.bot.get_channel(s.game_channel).send(WHITE_WEREWOLF_FINISHED)
        if WITCH_ROLE in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
    elif not is_alive(s, white_werewolf.id):
        # Der weiße Werwolf ist schon tot
        if WITCH_ROLE in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
    else:
        await s.bot.get_channel(s.game_channel).send(WHITE_WEREWOLF_WAKE)
        await white_werewolf.send(WHITE_WEREWOLF_INPUT)
        s.phase = WHITE_WEREWOLF_PHASE
        # Warte auf Antwort vom weißen Werwolf


async def choosing_white_werewolf(s, msg):
    if msg.content.lower().strip() == 'niemanden':
        # Wenn der weiße Werwolf niemanden fressen will, dann geht es einfach weiter
        await s.bot.get_channel(s.game_channel).send(WHITE_WEREWOLF_FINISHED)
        s.phase = ''
        if WITCH_ROLE in s.current_roles:
            await wake_witch(s)
        else:
            await daytime(s)
        return

    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will der weiße Werwolf fressen?
        if is_alive(s, chosen.id) and is_bad(s, chosen.id):
            # Lebt die Person noch? Ist das überhaupt einer seiner Werwolfkameraden?
            amor = get_player(s, CUPID_ROLE)
            if amor:
                if msg.author in s.player_list[amor]['loving'] and chosen in s.player_list[amor]['loving']:
                    # Wenn er seinen Liebespartner fressen will, halte ihn davon ab
                    await msg.author.send(WHITE_WEREWOLF_LOVE)
                    return
            comrade = chosen
            # Phase beendet; Entscheidung, was als nächstes passiert
            s.phase = ''
            await msg.author.send(ATE.format(victim=comrade.mention + ' ({})'.format(get_name_discriminator(comrade))))
            s.died[1] = comrade
            healer = get_player(s, 'Heiler')
            if healer:
                # Wenn der Heiler diese Person schützt, wird sie aber nicht sterben
                if s.died[1] == s.player_list[healer]['chosen']:
                    s.died[1] = None
            await s.bot.get_channel(s.game_channel).send(WHITE_WEREWOLF_FINISHED)
            if WITCH_ROLE in s.current_roles:
                await wake_witch(s)
            else:
                await daytime(s)
        elif not is_bad(s, chosen.id):
            await msg.author.send(WHITE_WEREWOLF_NOT_COMRADE)
        elif not is_alive(s, chosen.id):
            await msg.author.send(NOT_ALIVE + WHITE_WEREWOLF_INPUT)
    else:
        await msg.author.send(NOT_UNDERSTAND + WHITE_WEREWOLF_INPUT)


async def wake_witch(s):
    witch = get_player(s, WITCH_ROLE)
    if not witch:
        # Kein Spieler ist die Hexe
        # Sleep, sodass es nicht auffällt
        await s.bot.get_channel(s.game_channel).send(WITCH_WAKE)
        await asyncio.sleep(random.randint(20, 45))
        await s.bot.get_channel(s.game_channel).send(WITCH_FINISHED)
        await daytime(s)
    elif not is_alive(s, witch.id):
        # Die Hexe ist schon tot
        await daytime(s)
    else:
        await s.bot.get_channel(s.game_channel).send(WITCH_WAKE)
        tranks = s.player_list[witch]['tranks']
        if 'Heiltrank' in tranks:
            # Wenn sie noch einen Heiltrank hat, dann soll sie diesen benutzen können
            if s.died[0]:
                s.phase = WITCH_PHASE_HEAL
                await witch.send(s.died[0].mention + ' ({}) '.format(get_name_discriminator(s.died[0])) + WITCH_INPUT_HEAL)
                # Warte auf Antwort von der Hexe
                return
            else:
                await witch.send(NO_ONE_DIED)
                s.phase = WITCH_PHASE_KILL
                await witch.send(WITCH_INPUT_KILL)
        elif 'Gifttrank' in tranks:
            await witch.send(WITCH_ALREADY_HEALED)
            # Wenn sie keinen Heiltrank mehr hat oder niemand gestorben ist, soll sie direkt den Gifttrank benutzen können
            s.phase = WITCH_PHASE_KILL
            await witch.send(WITCH_INPUT_KILL)
        else:
            # Die Hexe hat keine Tränke mehr und kann nichts machen
            await witch.send(WITCH_NO_TRANKS)
            await asyncio.sleep(random.randint(10, 20))
            await s.bot.get_channel(s.game_channel).send(WITCH_FINISHED)
            await daytime(s)


async def choosing_witch_heal(s, msg):
    witch = get_player(s, WITCH_ROLE)
    tranks = s.player_list[witch]['tranks']
    if msg.content.lower().strip() == 'ja':
        # Sie möchte das Opfer retten
        del tranks[tranks.index('Heiltrank')]
        await msg.author.send(WITCH_HEALED.format(player=s.died[0].mention + ' ({}) '.format(get_name_discriminator(s.died[0]))))
        s.died[0] = None
    elif msg.content.lower().strip() == 'nein':
        # Sie möchte das Opfer nicht retten
        await msg.author.send(WITCH_NOT_HEALED.format(player=s.died[0].mention + ' ({})'.format(get_name_discriminator(s.died[0]))))
    else:
        await msg.author.send(NOT_UNDERSTAND + s.died[0].mention + ' ({}) {}'.format(get_name_discriminator(s.died[0]), WITCH_INPUT_HEAL))
        return
    s.phase = ''
    if 'Gifttrank' in tranks:
        # Hat sie noch einen Gifttrank, soll sie ihn benutzen können
        s.phase = WITCH_PHASE_KILL
        await msg.author.send(WITCH_INPUT_KILL)
    else:
        await msg.author.send(WITCH_ALREADY_KILLED)


async def choosing_witch_kill(s, msg):
    if msg.content.lower().strip() == 'nein':
        # Sie will niemanden vergiften
        await msg.author.send(WITCH_NO_KILLING)
        s.phase = ''
        await s.bot.get_channel(s.game_channel).send(WITCH_FINISHED)
        await daytime(s)
        return

    chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    witch = get_player(s, WITCH_ROLE)
    tranks = s.player_list[witch]['tranks']
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will sie vergiften?
        if is_alive(s, chosen.id):
            # Lebt diese Person überhaupt noch?
            amor = get_player(s, CUPID_ROLE)
            if amor:
                if msg.author in s.player_list[amor]['loving'] and chosen in s.player_list[amor]['loving']:
                    # Wenn die Hexe ihren Liebespartner vergiften will, halte sie davon ab
                    await msg.author.send(WITCH_LOVE)
                    return
            del tranks[tranks.index('Gifttrank')]
            killed_person = chosen
            await msg.author.send(WITCH_KILLED.format(victim=killed_person.mention + ' ({})'.format(get_name_discriminator(killed_person))))
            s.died[2] = killed_person
            # Phase beendet; der Tag bricht an
            s.phase = ''
            await s.bot.get_channel(s.game_channel).send(WITCH_FINISHED)
            await daytime(s)
        elif not is_alive(s, chosen.id):
            await msg.author.send(NOT_ALIVE + WITCH_INPUT_KILL)
    else:
        await msg.author.send(NOT_UNDERSTAND + WITCH_INPUT_KILL)


async def daytime(s):
    print(s.player_list)
    print(s.died)
    substract_lives(s)
    if [u.mention for u in s.died if u]:
        await wake_up_with_dead(s)
    else:
        # Niemand ist gestorben
        await s.bot.get_channel(s.game_channel).send('{} *{}*'.format(MORNING, NO_ONE_DIED))
        await angry_mob(s)


async def wake_up_with_dead(s):
    await s.bot.get_channel(s.game_channel).send(WHO_DIED.format(MORNING, ', '.join(['{player} ({role})'.format(player=u.mention, role=s.player_list[u]['role']) for u in s.died if u])))
    amor = get_player(s, CUPID_ROLE)
    if amor:
        # Wenn einer der Liebenden stirbt, sterben beide
        loving = s.player_list[amor]['loving']
        ld, ldw = None, None
        if loving[0] in s.died:
            ld = loving[0]  # Liebespartner, der gestorben ist
            ldw = loving[1] # Liebespartner, der mit ihm stirbt
        elif loving[1] in s.died:
            ld = loving[1]
            ldw = loving[0]
        if ld and ldw:
            s.player_list[ldw]['alive'] = 0
            s.died.append(ldw)
            await s.bot.get_channel(s.game_channel).send(COUPLE_DIES.format(td=ld.mention, loving=ldw.mention, role=s.player_list[ldw]['role']))
    old_man = get_player(s, OLD_MAN_ROLE)
    if old_man:
        if old_man in s.died and old_man != s.died[0] and old_man != s.died[1]:
            await s.bot.get_channel(s.game_channel).send('In der Nacht hat einer der Dorfbewohner' + OLD_MAN_DIED)
            old_man_died(s)
    hunter = get_player(s, HUNTER_ROLE)
    if hunter:
        if hunter in s.died and still_alive(s):
            # Der Jäger kann nur jemanden umbringen, wenn noch jemand lebt
            await s.bot.get_channel(s.game_channel).send(HUNTER_DIED + hunter.mention + HUNTER_INPUT)
            s.phase = HUNTER_PHASE_NIGHT
            # Warte auf die Nachricht des Jägers
            return
    await good_to_wild(s)
    await angry_mob(s)


async def good_to_wild(s):
    wild_child = get_player(s, WILD_CHILD_ROLE)
    if wild_child:
        if is_alive(s, wild_child.id) and s.player_list[wild_child]['good']:
            if not is_alive(s, s.player_list[wild_child]['role model'].id):
                s.player_list[wild_child]['good'] = 0
                await wild_child.send(WILD_CHILD_RM_DIED)
                await wild_child.send(NEW_WW_CHANNEL.format(channel_id=str(s.werewolf_channel)))
                await s.bot.get_channel(s.werewolf_channel).set_permissions(wild_child, read_messages=True, send_messages=True)
                await s.bot.get_channel(s.werewolf_channel).send(NEW_WW.format(player=wild_child.mention))


async def choosing_hunter(s, msg):
    try:
        chosen_id = int(re.findall(r'(?<=<@!)\d{18}(?=>)', msg.content)[0])
    except IndexError:
        try:
            chosen_id = int(re.findall(r'(?<=<@)\d{18}(?=>)', msg.content)[0])
        except IndexError:
            return
    chosen = s.bot.get_user(chosen_id)
    #chosen = get_player_by_name(s, msg.content.strip())
    print(chosen)
    if chosen in s.player_list.keys() and chosen != msg.author:
        # Wen will er mit in den Tod reißen?
        if is_alive(s, chosen.id):
            # Lebt diese Person überhaupt noch?
            # Anm.: Es muss nicht beachtet werden, ob der Jäger seinen Liebespartner tötet, weil dieser sowieso vorher schon mit ihm stirbt
            s.player_list[chosen]['alive'] = 0
            await s.bot.get_channel(s.game_channel).send(HUNTER_CHOSE.format(victim=chosen.mention + ' ({})'.format(s.player_list[chosen]['role'])))
            chosen = [chosen]
            amor = get_player(s, CUPID_ROLE)
            if amor:
                # Wenn einer der Liebenden stirbt, sterben beide
                loving = s.player_list[amor]['loving']
                ldw = None
                if loving[0] == chosen[0]:
                    ldw = loving[1]  # Liebespartner, der mit ihm stirbt
                elif loving[1] == chosen[0]:
                    ldw = loving[0]
                if ldw:
                    s.player_list[ldw]['alive'] = 0
                    chosen.append(ldw)
                    await s.bot.get_channel(s.game_channel).send(COUPLE_DIES.format(td=chosen[0].mention, loving=ldw.mention, role=s.player_list[ldw]['role']))
            old_man = get_player(s, OLD_MAN_ROLE)
            if old_man:
                if old_man in chosen:
                    await s.bot.get_channel(s.game_channel).send('Der Jäger hat' + OLD_MAN_DIED)
                    old_man_died(s)
            if s.phase == HUNTER_PHASE_NIGHT:
                # Phase beendet; Der Tag beginnt
                s.phase = ''
                await good_to_wild(s)
                await angry_mob(s)
                return
            elif s.phase == HUNTER_PHASE_VOTE:
                # Phase beendet; Der Tag beginnt
                s.phase = ''
                await after_voting(s)
                return
        elif not is_alive(s, chosen.id):
            await s.bot.get_channel(s.game_channel).send(NOT_ALIVE + msg.author.mention + HUNTER_INPUT)
    else:
        await s.bot.get_channel(s.game_channel).send(NOT_UNDERSTAND + msg.author.mention + HUNTER_INPUT)


def old_man_died(s):
    for p in s.player_list:
        if not is_bad(s, p.id):
            # Wenn der alte Mann stirbt, wird jeder gute Mensch zum gewöhnlichen Dorfbewohner
            s.player_list[p]['role'] = 'Dorfbewohner'


async def angry_mob(s):
    if not await game_over(s):
        judge = get_player(s, JUDGE_ROLE)
        if judge:
            if is_alive(s, judge.id) and s.player_list[judge]['new vote']:
                await judge.send(JUDGE_NEW_VOTE_POSSIBLE)
        # Abstimmung beginnt
        s.phase = VOTING_PHASE
        await s.bot.get_channel(s.game_channel).send(ANGRY_MOB)
    else:
        await reset_vars(s)


async def voting(s, msg):
    idiot = get_player(s, IDIOT_ROLE)
    if msg.author == idiot and not s.player_list[idiot]['voting right']:
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
                amor = get_player(s, CUPID_ROLE)
                if amor:
                    if msg.author in s.player_list[amor]['loving'] and chosen in s.player_list[amor]['loving'] and msg.author != chosen:
                        # Wenn jemand gegen seinen Liebespartner stimmen will, halte ihn davon ab; Aber wenn er sich selbst wählt, ist es okay
                        await msg.delete()
                        await msg.author.send(CITIZEN_LOVE)
                        return
                s.player_list[msg.author]['voted for'] = chosen
                await s.bot.get_channel(s.game_channel).send(VOTED_FOR.format(player=msg.author.mention, chosen=chosen.mention))
                if citizens_chosen(s):
                    # Alle haben gewählt, Abstimmungsrunde beendet
                    s.phase = ''
                    judge = get_player(s, JUDGE_ROLE)
                    if judge and s.player_list[judge]['new vote']:
                        if is_alive(s, judge.id):
                            await judge.send(JUDGE_NO_VOTE_POSSIBLE)
                    candidates = []
                    for c, v in s.player_list.items():
                        candidates.append(v['voted for'])
                        v['voted for'] = None
                    count_cand = {k: v for k, v in sorted(dict(Counter(candidates)).items(), key=lambda item: item[1], reverse=True)}
                    await s.bot.get_channel(s.game_channel).send(VOTE_FINISHED.format(votes='\n'.join([u.mention + ': ' + str(c) for u, c in count_cand.items() if u])))
                    to_die = list(count_cand.keys())
                    for c, v in count_cand.items():
                        if v < count_cand[to_die[0]] or not c:
                            del to_die[to_die.index(c)]

                    if len(to_die) > 1:
                        scapegoat = get_player(s, SCAPEGOAT_ROLE)
                        if scapegoat:
                            if is_alive(s, scapegoat.id):
                                to_die = []
                                s.player_list[scapegoat]['alive'] = 0
                                await s.bot.get_channel(s.game_channel).send(VOTE_SCAPEGOAT.format(scapegoat=scapegoat.mention))
                                if amor:
                                    # Wenn einer der Liebenden stirbt, sterben beide
                                    loving = s.player_list[amor]['loving']
                                    ldw = None
                                    if loving[0] == scapegoat:
                                        ldw = loving[1]
                                    elif loving[1] == scapegoat:
                                        ldw = loving[0]
                                    if ldw:
                                        s.player_list[ldw]['alive'] = 0
                                        to_die.append(ldw)
                                        await s.bot.get_channel(s.game_channel).send(COUPLE_DIES.format(td=scapegoat.mention, loving=ldw.mention, role=s.player_list[ldw]['role']))
                                    old_man = get_player(s, OLD_MAN_ROLE)
                                    if old_man:
                                        if old_man in to_die:
                                            await s.bot.get_channel(s.game_channel).send('Die Dorfbewohner haben' + OLD_MAN_DIED)
                                            old_man_died(s)
                                    hunter = get_player(s, HUNTER_ROLE)
                                    if hunter:
                                        if hunter in to_die and still_alive(s):
                                            # Der Jäger kann nur jemanden umbringen, wenn noch jemand lebt
                                            await s.bot.get_channel(s.game_channel).send(HUNTER_DIED + hunter.mention + HUNTER_INPUT)
                                            s.phase = HUNTER_PHASE_VOTE
                                            # Warte auf die Nachricht des Jägers
                                            return
                                await after_voting(s)
                                return
                        await s.bot.get_channel(s.game_channel).send(VOTE_DRAW)
                    elif len(to_die) == 1:
                        to_die = [to_die[0]]
                        await s.bot.get_channel(s.game_channel).send(VOTE_VICTIM.format(victim=to_die[0].mention))
                        if idiot:
                            if idiot == to_die[0] and s.player_list[idiot]['voting right']:
                                s.player_list[idiot]['voting right'] = 0
                                await s.bot.get_channel(s.game_channel).send(VOTE_IDIOT)
                                await after_voting(s)
                                return
                        s.player_list[to_die[0]]['alive'] = 0
                        await s.bot.get_channel(s.game_channel).send(PLAYER_DIED.format(player=to_die[0].mention, role=s.player_list[to_die[0]]['role']))
                        if amor:
                            # Wenn einer der Liebenden stirbt, sterben beide
                            loving = s.player_list[amor]['loving']
                            ldw = None
                            if loving[0] == to_die[0]:
                                ldw = loving[1]
                            elif loving[1] == to_die[0]:
                                ldw = loving[0]
                            if ldw:
                                s.player_list[ldw]['alive'] = 0
                                to_die.append(ldw)
                                await s.bot.get_channel(s.game_channel).send(COUPLE_DIES.format(td=to_die[0].mention, loving=ldw.mention, role=s.player_list[ldw]['role']))
                        old_man = get_player(s, OLD_MAN_ROLE)
                        if old_man:
                            if old_man in to_die:
                                await s.bot.get_channel(s.game_channel).send('Die Dorfbewohner haben' + OLD_MAN_DIED)
                                old_man_died(s)
                        hunter = get_player(s, HUNTER_ROLE)
                        if hunter:
                            if hunter in to_die and still_alive(s):
                                # Der Jäger kann nur jemanden umbringen, wenn noch jemand lebt
                                await s.bot.get_channel(s.game_channel).send(HUNTER_DIED + hunter.mention + HUNTER_INPUT)
                                s.phase = HUNTER_PHASE_VOTE
                                # Warte auf die Nachricht des Jägers
                                return

                    await after_voting(s)
                    return
            else:
                await s.bot.get_channel(s.game_channel).send(ALREADY_DEAD.format(player=msg.author.mention))
    except AttributeError:
        return


async def after_voting(s):
    await good_to_wild(s)
    if not await game_over(s):
        if s.new_vote:
            s.new_vote = False
            await s.bot.get_channel(s.game_channel).send(JUDGE_NEW_VOTE)
            # Neue Abstimmung beginnt
            s.phase = VOTING_PHASE
        else:
            await s.bot.get_channel(s.game_channel).send(CITIZENS_SLEEP)
            s.died = [None, None, None]
            s.round_no += 1
            await standard_night(s)
    else:
        await reset_vars(s)


def substract_lives(s):
    for d in s.died:
        if d:
            s.player_list[d]['lives'] -= 1  # Jeder verliert ein Leben
            if s.player_list[d]['lives'] > 0 and (d == s.died[0] or d == s.died[1]):
                # Wenn der Spieler noch Leben übrig hat, dann stirbt er nicht;
                # aber nur, wenn er von einem Werwolf gefressen wurde
                s.died[s.died.index(d)] = None
            else:
                # Der Spieler lebt nicht mehr
                s.player_list[d]['alive'] = 0


async def game_over(s):
    print(s.player_list)
    alive = still_alive(s)
    print(alive)
    if not alive:
        # Alle sind tot
        await s.bot.get_channel(s.game_channel).send(GAME_OVER + NOONE_WON)
        return True
    elif True in [s.player_list[x]['good'] for x in alive] and False in [s.player_list[x]['good'] for x in alive]:
        amor = get_player(s, CUPID_ROLE)
        if amor:
            if len(alive) == 2 and s.player_list[amor]['loving'][0] in alive and s.player_list[amor]['loving'][1] in alive:
                # Das Liebespaar gewinnt
                await s.bot.get_channel(s.game_channel).send(GAME_OVER + COUPLE_WON)
                return True
    elif True not in [s.player_list[x]['good'] for x in alive]:
        # Die Dorfbewohner haben verloren
        white_werewolf = get_player(s, WHITE_WEREWOLF_ROLE)
        if len(alive) == 1:
            if white_werewolf:
                if s.player_list[white_werewolf] in alive:
                    await s.bot.get_channel(s.game_channel).send(GAME_OVER + WHITE_WEREWOLF_WON)
                    return True
        await s.bot.get_channel(s.game_channel).send(GAME_OVER + BAD_WON)
        return True
    elif False not in [s.player_list[x]['good'] for x in alive]:
        # Die Werwölfe haben verloren
        await s.bot.get_channel(s.game_channel).send(GAME_OVER + GOOD_WON)
        return True
    return False


async def reset_vars(s):
    for player in s.player_list:
        await s.bot.get_channel(s.werewolf_channel).set_permissions(player, read_messages=False, send_messages=False)
    for player in s.ready_list:
        s.ww.global_playerlist.remove(player)
    s.ready_list = []
    s.player_list = {}
    s.current_roles = []
    s.died = [None, None, None]
    s.new_vote = False

    s.playerID = None
    s.playing = False
    s.phase = ''

    s.game_status = {'waiting for selection': False, 'selecting': False, 'playing': False}
    s.round_no = 1
