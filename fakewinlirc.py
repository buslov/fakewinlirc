import os.path
import socket
import threading
import bottle


class FakeWinLirc:
    def __init__(self):
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socket.bind(("127.0.0.1", 8765))
        self.socket.listen(5)

    @staticmethod
    def mkcmd(cmd, repeatcount=0):
        s = "{c} {n:02x} {s} python\n".format(c="0" * 16, n=repeatcount, s=cmd)
        return bytes(s, "ascii")

    def serve_forever(self):
        while True:
            conn, addr = self.socket.accept()
            print("accepted", addr)
            self.clients.append(conn)

    def run(self):
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def sendtoall(self, *args, **kargs):
        data = self.mkcmd(*args, **kargs)
        closed = []
        for c in self.clients:
            try:
                c.sendall(data)
            except socket.error as e:
                print("exception:", e.errno, e)
                closed.append(c)
        for c in closed:
            self.clients.remove(c)
            print("removed client", c.getpeername())


class WebUI:
    def __init__(self):
        self.fakewinlirc = FakeWinLirc()
        self.fakewinlirc.run()
        self.bottleapp = bottle.Bottle()
        for kw in dir(self):
            attr = getattr(self, kw)
            if hasattr(attr, 'bottleroute'):
                self.bottleapp.route(attr.bottleroute[0], attr.bottleroute[1], attr)

    def _route(route, method="GET"):
        def decorator(f):
            f.bottleroute = (route, method)
            return f
        return decorator

    @_route("/")
    def index(self):
        return bottle.static_file("index.htm", root='')

    @_route("/static/<path>")
    def staticfiles(self, path):
        return bottle.static_file(path, root='static')

    @_route("/ajax", method="POST")
    def ajax(self):
        cmd = bottle.request.forms.get('cmd')
        self.fakewinlirc.sendtoall(cmd)


def run():
    WebUI().bottleapp.run(host='0.0.0.0', port='8080')


if __name__ == "__main__":
    print("os.getcwd():", os.getcwd())
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    print("scriptdir:", scriptdir)
    os.chdir(scriptdir)
    print("os.getcwd():", os.getcwd())
    run()
