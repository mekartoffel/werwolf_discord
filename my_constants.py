#allgemein
NOT_UNDERSTAND = 'Ich verstehe deine Eingabe nicht.\n'
NOT_A_NUMBER = 'Das war keine Zahl.\n'
NOT_ALIVE = 'Die Person lebt leider nicht mehr...\n'
#INPUT_ONE = 'Benutze dafür bitte den __globalen oder Servernamen der Person (*ohne* `@`).__'
INPUT_ONE = '\nZur Wahl gibt es folgende Personen: \n{options}\n'
#INPUT_MORE = 'Benutze dafür bitte den __globalen oder Servernamen der Personen (*ohne* `@`)__ und trenne mit einem *Komma*.'
INPUT_MORE = '\nZur Wahl gibt es folgende Personen: \n{options} \nTrenne mit einem Komma.\n'

#rollen
THIEF_ROLE = 'Dieb'
CUPID_ROLE = 'Amor'
WILD_CHILD_ROLE = 'Wildes Kind'
HEALER_ROLE = 'Heiler'
SEER_ROLE = 'Seherin'
WEREWOLF_ROLE = 'Werwolf'
WHITE_WEREWOLF_ROLE = 'Weißer Werwolf'
WITCH_ROLE = 'Hexe'
JUDGE_ROLE = 'Stotternder Richter'
SCAPEGOAT_ROLE = 'Sündenbock'
IDIOT_ROLE = 'Dorfdepp'
HUNTER_ROLE = 'Jäger'
OLD_MAN_ROLE = 'Alter Mann'

#phasen
THIEF_PHASE = 'THIEF'
CUPID_PHASE = 'CUPID'
WILD_CHILD_PHASE = 'WILD CHILD'
HEALER_PHASE = 'HEALER'
SEER_PHASE = 'SEER'
WEREWOLVES_PHASE = 'WEREWOLVES'
WEREWOLVES_PHASE_CONFIRM = 'WEREWOLVES_CONFIRMING'
WHITE_WEREWOLF_PHASE = 'WHITE_WEREWOLF'
WITCH_PHASE_HEAL = 'WITCH_HEAL'
WITCH_PHASE_KILL = 'WITCH_KILL'
VOTING_PHASE = 'VOTING'
HUNTER_PHASE_NIGHT = 'HUNTER_NIGHT'
HUNTER_PHASE_VOTE = 'HUNTER_VOTE'

#commands
WHICH_ROLES = 'Es gibt folgende Rollen: {role_list}'
WHOS_READY = 'Bereit sind:\n{players}'
STILL_ALIVE = 'Es leben noch:\n{alive}'
NO_INFO = 'Darüber kann ich dir keine Auskunft geben.'
MISSING_VOTES = 'Noch nicht abgestimmt haben:\n{players}'
NOT_VOTING = 'Es wird gerade gar nicht abgestimmt.'

#start
NO_ONE_READY = 'Es ist noch keiner bereit.'
READY = '{player} ist bereit!'
NOT_READY = '{player} ist nicht mehr bereit!'
ALREADY_READY = 'Du bist schon bereit.'
ALREADY_SOMEWHERE = 'Du bist schon in einem anderen Server dabei.'
GAME_STARTED = '{player} hat das Spiel gestartet und wählt somit, welche Rollen dabei sind. Mitspieler sind:{other_players}'
WAITING_FOR_ROLES = '{player}, gib {number_players} Rolle(n) ein. Wenn der Dieb dabei sein soll, dann gib noch 2 zusätzliche Rollen ein. Trenne mit einem Komma, z.B. \"Rolle1, Rolle2, Rolle3\"'
ALREADY_PLAYING = 'Es findet gerade ein Spiel statt.'
NOT_ENOUGH_PLAYERS = 'Es sind noch nicht genügend Spieler. Es sollte(n) noch mindestens {missing} Spieler dazukommen.'

SOMETHING_WRONG = 'Da stimmt etwas nicht. ' + WAITING_FOR_ROLES
ROLES = 'Die Rollen sind also ```\n{roles}\n```Ist das so richtig?'
ROLES_AGAIN = 'Gib die Rollen noch einmal ein. Trenne mit einem Komma.'
DISTRIBUTING_ROLES = 'Okay, dann verteile ich jetzt die Rollen.'
ROLE_FOR_PLAYER = 'Du hast folgende Rolle: {role}'
NEW_WW_CHANNEL = 'Es wurde ein neuer Kanal für dich und die anderen Werwölfe freigeschalten: <#{channel_id}>'
NEW_WW = '{player} gehört nun zu den Werwölfen!'

