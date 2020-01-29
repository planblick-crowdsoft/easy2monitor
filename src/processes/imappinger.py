from time import sleep
import threading
import requests
from db.ping import DbPing
from db.downtime import Downtime
import json
import hashlib
import datetime
from pblib.amqp import client
import imaplib


class ImapPing:
    def __init__(self, config: dict, intervall: int):
        self.config = config
        self.intervall = intervall

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        DbPing()
        while True:
            sleep(self.intervall)
            try:
                # print(f"Sending pings every {self.intervall}s")
                for check in self.config:
                    name_hash = hashlib.sha256(check.get("name").encode()).hexdigest()
                    ping = DbPing.session.query(DbPing).filter_by(name_hash=name_hash).first()
                    if ping is None:
                        ping = DbPing()
                        ping.name_hash = name_hash

                    if ping.data:
                        check["last_successfull"] = json.loads(ping.data).get("last_successfull")
                        check["last_failure"] = json.loads(ping.data).get("last_failure")

                    # print("TARGET", ping)
                    probe_result = False
                    print(f"Checking {check.get('name')}")

                    try:
                        s = imaplib.IMAP4(check.get("host"), check.get("port"))
                        status = s.noop()[0]
                        s.logout()
                    except Exception as e:
                        status = -1

                    if status != -1:
                        probe_result = True
                    else:
                        probe_result = False

                    if probe_result:
                        check["last_successfull"] = str(datetime.datetime.now()).split(".", 1)[0]
                        # print("OK")
                    else:
                        check["last_failure"] = str(datetime.datetime.now()).split(".", 1)[0]
                        if check.get("checktime") and len(check.get("checktime")) > 0:
                            last_checktime = datetime.datetime.strptime(check["checktime"], "%Y-%m-%d %H:%M:%S")
                            now = datetime.datetime.now()
                            seconds = round((now - last_checktime).total_seconds())
                            time = Downtime()
                            time.timestamp = now
                            time.name = check["name"]
                            time.name_hash = name_hash
                            time.seconds = seconds
                            time.save()
                            check["downtime_seconds"] = int(check.get("downtime_seconds", 0)) + seconds
                        # print("NOK", response.status_code)

                    # test whether we have a switch from working to not working
                    if ping.data and json.loads(ping.data).get("result") is True and probe_result is False:
                        msg = {
                            "type": "imap_check_failed",
                            "check_name": check["name"],
                            "check_host": check["host"],
                            "check_port": check["port"]
                        }
                        queue_connector = client()
                        queue_connector.publish(toExchange="monitoring", routingKey="imap_check_failed",
                                                message=json.dumps(msg))

                    # test whether we have a switch from non-working to working
                    if ping.data and json.loads(ping.data).get("result") is False and probe_result is True:
                        msg = {
                            "type": "imap_check_recovered",
                            "check_name": check["name"],
                            "check_host": check["host"],
                            "check_port": check["port"]
                        }
                        queue_connector = client()
                        queue_connector.publish(toExchange="monitoring", routingKey="imap_check_recovered",
                                                message=json.dumps(msg))

                    whole = 365 * 24 * 60 * 60

                    downtime_seconds = check.get("downtime_seconds", 0)
                    check["downtime_seconds"] = downtime_seconds
                    check["downtime_percentage"] = 100 * float(downtime_seconds / float(whole))
                    check["uptime_percentage"] = 100 - check["downtime_percentage"]

                    time = datetime.datetime.now()
                    check["result"] = probe_result
                    check["checktime"] = str(time).split(".", 1)[0]
                    ping.data = json.dumps(check)
                    ping.name = check["name"]
                    ping.timestamp = time
                    # print("BEFORE SAVE", ping)
                    ping.save()

            except Exception as e:
                raise
