"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Kevin Lundeen
:Version: f20
"""
import pickle
import socketserver
import sys
import time

BUF_SZ = 1024 # tcp receive buffer size


class GroupCoordinatorDaemon(socketserver.BaseRequestHandler):
  """
  A Group Coordinator Daemon (GCD) which will respond with a list of potential group members to a text message JOIN
  with list of group members to contact.

  For Lab1, we just respond with a fixed list of two servers.
  """
  HELLO_RESPONSE = ['Hi there']

  def handle(self):
    """
    Handles the incoming messages - expects only 'JOIN' messages
    """
    raw = self.request.recv(BUF_SZ) # self.request is the TCP socket connected to the client
    print(self.client_address)
    try:
      message = pickle.loads(raw)
    except (pickle.PickleError, KeyError, EOFError):
      response = bytes('Expected a pickled message, got ' + str(raw)[:100] + '\n', 'utf-8')
    else:
      if message != 'HELLO':
        response = pickle.dumps('Unexpected message: ' + str(message))
      else:
        response = pickle.dumps(self.HELLO_RESPONSE)


    print('start sleep')
    time.sleep(1.6)
    print('end')

    self.request.sendall(response)


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print("Usage: python gcd.py GCDPORT")
    exit(1)
  port = int(sys.argv[1])
  with socketserver.TCPServer(('', port), GroupCoordinatorDaemon) as server:
    try:
      server.serve_forever()
    except KeyboardInterrupt as e:
      print('Shutting down...')