GOING_TO_SLEEP = 'Die Nacht legt sich still über euer Dorf. Alle Dorfbewohner begeben sich zur Ruhe und schließen die Augen.'

CANT_VOTE = '{player}, du darfst gar nicht mehr wählen.'
NOT_ALLOWED = '{player}, diesen Spieler kannst du nicht wählen.'

#dieb
THIEF_WAKE = 'Der **Dieb** wacht auf. Er ist sehr unzufrieden mit sich selbst und möchte sich deshalb eine der übrigen Identitäten stehlen.'
THIEF_OPTIONS = 'Du hast folgende Rollen zur Auswahl: {roles}'
THIEF_CHOSE_WRONG = 'Das war keine der zur Wahl stehenden Identitäten. Bitte wähle noch einmal.'
THIEF_CHOSE = 'Okay, du hast nun folgende Identität: {role}'
THIEF_FINISHED = 'Der **Dieb** hat eine Identität gestohlen und geht zufrieden schlafen.'

#amor
CUPID_WAKE = '**Amor** wacht auf. Er hat auf einmal große Lust, zwei Leute mit seinen Liebespfeilen abzuschießen, um ein bisschen mehr Spannung in seinem Leben zu haben.'
CUPID_INPUT = 'Wen möchtest du mit deinen Liebespfeilen abschießen? __(Schicke mir bitte die **Zahl** der Personen, die du abschießen möchtest.)__ ' + INPUT_MORE
CUPID_CHOSE_COUPLE = 'Okay, die beiden sind nun verliebt: {couple}'
NOTIFY_LOVER = 'Du bist jetzt verliebt in {other_lover} '
CUPID_FINISHED = '**Amor** hat sich zwei Personen ausgesucht, die sich ineinander verlieben sollen und geht in Ruhe schlafen.'

#wildes kind
WILD_CHILD_WAKE = 'Das **wilde Kind** wacht auf. Es sucht sich ein Vorbild. Wenn dieses stirbt, kehrt das wilde Kind zurück zu den Werwölfen und wird deren Verbündeter.'
WILD_CHILD_INPUT = 'Wer soll dein Vorbild sein? __(Schicke mir bitte die **Zahl** der Person, die dein Vorbild sein soll.)__' + INPUT_ONE
WILD_CHILD_CHOSE = 'Okay, diese Person ist nun dein Vorbild: {player}'
WILD_CHILD_FINISHED = 'Das **wilde Kind** hat sich ein Vorbild ausgesucht und geht wieder schlafen.'
WILD_CHILD_RM_DIED = 'Dein Vorbild ist gestorben. Du agierst jetzt als Werwolf.'

#heiler
HEALER_WAKE = 'Der **Heiler** erwacht. Er hat ein ganz ungutes Gefühl und möchte deshalb diese Nacht jemanden beschützen.'
HEALER_INPUT = 'Welche Person möchtest du beschützen? __(Schicke mir bitte die **Zahl** der Person, die du beschützen möchtest.)__' + INPUT_ONE + '(Du kannst auch dich selbst schützen.)'
HEALER_CHOSE = 'Okay, diese Person beschützt du heute Nacht: {player}'
HEALER_SAME_IN_ROW = 'Du kannst nicht zwei Mal hintereinander dieselbe Person schützen. Wähle bitte jemand anderes.'
HEALER_FINISHED = 'Der **Heiler** hat eine Person gefunden, die es würdig ist, beschützt zu werden und geht wieder schlafen.'

#seherin
SEER_WAKE = 'Die **Seherin** wacht auf. Sie verdächtigt jemanden und möchte deshalb die Identität dieser Person in Erfahrung bringen.'
SEER_INPUT = 'Wen möchtest du überprüfen? __(Schicke mir bitte die **Zahl** der Person, deren Identität du wissen möchtest.)__' + INPUT_ONE
SEER_SEE_ROLE = '{player} hat folgende Identität: {role}'
SEER_FINISHED = 'Die **Seherin** hat etwas Interessantes gesehen und geht wieder schlafen.'

