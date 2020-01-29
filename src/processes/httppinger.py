from time import sleep
import threading
import requests
from db.ping import DbPing
import json
import hashlib
import datetime
from pblib.amqp import client


class HttpPing:
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
                    print(f"Calling {check.get('name')}")
                    url = check.get("url")
                    payload = {}
                    headers = {}
                    response = requests.request("GET", url, headers=headers, data=payload)

                    if response.status_code in check.get("valid_status") if check.get("valid_status") else [200]:
                        if check.get("reply_text_contains"):
                            if check.get("reply_text_contains") in response.text:
                                probe_result = True
                            else:
                                probe_result = False
                        else:
                            probe_result = True
                    else:
                        probe_result = False
                    # print("FIRST", check.get("last_successfull"))
                    if probe_result:
                        check["last_successfull"] = str(datetime.datetime.now()).split(".", 1)[0]
                        # print("OK")
                    else:
                        check["last_failure"] = str(datetime.datetime.now()).split(".", 1)[0]
                        # print("NOK", response.status_code)

                    # test whether we have a switch from working to not working
                    if ping.data and json.loads(ping.data).get("result") is True and probe_result is False:
                        msg = {
                            "type": "http_check_failed",
                            "check_name": check["name"],
                            "check_uri": check["url"],
                            "result_code": response.status_code,
                            "result_text": response.text,
                            "valid_code": check.get("valid_status")
                        }
                        queue_connector = client()
                        queue_connector.publish(toExchange="monitoring", routingKey="http_check_failed",
                                                message=json.dumps(msg))
                    # test whether we have a switch from non-working to working
                    if ping.data and json.loads(ping.data).get("result") is False and probe_result is True:
                        msg = {
                            "type": "http_check_recovered",
                            "check_name": check["name"],
                            "check_uri": check["url"],
                            "result_code": response.status_code,
                            "result_text": response.text,
                            "valid_code": check.get("valid_status")
                        }
                        queue_connector = client()
                        queue_connector.publish(toExchange="monitoring", routingKey="http_check_recovered",
                                                message=json.dumps(msg))

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
