
import socket
from threading import Thread
class Client:
    def __init__(self, host, port, serverhost, serverport):
        self.host = host
        self.port = port
        self.serverhost = serverhost
        self.serverport = serverport
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.choicelist={}
        self.currentRequest=""
        self.filerepo = {}
        #bind on new thread
        thread= Thread(target=self.bind)
        thread.start()
        #connect to server
        self.connectserver()
        #register to server
        self.reg()
        #start loop
        self.loop()
        thread.join()

    def loop(self):
        ####################################################################
        ##################  MAIN LOOP OF THE PROGRAM #######################
        ####################################################################
        while True:
            cmd=input("input command: ")
            cmd= cmd.lower()
            cmd= cmd.split(" ")
            if cmd[0]=="publish" and len(cmd)==3:
                print("Pushing...")
                self.filerepo[cmd[2]]=cmd[1]
                self.push(cmd[2])
                print("pushed")
                continue

            elif cmd[0]=="140203_REGTEST_140203_AAA": #DO NOT USE, ALREADY REGISTERED WHEN CREATED, TAKE NO EFFECT
                print("Registering...")
                self.reg()
                continue

            elif cmd[0]=="get" and len(cmd) == 2:
                self.get(cmd[1])
                
 
            elif cmd[0]=="fetch" and len(cmd) == 2:
                self.fetch(self.choicelist[int(cmd[1])])
                continue

            elif cmd=="exit":
                break
            else:
                print("Invalid command")
                continue

        


    ####################################################################
    ################   CONNECT TO SERVER AND BIND    ###################
    ####################################################################
    def connectserver(self):
        self.connectsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connectsocket.connect((self.serverhost, self.serverport))

    def bind(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Listening on port %s" % self.port)
        while True:
            c, addr = self.socket.accept()
            thread2 = Thread(target=self.on_new_client, args=(c, addr))
            thread2.start()
        c.close()




    ####################################################################
    ##########   HANDLE FILE REQUEST FROM ANOTHER PEER      ############
    ####################################################################
    def on_new_client(self, client_socket, addr):
        print(f"New connection from: {addr}")
        print("Waiting for file name")
        data=client_socket.recv(2048).decode()
        if data:
            header, data=self.decodemsg(data)
            if header=="FETCH_REQ":
                print("Sending file" + data)
                #send response
                client_socket.send("<FETCH_REQ_ACK/>".encode())
                self.sendfile(client_socket, data)
            
            if header=="PING":
                print("Ping request from server")
                msg = "<PING_ACK> " + data + " </PING_ACK>"
                self.connectsocket.send(msg.encode())
               


    def sendfile(self, client_socket, filename):
        filename=self.filerepo[filename]
        file = open(filename, 'rb')
        dat = file.read(2048)
        while (dat):
            client_socket.send(dat)
            dat = file.read(2048)
        file.close()
        client_socket.close()
        print('Done sending')




    ####################################################################
    ##################   HANDLE CLI FROM USER ##########################
    ####################################################################

    def push(self, filename):
        #get list of peer from server
        msg="<PUSH> " + filename + " </PUSH>"
        self.connectsocket.send(msg.encode())
        #get response from server
        data=self.connectsocket.recv(2048).decode()
        if(data=="<PUSH_ACK/>"):
            print("Pushed successfully")
            return 1
        else:
            return 0

    def reg(self):
        #register to server
        msg="<REG> "
        msg+= self.host+":"+str(self.port)
        msg+=" </REG>"
        self.connectsocket.send(msg.encode())
        print("Register with address: "+msg)
        #TODO: get respone from server
        data=self.connectsocket.recv(2048).decode()
        if(data=="<REG_ACK/>"):
            print("Registered successfully")
            return 1
        else:
            return 0



    def get(self, filename):
        #send request to server
        msg="<GET_F> " + filename + " </GET_F>"
        self.connectsocket.send(msg.encode())
        #TODO: get respone from server

        #get list from server
        list=self.connectsocket.recv(4096).decode()
        self.choicelist=list.split(";")


        #TODO: get response from server
        data=self.connectsocket.recv(2048).decode()
        if(data=="<GET_F_ACK/>"):
            print("List of user that have the file:")
            print(self.choicelist)
            self.currentRequest=filename
            return 1
        else:
            print("Failed to get list of user" )
            return 0
    
    def fetch(self, peer):
        peerHOST=peer.split(":")[0]
        peerPORT=int(peer.split(":")[1])
        print(peer)
        #new connect to peer
        newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newsocket.connect((peerHOST, peerPORT))
        #send file name to peer
        msg="<FETCH_REQ> " + self.currentRequest + " </FETCH_REQ>"
        newsocket.send(msg.encode())

        #TODO: get respone from peer
        data=newsocket.recv(2048).decode()
        if(data=="<FETCH_REQ_ACK/>"):
            print("Fetching file...")
        else:
            print("Failed to fetch file" )
            return 0

        #get file from peer
        FILENAME=self.currentRequest.split(".")[0]+"_copy."+self.currentRequest.split(".")[1]
        file=open(FILENAME,"wb")
        data=newsocket.recv(2048)
        while data:
            file.write(data)
            data=newsocket.recv(2048)

        newsocket.close()
        file.close()
        print("File fetched successfully")
        return 0


    ####################################################################
    ##################     ULTILITY FUNCTION ()       ##################
    ####################################################################
    def decodemsg(self, data):
        data= data.split("> ",1)
        header=data[0].split("<",1)[1]
        print(header)
        msg=data[1].split(" <",1)[0]
        return header, msg

        
        
        
    ####################################################################
    ##################     MAIN FUNCTION ()       ######################
    ####################################################################

PORT = int(input("PORT to start: "))
#set localhost
host = socket.gethostbyname(socket.gethostname())
serverhost = "192.168.102.1"

serverport = 8080
#print client
print("Client IP address is: " + host)

client = Client(host, PORT, serverhost, serverport)


 

    



