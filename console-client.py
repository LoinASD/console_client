#!/usr/bin/python

import requests
import uuid
import getpass
import re
from FHQFrontEndLib import FHQFrontEndLib
from datetime import datetime


class FHQ():
	def __init__(self):
		self.choosed_game = ''
		self.choosed_quest = ''
		self.email = ''
		self.url = 'http://fhq.sea-kg.com/api/'
		self.api = FHQFrontEndLib(self.url)
		self.allFunc = {
			r"t(ime)?"                            : self.time,
			r"i(nfo)?"                            : self.info,
			r"ch(ange|oose)?\-?serv"              : self.choose_serv,
			r'ch(ange|oose)?\-?g(ame)?'           : self.choose_game,
			r"l?g(ame)?\-?l(ist)?"                : self.games_list,
			r"l?q(uests?)?\-?l(ist)?"             : self.quests_list,
			r"l(o?g)?in"                          : self.login,
			r"sh(ow)?\-?q(uest)?"                 : self.show_quest,
			r"l(o?g)?out"                         : self.logout,
			r"ch(ange)?\-?p(ass)?(w(or)?d)?"      : self.change_password,
			r"u(ser)?\-?i(nfo)?"                  : self.user_info,
			r"(sc?(ore)?|l(ead(er)?)?)b(oar)?d?"  : self.scoreboard,
			#r"ev?(ents?)?l(ist)?"                 :events_list
		}

	def login(self, mail = None):

		if not mail:
			self.email = raw_input("Email: ")
			self.password = getpass.getpass('Password: ')
		else:
			self.email = mail
			self.password = getpass.getpass('Password: ')

		if not self.api.security.login(self.email, self.password):
			exit(1)
		self.token = self.api.token

	def choose_serv(self, ur = None):
		if not ur:
			print("1: http://fhq.sea-kg.com/api/\n2: http://fhq.keva.su/api/\n3: http://localhost/fhq/api/")
			numsrv = raw_input("Please choose server: ")
			domens = ['http://fhq.sea-kg.com/api/', 'http://fhq.keva.su/api/', 'http://localhost/fhq/api/']

			try:
				self.url = domens[int(numsrv) - 1 or 0]
			except ValueError:
				print 'Wrong domen'
				return

			print "Choosed: ", self.url

		else:
			self.url = ur
		self.api = FHQFrontEndLib(self.url)
		self.login(self.email)
		print('Your token: ' + self.token)

	def games_list(self, none = None):
		glist = self.api.games.list()["data"]
		for g in glist:
			print "%s)  %s \t (%s) " % (glist[g]["id"] ,glist[g]["title"],glist[g]["type_game"])

	def choose_game(self, game = None):
		# global self.choosed_game
		if game:
			try:
				choosed_gameid = int(game)
			except:
				print "unknown id"
				self.games_list()
				choosed_gameid = int(raw_input("Please choose game: "))
		else:
			self.games_list()
			choosed_gameid = int(raw_input("Please choose game: "))
		game = self.api.games.choose(choosed_gameid)
		self.choosed_game = game['data']['title']
		print('Choosed game ' + game['data']['title'])
		print

	def quests_list(self, none = None):
		if not self.choosed_game:
			self.choose_game()
		quests = self.api.quests.list({'filter_completed' : True, 'filter_open' : True, 'filter_current' : True})
		formattablequests = '{:<8}|{:<15}|{:<20}|{:<10}|{:<5}'
		print "\n"+formattablequests.format('Quest ID', 'Subject + Score', 'Name', 'Status', 'Solved')
		print formattablequests.format('--------', '---------------', '--------------------', '----------', '-----')
		for key, value in enumerate(quests['data']):
			print formattablequests.format(value['questid'], value['subject'] + ' ' + value['score'], value['name'], value['status'], value['solved'])
		print

	def time(self, none = None):
		print datetime.now().strftime('%d/%m/%y::%H:%M:%S')

	def show_quest(self, questid = None):
		if not questid:
			self.quests_list()
			questid = raw_input('Chooce Quest: ')
		quest = self.api.quests.get(questid)
		print '   Subject: ' + quest['data']['subject']
		print '     Score: ' + quest['data']['score']
		print '      Name: ' + quest['data']['name']
		print '    Author: ' + quest['data']['author']
		print '      Text: '
		print quest['data']['text']
		print

	def pass_quest(self, string = None):
		if re.match(r'^([0-9]+) (.*)$', string):
			match = re.match(r'^([0-9]+) (.*)$', string)
			questid = match.group(1)
			answer = match.group(2)
			result = self.api.quests.trypass(questid, answer)
			if result['result'] == 'ok':
				print "quest passed"
			else:
				print result['error']['message']
		else:
			print "unknown command"

	def info(self, none = None):
		i = r.get(self.url + 'public/info.php').json()
		if i["result"] == "ok":
			print "Sucssess..."
			print "Lead Time (sec):", i["lead_time_sec"]
			data = i["data"]
			print "Cities:   ",
			for city in data["cities"]:
				print city, ", ",
			quests = data["quests"]
			print
			print "Quests: %s  " % quests["count"],
			print "All attempts: %s  " % quests["attempts"],
			print "Solved: %s  " % quests["solved"]
			win = data["winners"]
			for game in win:
				print game + ": "
				gam = win["%s" % game]
				for user in gam:
					print "    ", user["user"], " --> ", user["score"]
		else: print "error"

	def logout(self, none = None):
		out = {"token":self.api.token}
		requests.post(self.url+"security/logout.php", params=out)

	def change_password(self, none = None):
		old_pass = getpass.getpass("Password: ")
		new_pass = getpass.getpass("New Password: ")
		confirm = getpass.getpass("Confirm new Password: ")
		p = {
			'old_password':          old_pass,
			"new_password":          new_pass,
			"new_password_confirm":  confirm,
			"token":                 self.token
		}
		if requests.post(self.url+"users/change_password.php", params=p).json()["result"] == "ok":
			print "Success!"
		else:
			print "Fail"

	def user_info(self, uid = None):
		if not uid:
			uid = raw_input("user id: ")
		answ = requests.post(self.url+"users/get.php", params={'userid':uid, "token":token}).json()
		data = answ[u"data"]
		for key in data: print "\n%s :  %s" % (key, data[key])

	def scoreboard(self, gid = None):
		if not gid:
			gid = raw_input('Enter gameid: ')
		answ = requests.post(self.url+'games/scoreboard.php', params={"token":token, "gameid":gid}).json()
		data = answ["data"]
		formattable = '{:<7}|{:<4}|{:<20}|{:<7}'
		print "\n"+formattable.format(" Place ", " ID ", "        Nick        ", " Score ")
		print formattable.format("-------","----","--------------------","-------")
		for place in data:
			for users in data[place]:
				while len(users["nick"])<19:
					users["nick"] += " "
				print "   %s   | %s | %s| %s" %(place, users["userid"], users["nick"], users["score"])
				# for user in data:
				# 	print 'place  | {userid:<2} | {nick:<18} | {score:<5}'.format(**data[place][users][0])


fhq = FHQ()

fhq.login('levkiselev@gmail.com')
print "All commands types conjoint or with hyphen.\nUsage: <command|two-words-command> [params]\nType 'help' for commands list."

while True:
	command = raw_input(fhq.choosed_game + "/" + fhq.choosed_quest + "> ")
	if command == "exit" or command =="ex": break
	elif command == "h" or command == "help":
		for func in fhq.allFunc:
			print func + '\t\t%s' % fhq.allFunc[func].__name__
	else:
		cmds = command.split()
		fcmd = cmds.pop(0)
		scmd = " ".join(cmds)
		for i in fhq.allFunc:
			if re.match(i, fcmd+scmd):
				fhq.allFunc[i](scmd)