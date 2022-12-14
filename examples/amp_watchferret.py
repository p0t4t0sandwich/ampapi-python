from datetime import datetime
from time import sleep
from dotenv import load_dotenv
import os

from ampapi_handler import AMPAPIHandler



def watchdog(instance_name):
    load_dotenv()
    username = os.getenv("AMP_API_USER")
    password = os.getenv("AMP_API_PASSWORD")

    ADS = AMPAPIHandler(
        baseUri="http://localhost:8108/",
        username=username,
        password=password
    )
    ADS.initHandler()

    for target in (ADS.ADSModule.GetInstances())["result"]:
        for instance in target["AvailableInstances"]:
            if instance["InstanceName"] == instance_name:
                instance_id = instance["InstanceID"]

                InstanceAPI = ADS.InstanceLogin(instance_id=instance_id)

                if InstanceAPI != None:
                    InstanceAPI.init()

                    state_tracker = 0
                    while True:
                        try:
                            status = InstanceAPI.Core.GetStatus()["State"]

                            if status == 30: state_tracker += 1
                            else: state_tracker = 0

                            if state_tracker >= 2:
                                now = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                print(f"Watchdog Event Detected: {now}")
                                InstanceAPI.Core.Kill()
                                sleep(10)
                                InstanceAPI.Core.Start()
                                print(f"Instance {instance_name} has been rescued")

                            sleep(300)
                        except:
                            InstanceAPI.Login()

                else:
                    print(f"Instance Offline: {instance_name}")

if __name__ == "__main__":
    watchdog("the non-friendly instance name1")