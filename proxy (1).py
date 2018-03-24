import socket, threading, select, fcntl,struct, os
import thread
import urllib2
import requests
import time
import hashlib
merge_data = {}
BUFLEN = 8192
content_length = 0
class ConnectionHandler:
	def __init__(self, connection, address, timeout):
		self.client = connection
		self.client_buffer = ''
		self.timeout = timeout
		self.buffer = ''
		print(content_length)
		self.method, self.path, self.protocol = self.get_base_header()
		if self.method=='CONNECT':
			self.method_CONNECT()
		elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):
			self.method_others()
		
		self.client.close()

	def get_base_header(self):
		while 1:
			self.client_buffer += self.client.recv(BUFLEN)
			end = self.client_buffer.find('\n')
			if end!=-1:
				break

		print '%s'%self.client_buffer[:end]#debug

		data = self.client_buffer[:end+1].split()
		self.client_buffer = ''
		return data

	def get_host_ip(self,ifname):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

	def new_socket(self, ip, port, host, path, range_num):  # which port to send,

		proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#GET_request = 'GET /elephant.jpg HTTP/1.1\r\nRange: bytes='+range_num+'\r\nConnection: close\r\n\r\n'
		GET_request = 'GET '+ path +' HTTP/1.1\r\nRange: bytes=' + range_num + '\r\nConnection: close\r\n\r\n'
		print 'GET is %s'%GET_request
		total = ''
		#ip = self.get_host_ip()

		try:
			proxy_socket.bind((ip, port))
			if(ip == '10.0.1.1'):
				proxy_socket.connect(('10.0.3.1',8000))
			if(ip == '10.0.2.1'):
				proxy_socket.connect(('10.0.3.1',8000))
			print 'connected to %d'%port
		except socket.error:
			print("fail to connect to server")
			proxy_socket.close()
		else:
			print("sending range request\n " + str(port))
			proxy_socket.send(GET_request)  # send range request

			print("reading from server \n")
			while True:
				buf = proxy_socket.recv(1024)
				if(not buf):
					break
				else:
					total += buf
		
		proxy_socket.close()
		print'hte location is '
		print(total.find('\r\n\r\n'))
		header = total[:total.find('\r\n\r\n')]
		content = total[total.find('\r\n\r\n')+4:]
		print('ocntent length is %s'%len(content))
		#header, content = total.split('\r\n\r\n',1)
		order1 = header.find('Content-Range')
		order2 = header[order1+13:].find('-')
		order = header[order1+21:order1 + order2 + 13]
		print 'the order is %s'%str(order)
		merge_data[order] = content
		print(header)
		#print 'content length %s'%len(content)
		print 'port is %s'%str(port)
		#print 'order is %s '%str(order)
	def method_others(self):
		addr = self.path
		self.path = self.path[7:]
		i = self.path.find('/')
		host = self.path[:i]
		path = self.path[i:]
		print ('path splited+++++++++++++')
		print('the host is %s'%host)
		print'the path is %s'%path		
		length = self.get_header(host, path)
		length_2 = int(length)/2
		range_1  = '0-' + str(length_2)
		range_2 = str(length_2) + '-' +  length
		ip_addr = {}
		ip_addr[0] ='10.0.1.1' # self.get_host_ip('eth0')
		ip_addr[1] ='10.0.2.1' #self.get_host_ip('eth1')
		m = hashlib.md5()
                m.update(host + path)
                cache_filename = m.hexdigest() + '.cached'
		start_time = time.time()
                if os.path.exists(cache_filename):
                        print'cacahe hit!!!'
                        data = open(cache_filename).readlines()
                        self.client.send(str(data))
			#print data
			elapse_time = time.time() - start_time
			print '-----------------------------------\n'
			print 'the elapse time is %s'%elapse_time
			print '\n----------------------------------\n'
                        return
		try:
			t1 = threading.Thread(target= self.new_socket, args= (ip_addr[0], 0, host, path, range_1,))
			t2 = threading.Thread(target= self.new_socket, args= (ip_addr[1], 0, host, path, range_2,))
			t1.start()
			t2.start()
			t1.join()
			t2.join()
		except:
			print('unable to connect')
		else:
			self.read_write()
			
			elapse_time = time.time() - start_time
			print '-------------------------\n'
			print 'the time span is %s'%elapse_time
			print '\n------------------------\n'
	def read_write(self):
		buf = ''
		ordered_data = sorted(merge_data.keys())
		for i in ordered_data:
			buf += merge_data[i]
		print '-----------------------------------------------the buf is %s'%len(buf)

		#self.client.send(buf)
		i = self.path.find('/')
		host = self.path[:i]
		path = self.path[i:]
		m = hashlib.md5()
		m.update(host + path)
		cache_filename = m.hexdigest() + '.cached'
		self.client.send(buf)
		open(cache_filename, 'wb').writelines(buf)
	def get_header(self, host, path):
		url = 'http://' + host +  path
		response = urllib2.urlopen(url)
		info = response.info()
		length = info['Content-Length']
		return length
		
def start_server(host='localhost', port=8080, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type)
    soc.bind((host, port))
    print "Serving on %s:%d."%(host, port)#debug
    soc.listen(0)
    while 1:
        thread.start_new_thread(handler, soc.accept()+(timeout,))

if __name__ == '__main__':
   # content_length = get_header()
    start_server()
    print('something')
