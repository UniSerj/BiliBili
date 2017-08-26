# encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from struct import *
import struct
import requests
import json
import re
import random
import xml.dom.minidom
import socket
import Tool
import threading
import time
import string


CIDInfoUrl='http://live.bilibili.com/api/player?id=cid:'
roomId=0000 #enter the roomID (number) here
roomid='0000' #enter the roomID (string) here
ChatPort=788
protocolVersion=1
ChatHost='livecmt-1.bilibili.com'

alist = [] #name list
mlist = [] #message list
rlist = [] #real-send list

statlist = [] #rank stat list

threads=[] #threads
room_ids=[] #rooms listened on (danmu storm)

class bilibili():
	def __init__(self):
		self.sock = None
		self.counter = 7

	def postMSG(self,message):
		session=requests.Session()
		
		headers={'Accept':'*/*',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
		'Connection':'keep-alive',
		'Content-Type':'application/x-www-form-urlencoded',
		'Cookie':'', # enter the cookie here
		'Host':'live.bilibili.com',
		'Origin':'http://static.hdslb.com',
		'Referer':'http://static.hdslb.com/live-static/swf/LivePlayerEx_1.swf',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
		'X-Requested-With':'ShockwaveFlash/25.0.0.148'}

		params={'color':'16772431','fontsize':'25','mode':'1','msg':message,'rnd':'1485350695','roomid':roomid}

		r=requests.post("http://live.bilibili.com/msg/send",data=params,headers=headers)

	def timeLoop(self):
		while True:
			self.counter = 7
			while self.counter > 0:
				time.sleep(1)
				self.counter=self.counter-1
			if len(alist) != 0:
				if len(alist) > 1:
					RealMsg="感谢米娜投喂的"
					for i in range(len(mlist[0])):
						RealMsg = '%s%s'%(RealMsg,mlist[0][i])
						if i != len(mlist[0])-1:
							RealMsg=RealMsg+"和"
					RealMsg=RealMsg+"喵~"


				else:
					for i in range(len(alist)):
						RealMsg="感谢" + alist[i] + "投喂的"
						for j in range(len(mlist[i])):
							RealMsg = '%s%s'%(RealMsg,mlist[i][j])
							if j != len(mlist[i])-1:
								RealMsg=RealMsg+"和"
						RealMsg=RealMsg+"喵~"

				randon_int = random.randint(0, 7)
				if randon_int == 0:
					RealMsg=RealMsg+"T.T"
				elif randon_int == 1:
					RealMsg=RealMsg+"^∇^"
				elif randon_int == 2:
					RealMsg=RealMsg+"・-・"
				elif randon_int == 3:
					RealMsg=RealMsg+"｀へ´"
				elif randon_int == 4:
					RealMsg=RealMsg+"≧Д≦"
				elif randon_int == 5:
					RealMsg=RealMsg+"￣ω￣"
				elif randon_int == 6:
					RealMsg=RealMsg+" ﾟДﾟ"
				elif randon_int == 7:
					RealMsg=RealMsg+"_(:3」∠)_"
					
				rlist.append(RealMsg)

			for element in rlist:
				self.postMSG(element)
				# time.sleep(1)

			del alist[:]
			del mlist[:]
			del rlist[:]

	def handle_messages(self,user_name,gift_name):
		if len(alist) == 0:
			alist.append(user_name)
			Tmplist = []
			Tmplist.append(gift_name)
			mlist.append(Tmplist)

		elif len(alist) == 1:
			flag1 = False #username_same
			flag2 = False #giftname_same
			for line in range(len(alist)):
				if alist[line] == user_name:
					for k in range(len(mlist[line])):
						if mlist[line][k] == gift_name:
							flag2 = True
					if flag2 == False:
						mlist[line].append(gift_name)

					flag1 = True

			if flag1 == False:
				alist.append(user_name)
				for k in range(len(mlist[0])):
						if mlist[0][k] == gift_name:
							flag2 = True
				if flag2 == False:
					mlist[0].append(gift_name)

		else:
			flag2 = False #giftname_same
			for k in range(len(mlist[0])):
					if mlist[0][k] == gift_name:
						flag2 = True
			if flag2 == False:
				mlist[0].append(gift_name)

	def handle_data(self,data):
		data_length=len(data)
		if data_length < 16:
			print("wrong")
			self.connect()
		else:
			info=struct.unpack("!ihhii" + str(data_length - 16) + "s", data)
			length=info[0]

			if(length<16):
				print("数据错误")
			elif length > 16 and length == data_length:
				action=info[3]-1
				# if action == 2:
				# 	user_count = struct.unpack("!ihhiii", data)[5]
				# 	print("人数:" + str(user_count))
				if action == 4:
					msg_str=info[5].decode("utf-8",'ignore')
					#print (msg_str)

					msg_json=json.loads(msg_str, encoding='utf-8')
					msg_type=msg_json['cmd']
					print(msg_type)

					if msg_type == "DANMU_MSG":
						user_id = msg_json['info'][2][0]
						user_name = msg_json['info'][2][1]
						comment = msg_json['info'][1]
						# print(user_name, comment)


					elif msg_type == "SEND_GIFT":
						gift_name = msg_json['data']['giftName']
						# print(gift_name.decode("utf-8"))
						# print(msg_json['data']['price'])
						# print(msg_json['data']["uname"])

						user_name = msg_json['data']['uname']
						user_id = msg_json['data']['uid']
						gift_num = str(msg_json['data']['num'])
						self.counter = 7


						self.handle_messages(user_name,gift_name)


					elif msg_type == "WELCOME":
						user_id = msg_json['data']['uid']
						user_name = msg_json['data']['uname']

					elif msg_type == "SYS_GIFT":
						#print(msg_str)
						try:
							gift_id = msg_json.get("giftId")

						except BaseException as e:
							print(e)
							pass

					elif msg_type == "SYS_MSG":
						# print(msg_json)
						try:
							real_roomid = msg_json.get("real_roomid")
							print(real_roomid)
							self.SmallTV(real_roomid,'1495083008640')
						except BaseException as e:
							pass




			elif 16 < length < data_length:
				#print("long data")
				single_data=data[0:length]
				threading.Thread(target=self.handle_data, args=(single_data,)).start()
				# self.handle_data(data)
				remain_data=data[length:data_length]
				threading.Thread(target=self.handle_data, args=(remain_data,)).start()
				# self.handle_data(data)

	def connect(self):
		# writer=asyncio.open_connection(ChatHost,ChatPort)
		print("connecting......")
		uid= (int)(100000000000000.0 + 200000000000000.0*random.random())
		body='{"roomid":%s,"uid":%s}' % (roomId, uid)

		bytearr = body.encode('utf-8')
		print(bytearr)
		packetlength=len(bytearr)+16
		sendbytes=pack('!IHHII', packetlength, 16, protocolVersion, 7, 1)
		if len(bytearr) != 0:
		    sendbytes = sendbytes + bytearr

		while 1:
			try:
				cid_info_xml=str(Tool.http_get(CIDInfoUrl + roomid))
				break
			except:
				continue

		start = cid_info_xml.find("<server>") + len("<server>")
		end = cid_info_xml.find("</server>", start)
		if 0 < start < end:
		    socket_server_url = cid_info_xml[start:end]

		#connect
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((socket_server_url, 788))
		self.sock.send(sendbytes)

	def send_heart_beat_msg(self):
		loop_count = -1
		while 1:
			time.sleep(1)
			loop_count += 1
			if loop_count > 20 or loop_count == 0:
				sendBytes=pack('!IHHII', 16, 16, protocolVersion, 2, 1)

				self.sock.send(sendBytes)
				loop_count = 0
			# self.sock.close()
			# print("与服务器的连接已关闭")

	def recv_msg_loop(self):
		while 1:
			try:
				recv_data=self.sock.recv(10240)
			except:
				self.sock.close()
				self.connect()
			self.handle_data(recv_data)

	def SmallTV(self,room_id,TV_rnd):
		url = 'http://live.bilibili.com/SmallTV/index?roomid=' + str(room_id)
		header = {
		'Accept':'application/json, text/javascript, */*; q=0.01',
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
		'Connection':'keep-alive',
		'Cookie':'',# enter the cookie here
		'Host':'live.bilibili.com',
		'Referer':'http://live.bilibili.com/'+room_id,
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
		'X-Requested-With':'XMLHttpRequest'
		}
		r = requests.post(url,headers = header)
		data = r.text
		data = json.loads(data)
		TV_id = data['data']['unjoin']
		TV_id = TV_id[0]['id']
		# print(TV_id)

		R_url = "http://api.live.bilibili.com/SmallTV/join?roomid="+str(room_id)+'&id='+str(TV_id)+'&_='+str(TV_rnd)
		# print(R_url)
		Referer = "http://live.bilibili.com/"+str(TV_id)
		R_header = {
		'Accept':'application/json, text/javascript, */*; q=0.01',
		'Accept-Encoding':'gzip, deflate, sdch',
		'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
		'Connection':'keep-alive',
		'Cookie':'',# enter the cookie here
		'Host':'api.live.bilibili.com',
		'Origin':'http://live.bilibili.com',
		'Referer':Referer,
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
		} 
		params = {'roomid':str(room_id),'id':str(TV_id),'_':TV_rnd}
		r = requests.post(R_url,data=params,headers = R_header)
		print(r.text)


	def active_threads(self):
		while 1:
			print("active threads: "+str(threading.active_count()))
			time.sleep(30)


if __name__ == '__main__':
	Bilibili=bilibili()
	Bilibili.connect()
	t1=threading.Thread(target=Bilibili.timeLoop)
	threads.append(t1)
	t2=threading.Thread(target=Bilibili.recv_msg_loop)
	threads.append(t2)
	t3=threading.Thread(target=Bilibili.send_heart_beat_msg)
	threads.append(t3)
	t4=threading.Thread(target=Bilibili.getrank)
	threads.append(t4)

	for t in threads:
		t.start()

