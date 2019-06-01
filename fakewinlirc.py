import os.path
import socket
import sys
import threading
import bottle

clients = []


def sendtoall(cmd):
    s = "{c} {n:02x} {s} python\n".format(c="0" * 16, n=0, s=cmd)
    d = bytes(s, encoding='ascii')
    closed = []
    for c in clients:
        try:
            c.sendall(d)
        except socket.error as e:
            print("exception:", e.errno, e, file=sys.stderr)
            closed.append(c)
    for c in closed:
        c.close()
        clients.remove(c)


@bottle.route("/")
def index():
    return bottle.static_file("index.htm", root='')


@bottle.route("/static/<path>")
def staticfiles(path):
    return bottle.static_file(path, root='static')


@bottle.post("/ajax")
def ajax():
    cmd = bottle.request.forms.get('cmd')
    sendtoall(cmd)


def tcpserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 8765))
    s.listen(5)
    while True:
        c, a = s.accept()
        print("accepted", a, file=sys.stderr)
        clients.append(c)


if __name__ == "__main__":
    print("os.getcwd():", os.getcwd(), file=sys.stderr)
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    print("scriptdir:", scriptdir, file=sys.stderr)
    os.chdir(scriptdir)
    print("os.getcwd():", os.getcwd(), file=sys.stderr)
    t = threading.Thread(target=tcpserver)
    t.daemon = True
    t.start()
    bottle.debug(True)
    bottle.run(host="0.0.0.0", port=8080)
