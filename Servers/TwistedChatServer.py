from twisted.protocols import basic
from twisted.internet import reactor, protocol

class ChatProtocol(basic.LineReceiver):
	def __init__(self):
		self.connections_established = {}
		self.port = 0
		self.host = ''
	
	def connectionMade(self):
		self.port = self.transport.getPeer().port
		self.host = self.transport.getPeer().host		
		self.transport.write('SERVER MESSAGE :\nRules :\n1.Select an IP to start chat : start IP PORT\n2.To send a new Message : send IP PORT MESSAGE\n')
		for all_clients in self.factory.clients:
			self.transport.write('(' + all_clients.host + ',' + str(all_clients.port) + ')\n')
			all_clients.transport.write('SERVER MESSAGE : New Person Online - (' + self.host + ',' + str(self.port) + ')\n')

		for all_clients in self.factory.live_lec_hosts:
			self.transport.write('{' + all_clients.host + ',' + str(all_clients.port) + '}\n')

        	self.factory.clients.append(self)
		
    	def connectionLost(self, reason):
		for all_clients in self.factory.clients:
			all_clients.transport.write('SERVER MESSAGE : Person Offline - (' + self.host + ',' + str(self.port) + ')\n')		
		self.factory.clients.remove(self)
		if self in self.factory.live_lec_hosts:
			self.factory.live_lec_hosts.remove(self)

    	def lineReceived(self, line):
		command = line.split()[0]
		ip = line.split()[1]
		port = line.split()[2]
		if command == 'start':
			k = 0
			for all_ip in self.factory.clients:
				if int(port) == all_ip.port and ip == all_ip.host and all_ip != self:
					self.connections_established[ip + ',' + port] = all_ip
					self.transport.write('SERVER MESSAGE : Connections Established with (' + all_ip.host + ',' + str(all_ip.port) + ')\n')
					all_ip.connections_established[self.host + ',' + str(self.port)] = self
					all_ip.transport.write('SERVER MESSAGE : Connection was Established by (' + self.host + ',' + str(self.port) + ')\n')
					k = 1
			if k == 0:
				self.transport.write('SERVER MESSAGE : No Connection Found\n')
					
		elif command == 'send':
			try:
				self.connections_established[ip + ',' + port].message(" ".join(line.split()[3:]),self)
			except KeyError:
				pass
		elif command == 'screen_request':
			for all_ip in self.factory.clients:
				if int(port) == all_ip.port and ip == all_ip.host and all_ip != self:
					all_ip.transport.write('SERVER MESSAGE : Remote Control Request (' + self.host + ',' + str(self.port) + ')\n')
		elif command == 'screen_grant':
			for all_ip in self.factory.clients:
				if int(port) == all_ip.port and ip == all_ip.host and all_ip != self:
					all_ip.transport.write('SERVER MESSAGE : Remote Control Grant (' + self.host + ',' + str(self.port) + ')\n')

		elif command == 'screen_not_grant':
			for all_ip in self.factory.clients:
				if int(port) == all_ip.port and ip == all_ip.host and all_ip != self:
					all_ip.transport.write('SERVER MESSAGE : Remote Control Not Grant (' + self.host + ',' + str(self.port) + ')\n')
		elif command == 'screen_server_created':
			for all_ip in self.factory.clients:
				if int(port) == all_ip.port and ip == all_ip.host and all_ip != self:
					all_ip.transport.write('SERVER MESSAGE : Server Created (' + self.host + ',' + str(self.port) + ')\n')
		elif command == 'new_live_lec':
			self.factory.live_lec_hosts.append(self)
			for all_ip in self.factory.clients:
				if all_ip != self:
					all_ip.transport.write('SERVER MESSAGE : New Live Lecture (' + self.host + ',' + str(self.port) + ')\n')
		else:
			self.transport.write('SERVER MESSAGE : Wrong Input\n')

    	def message(self, message, sender):
        	self.transport.write('(' + sender.host + ',' + str(sender.port) +') : ' + message + '\n')

class ChatFactory(protocol.ServerFactory):
	protocol = ChatProtocol
	clients = []
	live_lec_hosts = []
	
factory = ChatFactory()
reactor.listenTCP(5000, ChatFactory());
reactor.run()
