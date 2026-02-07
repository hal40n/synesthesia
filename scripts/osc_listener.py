# scripts/osc_listener.py
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def handle(address, *args):
    print(f"[osc] {address} {args}")

dispatcher = Dispatcher()
dispatcher.map("/syn", handle)

server = BlockingOSCUDPServer(("0.0.0.0", 57121), dispatcher)
print("Listening on 57121...")
server.serve_forever()
