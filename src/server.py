import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))
from api.main import app
from pblib.server import Server
from pblib.amqp import client
from processes.httppinger import HttpPing
from processes.smtppinger import SmtpPing
from processes.imappinger import ImapPing
import json
from models.mq_handler import msg_handler

if __name__ == '__main__':
    with open("./check_definitions/http_check_definitions.json", "r") as configfile:
        config = json.loads(configfile.read())
    HttpPing(config=config, intervall=10)

    with open("./check_definitions/smtp_check_definitions.json", "r") as configfile:
        config = json.loads(configfile.read())
    SmtpPing(config=config, intervall=10)

    with open("./check_definitions/imap_check_definitions.json", "r") as configfile:
        config = json.loads(configfile.read())
    ImapPing(config=config, intervall=10)

    name = "monitoring"
    queue = "monitoring"
    bindings = {}
    bindings['monitoring'] = ['*']
    callback = msg_handler

    client.addConsumer(name, queue, bindings, callback)

    server = Server()
    server.start(flask_app=app, app_path="/api", static_dir="/html", static_path="/", port=int(os.getenv("FRONTEND_PORT")))
