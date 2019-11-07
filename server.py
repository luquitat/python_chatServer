import socket, select
from threading import Timer

connected_list = []

#Funcion principal para encontrar funciones. Nuestro controlador
def atender(sock, msg, data):
	lista = []
	lista = data.split(" ")
	print lista
	if data.startswith("/"):
		opcion = lista[0][1:]
		if opcion not in opciones:
			sock.send("\r El comando no existe o es incorrecto. Use /help para ver los comandos disponibles\n")
		else:
			if opcion == opciones[0]: ###### LOGOUT ######
				logout(sock)
			elif opcion == opciones[1]: ###### MSG ######
				if(len(lista) > 2):
					user = lista [1]
					param_dos = ' '.join(lista[2:])
					privado(sock,param_dos,user)
				else:
					todos(sock, msg)
			elif opcion == opciones[2]: ###### HELP ######
				helps(sock)
			elif opcion == opciones[3]: ###### NICK ######
				if(len(lista) > 1):
					newNick = lista [1]
					nick(sock,newNick)

			elif opcion == opciones[4]: ###### USUARIOS ######
				usuarios(sock)

			elif opcion == opciones[5]: ###### KICK ######
				if(len(lista) > 1):
					user = lista [1]
					param_dos = ' '.join(lista[2:])
					kick(sock,param_dos,user)
				else:
					todos(sock, msg)
			else:
				todos(sock, msg)
	else:
		todos(sock, msg)

# Funcion para el logout recorrmos todos los usuarios y mandamos un mensaje a ellos
# y luego ejecutamos una funcion para que se ejecute dentro de 10 seg
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
	
# Funcion para el timeout del logout del servidor
def timerLogout():
	global flag
	flag = 0


#Funcion para enviar mensajes a todos. Recorremos la lista de conectados
# y le enviamos un mensaje a todos los usuarios
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

# se envia un mensaje privado a un usuario seleccionado. Recorremos la lista de conectados
# y buscamos el usuario y le mandamos el mensaje solo a el
def privado(sock,message,user):
	flag = -1
	for socket in connected_list:
		if socket != server_socket:
			if record[socket.getpeername()] == user:
				try :
					flag = 1
					socket.send("\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m\33[44m\33[33m"+ message+"\33[0m\n")
				except :
					# Si la conexion no esta disponible
					socket.close()
					connected_list.remove(socket)
	if( flag == -1):
		sock.send("\r\33[1m"+"\33[31m El usuario "+user+" no existe \33[0m\n")
	
# se elimina un usuario seleccionado. Recorremos la lista de conectados
# y buscamos el que se quiere eliminar
def kick(sock,message,user):
	for socket in connected_list:
		if socket != server_socket and socket != sock:
			if record[socket.getpeername()]  == user:
				try :
					msg="\r\33[1m"+"\33[31m "+user+" ha sido eliminado por "+record[sock.getpeername()]+" \33[0m\n"
					del record[socket.getpeername()]
					connected_list.remove(socket)
					socket.close()
					continue

				except :
					# Si la conexion no esta disponible
					socket.close()
					connected_list.remove(socket)
	todos(sock,msg)
# el usuario obtiene una lista de todos los usuarios conectados
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
			msg = "\r Estas solito ;)"
		else:
			msg = "\r Usuarios: " + lista_usuarios
		privado(sock, msg, record[sock.getpeername()])
	except :
		# Si la conexion no esta disponible
		socket.close()
		connected_list.remove(socket)

# function: le pasamos el socket y el nuevo nick y recorremos el array de usuarios
# preguntando si el nuevo nick es diferente a cualquier otro usuario
# enviamos el mensaje a todos y al mismo usuario
def nick(sock, newNick):
	try :
		oldNick = ""
		for ip_port, nombre in record.items():
			if(newNick != nombre):
				oldNick = nombre
				record[sock.getpeername()] = newNick
		if(oldNick != ""):
			msg = "\r El usuario " + oldNick + " cambio su nick a " + newNick + "\n"
			todos(sock, msg)
			privado(sock, "\r Cambiaste tu nick a " + newNick, newNick)
		else :
			privado(sock, "\r El nick ya existe", record[sock.getpeername()])
	except :
		# Si la conexion no esta disponible
		socket.close()
		connected_list.remove(socket)
		
# Funcion de help: se le envia la ayuda al usuario seleccionado
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
	#Se usa para el logout, si es 0 apagamos el servidor 
	flag = 1
	#lista de opciones para los codigos
	opciones = ["logout","msg","help","nick","usuarios","kick"]

	ayuda = "\33[32m\t\t **************** AYUDA **************** \n"
	ayuda += "\t/msg 'usuario' 'mensaje': Mensaje privado a usuario\n"
	ayuda += "\t/nick 'nuevo nick': Cambiar nick\n"
	ayuda += "\t/usuarios : Lista de usuarios conectados\n"
	ayuda += "\t/kick 'usuario' : Elimina un usuario\n"
	ayuda += "\t/help : Ayuda\n"
	ayuda += "\texit : Salir\n"
	ayuda += "\t/logout : Apagar servidor\n"
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
					
					sockfd.send("\33[32m\r\33[1m Bienvenido al Chat. Ingrese 'exit' en cualquier momento para salir \n\33[0m")
					todos(sockfd, "\33[32m\33[1m\r "+name+" se unio a la conversacion \n\33[0m")
			#Mensajes entrantes de cualquier usuario que no sea la primera conexion
			else:
				# Datos del cliente
				try:
					data1 = sock.recv(buffer)

					data=data1[:data1.index("\n")]
                    
                    #obtener addr del cliente que envia el mensaje
					i,p=sock.getpeername()
					if data == "exit":
						msg="\r\33[1m"+"\33[31m "+record[(i,p)]+" ha dejado la conversacion \33[0m\n"
						#enviamos la desconexion del usuario a los demas usuarios
						todos(sock,msg)
						#logueamos la desconexion del usuario en el servidor
						print "Cliente (%s, %s) esta offline" % (i,p)," [",record[(i,p)],"]"
						#eliminamos el usuario de la lista y eliminamos el socket de la lista de socket
						del record[(i,p)]
						connected_list.remove(sock)
						sock.close()
						continue

					else:
						msg="\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+data+"\n"
						#es nuestro controlador, donde manejamos los codigos
						#sock: es el socket abierto entre el servidor y el usuario
						#msg: es el mensaje armado para que salga lindo en la pantalla
						#data: es el mensaje crudo que envio el cliente
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