#werwolf
WEREWOLVES_WELCOME = 'Willkommen!\n{werewolves}, ihr seid für diese Runde die Werwölfe. Hier ist Raum für euch zum Diskutieren und Abstimmen.'
WEREWOLVES_WAKE = 'Die **Werwölfe** wachen auf und haben richtig Hunger. Sie müssen sich nur noch einigen, wen sie diese Nacht fressen wollen.'
WEREWOLVES_INPUT = ', wer soll gefressen werden? __(Schickt mir bitte die **Zahl** der Person, die gefressen werden soll.)__' + INPUT_ONE + 'Wenn jemand nicht wählen will oder kann, kann er auch `Enthaltung` eingeben.\nIhr könnt euch auch vorher absprechen.'
WEREWOLVES_LOVE = 'Du kannst deinen Liebespartner doch nicht fressen! 💔'
WEREWOLVES_DONT_CARE = '{player} ist es egal.'
WEREWOLVES_CHOSE = '{player} möchte folgende Person fressen: {victim}'
WEREWOLVES_WHO_TO_KILL = 'Ich weiß jetzt nicht genau, wen ihr umbringen wollt, könnt ihr nochmal stimmen?'
WEREWOLVES_CONFIRM = 'Wollt ihr folgende Person fressen: {victim}? (Es reicht, wenn einer von euch \"Ja\" bzw. \"Nein\" antwortet, sprecht euch also ab!)'
WEREWOLVES_VOTE_AGAIN = 'Okay, wer soll gefressen werden? (Nur, wer seine Meinung ändert, sollte nochmal seine Stimme ändern.)'
WEREWOLVES_FINISHED = 'Die **Werwölfe** haben ihr Opfer gefunden und gehen wieder schlafen.'

#weisser werwolf
WHITE_WEREWOLF_WAKE = 'Der **weiße Werwolf** erwacht. Er möchte eventuell einen seiner Werwolf-Kameraden fressen.'
WHITE_WEREWOLF_INPUT = 'Wen möchtest du fressen? __(Schicke mir bitte die **Zahl** der Person, die du fressen möchtest.)__' + INPUT_ONE + '(Wenn du niemanden fressen möchtest, antworte mit `Niemanden`)'
WHITE_WEREWOLF_NOT_COMRADE = 'Die Person ist keiner deiner Werwolf-Kameraden...\n' + WHITE_WEREWOLF_INPUT
NO_COMRADE_LEFT = 'Es ist kein anderer Werwolf am Leben, also gehst du wieder in Ruhe schlafen.'
WHITE_WEREWOLF_LOVE = 'Du kannst deinen Liebespartner doch nicht fressen! 💔'
WHITE_WEREWOLF_FINISHED = 'Der **weiße Werwolf** hat einen seiner Kameraden gefressen (oder auch nicht) und geht wieder schlafen.'

ATE = 'Folgende Person wurde gefressen: {victim}'

#hexe
WITCH_WAKE = 'Die **Hexe** wacht durch die Geräusche auf, die die Werwölfe verursacht haben. Sie sieht sich im Dorf um.'
WITCH_ALREADY_HEALED = 'Deinen Heiltrank hast du bereits genutzt.'
WITCH_INPUT_HEAL = ' ist gestorben. Möchtest du diese Person mit deinem Heiltrank retten?'
WITCH_HEALED = '{player} wurde von dir gerettet!'
WITCH_NOT_HEALED = '{player} wurde nicht von dir gerettet.'
WITCH_ALREADY_KILLED = 'Deinen Gifttrank hast du schon genutzt. Also gehst du wieder schlafen.'
WITCH_KILLED = 'Du hast folgende Person vergiftet: {victim}'
WITCH_NO_TRANKS = 'Du hast keine Tränke mehr, die du nutzen kannst. (Wir warten jetzt pseudomäßig trotzdem. 😈)'
WITCH_INPUT_KILL = 'Möchtest du noch jemanden mit deinem Gifttrank vergiften? __(Schicke mir bitte die **Zahl** der Person, die du töten möchtest.)__' + INPUT_ONE + '(Wenn du niemanden töten willst, antworte einfach mit `Nein`)'
WITCH_LOVE = 'Du kannst deinen Liebespartner doch nicht vergiften! 💔'
WITCH_NO_KILLING = 'Du willst niemanden vergiften und gehst wieder schlafen.'
WITCH_FINISHED = 'Die **Hexe** hat eventuell einen oder beide ihrer Tränke verwendet und geht wieder schlafen.'

