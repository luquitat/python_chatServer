import socket, select, string, sys
##
#Le damos formato a la respuesta del servidor cuando se envia un mensaje
def display() :
	you="\33[33m\33[1m"+" Tu: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def main():

    if len(sys.argv)<2:
        host = raw_input("Ingrese ip del servidor: ")
    else:
        host = sys.argv[1]

    port = 5001
    
    #Preguntamos por el usuario
    name=raw_input("\33[34m\33[1m CREANDO NUEVO ID:\n Ingrese nombre de usuario: \33[0m")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
    # Se conecta con el servidor
    try :
        s.connect((host, port))
    except :
        print "\33[31m\33[1m No se pudo cconectar al servidor \33[0m"
        sys.exit()

    # si se pudo conectar, sigue por aca
    s.send(name)
    display()
    while 1:
        socket_list = [sys.stdin, s]
        
        # Obtenemos la lista de socket disponibles
        rList, wList, error_list = select.select(socket_list , [], [])
        
        for sock in rList:
            # Mensaje entrante del servidor
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\33[31m\33[1m \rDESCONECTADO!!\n \33[0m'
                    sys.exit()
                else :
                    sys.stdout.write(data)
                    display()
        
            # El usuario ingresa un mensaje
            else :
                msg=sys.stdin.readline()
                s.send(msg)
                display()

if __name__ == "__main__":
    main()
