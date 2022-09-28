import socket
import sys
import pickle

SEND = "send"
RECV = "receive"
GCD_MSG = "JOIN"
MEMBER_MSG = "HELLO"

TIMEOUT_VAL = 1.5
BUF_SZ = 1024 # tcp receive buffer size

#TODO: INCLUDE DOCTEST

def connect(s, host, port, msg):
    socket.setdefaulttimeout(TIMEOUT_VAL)
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

def receiveData(s, msg):
    data = s.recv(BUF_SZ)
    result = pickle.loads(data)
    return result

def sendData(s, msg):
    data = pickle.dumps(msg)
    s.sendall(data)
    return True

def operateOnData(s, msg, operation):
    opDict = {"send": sendData, "receive": receiveData}
 
    s.settimeout(TIMEOUT_VAL)
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
    
def sendMessageToMembers(memberList): 
    for member in memberList:
        m = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        connected = connect(m, member['host'], member['port'], MEMBER_MSG)
        if connected and operateOnData(m, MEMBER_MSG, SEND) == True:
            receivedData = operateOnData(m, None, RECV)
            print(receivedData)

        m.close()

def connectToGCD(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = connect(s, host, port, GCD_MSG)

    if connected and operateOnData(s, GCD_MSG, SEND):
        #Otherwise, continue receiving
        receivedData = operateOnData(s, None, RECV)
        print(receivedData)
        s.close()
        return receivedData
    
    return None

def main():
    if len(sys.argv) != 3:
        print('Usage: python client.py HOST PORT')
        exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    #connect and fetch data from GCD
    memberlist = connectToGCD(host, port)

    if memberlist is None:
        print('Error occurred. Please try again.')
        exit(1)

    #now parse the response and send hello messages
    sendMessageToMembers(memberlist)

if __name__ == '__main__':
    main()