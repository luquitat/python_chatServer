import socket, select, string, sys

#Helper function (formatting)
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
    
    #asks for user name
    name=raw_input("\33[34m\33[1m CREANDO NUEVO ID:\n Ingrese nombre de usuario: \33[0m")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
    # connecting host
    try :
        s.connect((host, port))
    except :
        print "\33[31m\33[1m No se pudo cconectar al servidor \33[0m"
        sys.exit()

    #if connected
    s.send(name)
    display()
    while 1:
        socket_list = [sys.stdin, s]
        
        # Get the list of sockets which are readable
        rList, wList, error_list = select.select(socket_list , [], [])
        
        for sock in rList:
            #incoming message from server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\33[31m\33[1m \rDESCONECTADO!!\n \33[0m'
                    sys.exit()
                else :
                    sys.stdout.write(data)
                    display()
        
            #user entered a message
            else :
                msg=sys.stdin.readline()
                s.send(msg)
                display()

if __name__ == "__main__":
    main()
