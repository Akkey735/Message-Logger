import threading
import websocket
import datetime
import colorama
import httpx
import json
import time

from plyer import notification

welcome_ascii = '''
██╗░░░░░░█████╗░░██████╗░░██████╗░███████╗██████╗░
██║░░░░░██╔══██╗██╔════╝░██╔════╝░██╔════╝██╔══██╗
██║░░░░░██║░░██║██║░░██╗░██║░░██╗░█████╗░░██████╔╝
██║░░░░░██║░░██║██║░░╚██╗██║░░╚██╗██╔══╝░░██╔══██╗
███████╗╚█████╔╝╚██████╔╝╚██████╔╝███████╗██║░░██║
╚══════╝░╚════╝░░╚═════╝░░╚═════╝░╚══════╝╚═╝░░╚═╝
'''
colorama.init(convert=True)

class Util:
	def __init__(self):
		pass
	
	def get_guild_name(self, token, guild_id):
		try:
			response = httpx.get(f"https://discord.com/api/v9/guilds/{guild_id}", headers={"Authorization": token})
			guild_name = response.json().get("name")
			if guild_name == None:
				return guild_id
			else:
				return guild_name
		except:
			return guild_id
			
	def check_token(self, token):
		try:
			response = httpx.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
			if response.status_code == 200:
				return True
			else:
				return False
		except:
			return False

class MessageLogger:
	def __init__(self, token):
		self.ws = None
		self.token = token
		self.util = Util()
	
	def get_response(self):
		response = self.ws.recv()
		if response:
			return json.loads(response)
			
	def send_request(self, payload):
		self.ws.send(json.dumps(payload))

	def heartbeat(self, interval):
		while True:
			time.sleep(interval)
			heartbeat_payload = {
				"op": 1,
				"d": "null"
			}
			self.send_request(heartbeat_payload)

	def main(self):
		self.ws = websocket.WebSocket()
		self.ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
		
		response = self.get_response()
		
		threading.Thread(target=self.heartbeat, args=(response["d"]["heartbeat_interval"] / 1000,)).start()
		
		payload = {
			"op": 2,
			"d": {
				"token": self.token,
				"properties": {
					"$os": "windows",
					"$browser": "chrome",
					"$device": "pc"
				}
			}
		}
		self.send_request(payload)
		
		while True:
			event = self.get_response()
			try:
				if event["t"] == "READY":
					print(colorama.Fore.GREEN + "Logged in." + colorama.Fore.RESET)
					notification.notify(title="Connected", message="Connected to the server and logged in.")
				elif event["t"] == "MESSAGE_CREATE":
					now_date = datetime.datetime.now()
					now_time = f"{now_date.hour}:{now_date.minute}:{now_date.second}"
					message_author = event["d"]["author"]["username"] + "#" + event["d"]["author"]["discriminator"]
					message_content = event["d"]["content"]
					message_embeds = event["d"]["embeds"]
					message_guild = self.util.get_guild_name(self.token, event["d"]["guild_id"])
					if len(message_embeds) < 1:
						message_embeds = ""
					print(colorama.Fore.LIGHTCYAN_EX + f"[{now_time} | POST | {message_guild}] {message_author}: {message_content}" + colorama.Fore.LIGHTBLUE_EX + f"{message_embeds}" + colorama.Fore.RESET)
				elif event["t"] == "MESSAGE_UPDATE":
					now_date = datetime.datetime.now()
					now_time = f"{now_date.hour}:{now_date.minute}:{now_date.second}"
					message_author = event["d"]["author"]["username"] + "#" + event["d"]["author"]["discriminator"]
					message_content = event["d"]["content"]
					message_embeds = event["d"]["embeds"]
					message_guild = self.util.get_guild_name(self.token, event["d"]["guild_id"])
					if len(message_embeds) < 1:
						message_embeds = ""
					print(colorama.Fore.LIGHTYELLOW_EX + f"[{now_time} | EDIT | {message_guild}] {message_author}: {message_content}" + colorama.Fore.LIGHTBLUE_EX + f"{message_embeds}" + colorama.Fore.RESET)
				elif event["t"] == "MESSAGE_DELETE":
					now_date = datetime.datetime.now()
					now_time = f"{now_date.hour}:{now_date.minute}:{now_date.second}"
					message_guild = self.util.get_guild_name(self.token, event["d"]["guild_id"])
					print(colorama.Fore.LIGHTRED_EX + f"[{now_time} | DELETE | {message_guild}] Message has been deleted." + colorama.Fore.RESET)
			except:
				pass

def main():
	print(colorama.Fore.BLUE + welcome_ascii + colorama.Fore.RESET)
	while True:
		token = input("Token: ")
		print(colorama.Fore.YELLOW + "Checking TOKEN..." + colorama.Fore.RESET)
		result = Util().check_token(token)
		if result:
			break
		else:
			print(colorama.Fore.RED + "The TOKEN is invalid or has been determined to be so for some reason." + colorama.Fore.RESET)
			print(colorama.Fore.YELLOW + "(You may also get this error if you have an invalid Internet connection, rate limitation, or some other glitch.)" + colorama.Fore.RESET)
	print(colorama.Fore.GREEN + "Start logging in." + colorama.Fore.RESET)
	while True:
		try:
			logger_client = MessageLogger(token)
			logger_client.main()
		except:
			pass
		notification.notify(title="Disconnected", message="Connection has been terminated. Attempt to reconnect.")
		
if __name__ == "__main__":
	main()