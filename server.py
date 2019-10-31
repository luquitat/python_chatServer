import socket, select

connected_list = []

#Funcion principal para encontrar funciones
def atender(sock, msg, data):
	lista = []
	opciones = ["login","logout","msg","help","nick","usuarios","kick","prueba","killbill"]
	lista = data.split(" ")
	print lista
	if len(lista) > 2:
		opcion = lista[0][1:]
		user = lista [1]
		param_dos = ' '.join(lista[2:])
		if lista[0][0] == "/":
			if opcion not in opciones:
				print "El comando no existe o es incorrecto. Use /help para ver los comandos disponibles"
			else:
				send_to_user(sock,param_dos,user)
	else:
		send_to_all(sock, msg)

#Funcion para enviar mensajes a todos
def send_to_all (sock, message):
	#El mensaje no se envia al servidor ni al 
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				# Si la conexion no esta disponible
				socket.close()
				connected_list.remove(socket)

def send_to_user(sock,message,user):
	llave = [key for key, nombre in record.items() if nombre == user]
	#print llave
	lla = llave[0]
	for socket in connected_list:
		if socket != server_socket and socket != sock:
			#print "esto es socket de lista ", socket.getpeername()
			#print "esta es la llave de ram ", lla
			#print "la llave es igual alsocket? ", lla == socket.getpeername()
			if socket.getpeername() == lla:
				try :
					socket.send("\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+message+"\n")
				except :
					# Si la conexion no esta disponible
					socket.close()
					connected_list.remove(socket)

if __name__ == "__main__":
	name=""
	#diccionario para almacenar direcciones correspondientes a usuarios
	record={}
	# lista para mantener descriptores de sockets
	connected_user = []
	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.bind(("", port))
	server_socket.listen(10) #listen como maximo 10 conexiones a la vez

	# Agregar socket del servidor a la lista de conexiones legibles 
	connected_list.append(server_socket)

	print "\33[32m \t\t\t\tSERVER ACTIVO \33[0m" 

	while 1:
        # Obtener la lista de sockets que estan listos para ser leidos por select 
		rList,wList,error_sockets = select.select(connected_list,[],[])

		for sock in rList:
			#Nueva conexion
			if sock == server_socket:
				# administrar el caso en que haya una nueva conexion recibida a traves del socket server
				sockfd, addr = server_socket.accept()
				name=sockfd.recv(buffer)
				connected_list.append(sockfd)
				record[addr]=""
				#print "record and conn list ",record,connected_list
                
                #si el nombre esta repetido
				if name in record.values():
					sockfd.send("\r\33[31m\33[1m El nombre de usuario ya existe!\n\33[0m")
					del record[addr]
					connected_list.remove(sockfd)
					sockfd.close()
					continue
				else:
                    #add name and address
					record[addr]=name
					print "Cliente (%s, %s) conectado" % addr," [",record[addr],"]"
					##print record
					##print sockfd.getpeername()
					##print str(connected_list)[1:-1]
					## Prueba de send privado
					
					#llave = [key for key, nombre in record.items() if nombre == "ram"]
					##print llave
					#lla = llave[0]
					
					sockfd.send("\33[32m\r\33[1m Bienvenido al Chat. Ingrese 'tata' en cualquier moento para salir \n\33[0m")
					send_to_all(sockfd, "\33[32m\33[1m\r "+name+" se unio a la conversacion \n\33[0m")
					#send_to_user(sockfd, "esto es una prueba si sos ram")

			#Mensajes entrantes de algun cliente
			else:
				# Datos del cliente
				try:
					data1 = sock.recv(buffer)
					#print "sock es: ",sock
					data=data1[:data1.index("\n")]
					#print "\ndata recibida: ",data
                    
                    #obtener addr del cliente que envia el mensaje
					i,p=sock.getpeername()
					if data == "tata":
						msg="\r\33[1m"+"\33[31m "+record[(i,p)]+" ha dejado la conversacion \33[0m\n"
						send_to_all(sock,msg)
						print "Cliente (%s, %s) esta offline" % (i,p)," [",record[(i,p)],"]"
						del record[(i,p)]
						connected_list.remove(sock)
						sock.close()
						##TEMPORALMENTE CIERRA EL SERVIDOR
						server_socket.close()
						continue

					else:
						msg="\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+data+"\n"
						atender(sock,msg,data)
						
						#send_to_all(sock,msg)
            
                #abrupt user exit
				except:
					(i,p)=sock.getpeername()
					send_to_all(sock, "\r\33[31m \33[1m"+record[(i,p)]+" ha dejado la conversacion inesperadamente\33[0m\n")
					print "Cliente (%s, %s) esta offline (error)" % (i,p)," [",record[(i,p)],"]\n"
					del record[(i,p)]
					connected_list.remove(sock)
					sock.close()
					continue

	server_socket.close()

