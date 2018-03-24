import socket

def connection():
	fo = open("cat.jpg", "w")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print('connection created')

	try:
		#s.bind(('10.0.2.15', 5001))
		s.connect(('127.0.0.1', 8080))
	except socket.error:
		print(error)
		s.close()
	else:
		print('sending')
		s.send('''GET http://10.0.3.1:8000/z4d4kWk.jpg HTTP/1.1
	Host: i.imgur.com
	Connection: keep-alive
	Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
	Accept-Language: en-US,en:q=0.5
	Accept-Encoding: gzip, deflate, br
	User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0  ''')
	
	rec = ""
	while True:
		buf = s.recv(1024)
		if(not buf):
			break
		else:
			rec += buf
	l=len(rec)
	fo.write(rec)
	fo.close()
	s.close()

if __name__ == '__main__':
	connection()