#tag
MORNING = 'Die Sonne geht auf und der Tag bricht an. Alle wachen auf.'
WHO_DIED = '{}\nEs ist gestorben: {}'
NO_ONE_DIED = 'Niemand ist gestorben! 🎉'
COUPLE_DIES = 'Da {td} gestorben ist, stirbt nun auch {loving} ({role}). 💔'
CITIZENS_SLEEP = 'Nach diesem anstrengenden Tag gehen alle wieder schlafen.'

JUDGE_NEW_VOTE_POSSIBLE = 'Bis zum Ende der ersten Abstimmung kannst du mir mit der Nachricht `ABSTIMMUNG` sagen, dass du noch eine zweite Abstimmung direkt nach der ersten Abstimmung möchtest'
JUDGE_NO_VOTE_POSSIBLE = 'Die Abstimmung ist beendet und du kannst diese Runde keine zweite Abstimmung herbeiführen.'
JUDGE_NEW_VOTE = 'Der stotternde Richter hat eine neue Abstimmungsrunde angeordnet! Ihr müsst also sofort erneut jemanden wählen, den ihr hinrichten wollt. (Wenn sich jemand entschieden hat, die gewünschte Person bitte mit einem `@` taggen.)'
NEW_VOTE_ANSWER = 'Okay, es wird eine zweite Abstimmung geben.'

ANGRY_MOB = 'In eurer Stadt passieren seltsame Dinge und ihr seid alle ein wütender Mob mit Fackeln 🔥 und Mistgabeln 🍴. Ihr wollt jemanden wählen, den ihr verbrennen (oder aufspießen) könnt. (Wenn sich jemand entschieden hat, die gewünschte Person bitte mit einem `@` taggen.)\nACHTUNG: Es gibt nur eine Wahlrunde, also entscheidet weise (und denkt ggf. an Dorfdepp und Sündenbock)!'
VOTED_FOR = '{player} hat für {chosen} abgestimmt!'
CITIZEN_LOVE = 'Du kannst doch nicht gegen deinen Liebespartner stimmen! 💔'
ALREADY_DEAD = '{player}, dieser Spieler ist schon tot. Du kannst ihn nicht wählen.'
VOTED = 'So habt ihr bisher abgestimmt:\n{votes}'
VOTE_FINISHED = 'So habt ihr abgestimmt:\n{votes}'
VOTE_SCAPEGOAT = 'Ihr konntet euch nicht einig werden. Deshalb muss der Sündenbock, also {scapegoat} sterben.'
VOTE_DRAW = 'Ihr konntet euch nicht einig werden und da es keinen Sündenbock gibt, stirbt heute niemand mehr.'
VOTE_VICTIM = 'Die Abstimmung hat ergeben, {victim} zu töten.'
VOTE_IDIOT = 'Ihr habt den Dorfdeppen erwischt! Er stirbt nicht, verliert aber ab jetzt sein Stimmrecht.'
PLAYER_DIED = '{player} ({role}) ist gestorben.'

#jaeger
HUNTER_DIED = 'Der Jäger ist gestorben. '
HUNTER_INPUT = ', wen möchtest du als letzte Tat noch mit dir in den Tod reißen? Tagge die gewünschte Person bitte mit einem `@`'
HUNTER_CHOSE = 'Der Jäger hat folgende Person mit sich in den Tod gerissen: {victim}'

#alter mann
OLD_MAN_DIED = ' den **alten Mann** getötet! Aus Verzweiflung, einen solch hochgelehrten Mann verloren zu getötet zu haben, verlieren alle Dorfbewohner ihre besonderen Fähigkeiten. *Alle sind nun gewöhnliche Dorfbewohner*.'

#spiel beendet
GAME_OVER = '*Das Spiel ist beendet!* '
BAD_WON = 'Die **Werwölfe** haben gewonnen! '
GOOD_WON = 'Die **Dorfbewohner** haben gewonnen! '
COUPLE_WON = 'Das **Liebespaar** hat gewonnen! '
WHITE_WEREWOLF_WON = 'Der **weiße Werwolf** hat gewonnen! '
NOONE_WON = '___Alle___ sind gestorben. Es gibt keinen Gewinner, nur Verlierer. :('