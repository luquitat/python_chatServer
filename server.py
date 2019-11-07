import socket, select
from threading import Timer

connected_list = []

#Funcion principal para encontrar funciones
def atender(sock, msg, data):
	lista = []
	lista = data.split(" ")
	print lista
	if data.startswith("/"):
		opcion = lista[0][1:]
		if opcion not in opciones:
			sockfd.send("\n El comando no existe o es incorrecto. Use /help para ver los comandos disponibles")
		else:
			if opcion == opciones[1]: ###### LOGOUT ######
				logout(sock)
			elif opcion == opciones[2]: ###### MSG ######
				if(len(lista) > 2):
					user = lista [1]
					param_dos = ' '.join(lista[2:])
					privado(sock,param_dos,user)
				else:
					todos(sock, msg)
			elif opcion == opciones[3]: ###### HELP ######
				helps(sock)
			elif opcion == opciones[4]: ###### NICK ######
				if(len(lista) > 1):
					newNick = lista [1]
					nick(sock,newNick)

			elif opcion == opciones[5]: ###### USUARIOS ######
				usuarios(sock)

			elif opcion == opciones[6]: ###### KICK ######
				if(len(lista) > 1):
					user = lista [1]
					param_dos = ' '.join(lista[2:])
					kick(sock,param_dos,user)
				else:
					todos(sock, msg)
			else:
				print "probando error"
	else:
		todos(sock, msg)


def logout (sock):
	for socket in connected_list:
		if socket != server_socket:
			try :
				socket.send("\r\33[1m"+"\33[31m\t\tSERAN DESCONECTADOS EN 10 SEGUNDOS \33[0m\n")
			except :
				# Si la conexion no esta disponible
				socket.close()
				connected_list.remove(socket)

	t = Timer(10.0, timerLogout)
	t.start()
	

def timerLogout():
	global flag
	flag = 0


#Funcion para enviar mensajes a todos
def todos (sock, message):
	#El mensaje no se envia al servidor ni al 
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				# Si la conexion no esta disponible
				socket.close()
				connected_list.remove(socket)

def privado(sock,message,user):
	llave = [key for key, nombre in record.items() if nombre == user]
	#print llave
	lla = llave[0]
	for socket in connected_list:
		if socket != server_socket:
			#print "esto es socket de lista ", socket.getpeername()
			#print "esta es la llave de ram ", lla
			#print "la llave es igual alsocket? ", lla == socket.getpeername()
			if socket.getpeername() == lla:
				try :
					if (sock.getpeername() == lla):
						socket.send("\n\33[0m\33[44m\33[33m"+ message+"\33[0m\n")
					else:	
						socket.send("\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m\33[44m\33[33m"+ message+"\33[0m\n")
				except :
					# Si la conexion no esta disponible
					socket.close()
					connected_list.remove(socket)

def kick(sock,message,user):
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
					msg="\r\33[1m"+"\33[31m "+record[lla]+" ha sido eliminado por "+record[sock.getpeername()]+" \33[0m\n"
					del record[lla]
					todos(sock,msg)
					connected_list.remove(socket)
					socket.close()
					continue

				except :
					# Si la conexion no esta disponible
					socket.close()
					connected_list.remove(socket)

def usuarios(sock):
	try :
		lista_usuarios = ""
		i = 0;
		for ip_port, nombre in record.items():
			if ip_port != sock.getpeername():
				i += 1
				lista_usuarios += nombre
				if i < len(record.items()):
					lista_usuarios += ", "
		if(lista_usuarios == ""):
			msg = "Estas solito ;)"
		else:
			msg = " Usuarios: " + lista_usuarios
		privado(sock, msg, record[sock.getpeername()])
	except :
		# Si la conexion no esta disponible
		socket.close()
		connected_list.remove(socket)

def nick(sock, newNick):
	try :
		oldNick = ""
		for ip_port, nombre in record.items():
			if(newNick != nombre):
				oldNick = nombre
				record[sock.getpeername()] = newNick
		if(oldNick != ""):
			msg = "\n El usuario: " + oldNick + " cambio su nick a " + newNick + "\n"
			todos(sock, msg)
		
	except :
		# Si la conexion no esta disponible
		socket.close()
		connected_list.remove(socket)

def helps(sock):
	try :
		sock.send(ayuda)
		
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

	flag = 1

	opciones = ["login","logout","msg","help","nick","usuarios","kick"]

	ayuda = "\33[32m\t\t **************** AYUDA **************** \n"
	ayuda += "\t/msg 'usuario' 'mensaje': Mensaje privado a usuario\n"
	ayuda += "\t/nick 'nuevo nick': Cambiar nick\n"
	ayuda += "\t/usuarios : Lista de usuarios conectados\n"
	ayuda += "\t/kick 'usuario' : Elimina un usuario\n"
	ayuda += "\t/help : Ayuda\33[0m\n"
	ayuda += "\33[32m\t\t *************************************** \n"

	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	server_socket.bind(("", port))
	server_socket.listen(10) #listen como maximo 10 conexiones a la vez

	# Agregar socket del servidor a la lista de conexiones legibles 
	connected_list.append(server_socket)

	print "\33[32m\t\t\t\tSERVER ACTIVO\33[0m" 

	while flag > 0:
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
                
                #si el nombre esta repetido
				if name in record.values():
					sockfd.send("\r\33[31m\33[1m El nombre de usuario ya existe!\n\33[0m")
					del record[addr]
					connected_list.remove(sockfd)
					sockfd.close()
					continue
				else:
                    # a la ip y port del cliente le asignamos el nombre de usuario
					record[addr]=name
					print "Cliente (%s, %s) conectado" % addr," [",record[addr],"]"
					
					sockfd.send("\33[32m\r\33[1m Bienvenido al Chat. Ingrese 'tata' en cualquier momento para salir \n\33[0m")
					todos(sockfd, "\33[32m\33[1m\r "+name+" se unio a la conversacion \n\33[0m")
					#send_to_user(sockfd, "esto es una prueba si sos ram")

			#Mensajes entrantes de algun cliente
			else:
				# Datos del cliente
				try:
					data1 = sock.recv(buffer)

					data=data1[:data1.index("\n")]
                    
                    #obtener addr del cliente que envia el mensaje
					i,p=sock.getpeername()
					if data == "tata":
						msg="\r\33[1m"+"\33[31m "+record[(i,p)]+" ha dejado la conversacion \33[0m\n"
						todos(sock,msg)
						print "Cliente (%s, %s) esta offline" % (i,p)," [",record[(i,p)],"]"
						del record[(i,p)]
						connected_list.remove(sock)
						sock.close()
						continue

					else:
						msg="\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+data+"\n"
						atender(sock,msg,data)
            
                #Si hay algun problema se deconecta el usuario
				except:
					(i,p)=sock.getpeername()
					todos(sock, "\r\33[31m \33[1m"+record[(i,p)]+" ha dejado la conversacion inesperadamente\33[0m\n")
					print "Cliente (%s, %s) esta offline (error)" % (i,p)," [",record[(i,p)],"]\n"
					del record[(i,p)]
					connected_list.remove(sock)
					sock.close()
					continue

	server_socket.close()

