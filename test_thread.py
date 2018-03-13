import threading
import socket


def new_socket(port, range_num): #which port to send,

	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	GET_request = 'GET /z4d4kWk.jpg HTTP/1.1\r\nHost: i.imgur.com\r\nRange: bytes='+range_num+'\r\nConnection: close\r\n\r\n'
	print'the GET is %s \n'%GET_request
	total = ''
	ip = get_host_ip()
	print('starting......' + str(port))

	try:
		proxy_socket.bind((ip, port))
		proxy_socket.connect(('151.101.52.193',80))
		print('connected to host')
	except socket.error:
		print("fail to connect to server" + str(port))
		proxy_socket.close()
	else:
		print("sending range request " + str(port))
		proxy_socket.send(GET_request) #send range request

		print("reading from server "+ str(port))
		while True:
			buf = proxy_socket.recv(1024)
			if(not buf):
				break
			else: 
				total += buf
	proxy_socket.close()
	print('header location') 
	print(total.find('\r\n\r\n'))
	
	header = total[:total.find('\r\n\r\n')]
	content = total[total.find('\r\n\r\n')+4:]
	#header, content = total.split('\r\n\r\n',1)
	print(header)
	print 'content length %s'%len(content)
        order1 = header.find('Content-Range')
        order2 = header[order1+13:].find('-')
        order = header[order1+21:order1+order2+13]
	print 'port is %s'%str(port)
	print 'order is %s '%str(order) 
        #extract the data and range length
        merge_data[order] = content
	
	#thread.exit_thread()
def get_host_ip():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
	finally:
		s.close()

	return ip
if __name__ == '__main__':
	merge_data = {}
	buf = ''
	try:
		t1 = threading.Thread(target = new_socket, args = (5001,'0-100000'))
		t2 = threading.Thread(target = new_socket, args = (5002,'100000-146515'))
		t1.start()
		t2.start()
		t1.join()
		t2.join()
	except:
		print('unable to create thread')
	ordered_data = sorted(merge_data.keys())
	for i in ordered_data:
		buf +=merge_data[i]
		print('order in process')
		print(len(merge_data[i]))
	f = open("cat.jpg", "w")
	print(len(buf))
	f.write(buf)
	f.close()
	#print(len(buf))











	
