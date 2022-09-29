"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Avery Dinh
:Version: f22
"""

import socket
import sys
import pickle

"""
A simple client application that sends a message to a test Group Coordinator Daemon to obtain a list of other members,
and consequently attempt to send hello messages to each of the member.
"""
class SimpleClient(object):

    SEND = "send"
    RECV = "receive"
    GCD_MSG = "JOIN"
    MEMBER_MSG = "HELLO"
    TIMEOUT_VAL = 1.5
    BUF_SZ = 1024 # tcp receive buffer size

    """
    Constructor parameters: 
    h : str - the name of the host server
    p : int - the port number to use
    """
    def __init__(self, h, p) -> None:
        self.host = h
        self.port = p

    """
    Helper function to receive data from the server
    Parameters: 
    s : socket - the socket connection 
    msg: str - a msg that might be sent over
    """
    def receiveData(self, s, msg = ''):
        data = s.recv(SimpleClient.BUF_SZ)
        result = pickle.loads(data)
        return result

    """
    Helper function to receive data from the server
    Parameters: 
    s : socket - the socket connection 
    msg: str - a msg that might be sent over
    """
    def sendData(self, s, msg):
        data = pickle.dumps(msg)
        s.sendall(data)
        return True

    """
    Function to do some specified operation (send or receive) on data
    Parameters: 
    s : socket - the socket connection 
    msg: str - a msg that might be sent over
    operation : str - the operation to get done ['send' or 'receive']
    return result as a string Literal
    """
    def operateOnData(self, s, msg, operation):
        opDict = {"send": self.sendData, "receive": self.receiveData}
    
        s.settimeout(SimpleClient.TIMEOUT_VAL)
        try:
            result = opDict[operation](s, msg) #pickle.dumps(msg)
            return result
        except socket.timeout as e:
            s.close()
            print('Timeout error, connection took to long', e)
            return False
        except OSError as e:
            s.close()
            print('Error connecting: ', e)
            return False
    
    """
    Function to start a connection to the server

    Parameters: 
    s : socket - the socket connection 
    host : str - name of the server
    port : int - port number to use
    msg: str - a msg that might be sent over
    return True if connection is established without any error, False otherwise
    """    
    def connect(self, s, host, port, msg):
        socket.setdefaulttimeout(SimpleClient.TIMEOUT_VAL)
        try:
            print('\n%s to (%s, %i)' % (msg, host, port))
            s.connect((host, port))
            return True
        except socket.timeout as e:
            s.close()
            print('Timeout error, connection took to long', e)
            return False
        except OSError as e:
            s.close()
            print('Error connecting: ', e)
            return False
    
    """
    Function to communicate to the member servers
    Parameters: 
    memberList : list - a list of dictionaries containing the memebers
    """
    def talkToMembers(self, memberList): 
        for member in memberList:
            m = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
            connected = self.connect(m, member['host'], member['port'], SimpleClient.MEMBER_MSG)
            if connected and self.operateOnData(m, SimpleClient.MEMBER_MSG, SimpleClient.SEND) == True:
                receivedData = self.operateOnData(m, None, SimpleClient.RECV)
                if receivedData:
                    print(receivedData)

            m.close()

    """
    Function to start a connection to the test Daemon

    Parameters: 
    s : socket - the socket connection 
    host : str - name of the server
    port : int - port number to use
    return member list if connection is established without any error, None otherwise
    """   
    def connectToGCD(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = self.connect(s, host, port, SimpleClient.GCD_MSG)

        if connected and self.operateOnData(s, SimpleClient.GCD_MSG, SimpleClient.SEND):
            #Otherwise, continue receiving
            receivedData = self.operateOnData(s, None, SimpleClient.RECV)
            print(receivedData)
            s.close()
            return receivedData
        
        return None

    """
    Main function to execute the sequence: talk to the test GCD, then to the members
    """
    def execute(self):
        
        #connect and fetch data from GCD
        memberlist = self.connectToGCD(host, port)

        if memberlist is None:
            print('Error occurred. Please try again.')
            exit(1)

        #now parse the response and send hello messages
        self.talkToMembers(memberlist)

"""
Application entry point, create an instance of the Simple Client, then execute.
"""
if __name__ == '__main__':
    if len(sys.argv) != 3:
            print('Usage: python client.py HOST PORT')
            exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = SimpleClient(host, port)
    client.execute()