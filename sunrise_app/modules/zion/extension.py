#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
# Massimiliano Bellino
# Stefano Barbareschi
#********************************************************************************/

import os
import json
import requests

from flask import Flask
from typing import Optional, List

from sunrise_app.modules.zion.models import AlarmStatus, ZionConfig, Device, Scope, AlarmSearchStatus, AlarmSeverity

APPLICATION_JSON = 'application/json'

class ZionInterface:
    config_file_path: str
    config: Optional[ZionConfig]

    devices: List[Device] = []
    
    def __init__(self, config_file_path: str, app: Optional[Flask] = None):
        """inizialize app in Flask

        Args:
            config_file_path (str): the configuration file path
            app (Optional[Flask], optional): Flask object. Defaults to None.
        """
        self.config_file_path = config_file_path
        self.load_config()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """inizialize app through flask

        Args:
            app (Flask): connects flask with zion
        """
        app.extensions[ZionInterface.__name__] = self

    #properties for configuration and token setup
    @property
    def configured(self) -> bool:
        return False if self.config is None else True
    
    @property
    def config_file(self) -> str:
        return os.path.join(self.config_file_path, "config.json")
    
    @property
    def token(self) -> Optional[str]:
        return self.config.token if self.config else None
    
    @token.setter
    def token(self, token: str):
        if self.config:
            self.config.token = token
    
    
    def load_config(self):
        """loads configuration from Zionconfig JSON
        """
        if os.path.exists(self.config_file_path) and os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = ZionConfig.FromJSON(json.load(f))
                self.get_devices()
        else:
            self.config = None
            self.devices = []

    
    def save_config(self, config: ZionConfig):
        """save config to remain configurated

        Args:
            config (ZionConfig): the Zion Configuration
        """
        if not os.path.exists(self.config_file_path):
            os.makedirs(self.config_file_path)

        with open(self.config_file, "w") as f:
            json.dump(config.toJSON(), f, indent=2)

        self.load_config()

   
    def reset_config(self):
        """ remove config file and reloads it
        """
        if os.path.exists(self.config_file_path) and os.path.exists(self.config_file):
            os.remove(self.config_file)

        self.load_config()
    
    def get_shape_blocks(self):
        """the lists that create the basic blocks in Shape used in the Zion Api.
        these are shown as fields dropdowns and are included in the other blocks.

        Returns:
            _type_: dict of lists("devices","scopes","alarmSeverity","alarmSearchStatus")
        """
        return {
            "devices": [(d.name, d.id.id) for d in self.devices],
            "scopes": [(s.name, s.value) for s in Scope],
            "alarmSeverity": [(s.name, s.value) for s in AlarmSeverity],
            "alarmSearchStatus": [(s.name, s.value) for s in AlarmSearchStatus],
        }
    
    def do_post(self, url: str, payload: object) -> Optional[requests.Response]:
        """function used to make a POST request.
        header contains authentication token.
        error 401 is checked in case credentials fail or timeout
        Args:
            url (str): request URL
            payload (object): the message we want to post

        Returns:
            Optional[requests.Response]:request response
        """
        if not self.config:
            return None
        
        if not self.token:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)
            
            if not token:
                return None
            
            self.token = token

        headers = {
            "accept": APPLICATION_JSON,
            "X-Authorization": f"Bearer {self.token}"
        }

        res = requests.post(
            url,
            json=payload,
            headers=headers
            )
        
        if res.status_code == 401:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)
            
            if not token:
                return None
            
            self.token = token            
            return self.do_post(url, payload)
        
        return res

    def do_get(self, url: str) -> Optional[dict]:
        """function used to make a GET request,
        error 401 is checked in case credentials fail or timeout
        Args:
            url (str): request URL
        Returns:
            Optional[dict]: JSON of the response
        """
        if not self.config:
            return None

        if not self.token:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)
            
            if not token:
                return None
            
            self.token = token
        
        headers = {
            "accept": APPLICATION_JSON,
            "X-Authorization": f"Bearer {self.token}"
        }

        res = requests.get(
            url,
            headers=headers
        )

        if res.status_code == 401:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)
            
            if not token:
                return None
            
            self.token = token            
            return self.do_get(url)

        return res.json()
    
    def do_delete(self, url: str) -> Optional[dict]:
        """function used to make a DELETE request,
        error 401 is checked in case credentials fail or timeout
        Args:
            url (str): request URL
        Returns:
            Optional[dict]: response status code
        """

        if not self.config:
            return None
        if not self.token:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)
            if not token:
                return None
            self.token = token

        headers = {
        "accept": APPLICATION_JSON,
        "X-Authorization": f"Bearer {self.token}"
        }

        res = requests.delete(url,headers=headers)


        if res.status_code == 401:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)

            if not token:
                return None
            
            self.token = token        
            return self.do_delete(url)

        return res.json()
        
    
    def refresh_token(self, url, username: str, password: str) -> Optional[str]:
        """make login to refresh auth token

        Args:
            url (_type_): config URL for login
            username (str): config username
            password (str): config password

        Returns:
            Optional[str]: auth token 
        """
        headers = {
            "Content-Type": APPLICATION_JSON,
            "accept": APPLICATION_JSON,
        }

        res = requests.post(
            f"{url}api/auth/login",
            headers=headers,
            json={"username": username, "password": password}
        )
        
        if res.status_code != 200:
            return None
        
        data = res.json()
        return data["token"]
    

    def get_devices(self, size: int = 20, page: int = 0):
        """populate device list trough connection with Zion Devices

        Returns:
            bool: list is populated 
        """     
        if not self.config:
            return False
        
        url = f"{self.config.url}api/tenant/devices?pageSize={size}&page={page}"

        res = self.do_get(url)

        if not res:
            return False
        
        self.devices = []

        for device in res["data"]:
            self.devices.append(
                Device.FromZION(device)
            )

        if res["hasNext"]:
            return self.get_devices(size, page+1)
        
        return True
    
    def device_last_telemetry(self, device_id: str, keys: str = "") -> Optional[dict]:
        """returns the chosen device's last telemetry in json format,
        called by zion_device_last_telemetry

        Args:
            device_id (str): id of device
            keys (str, optional): keys to filter result. Defaults to "".

        Returns:
            Optional[dict]: dictionary
        """
        if not self.config:
            return None
        
        url = f"{self.config.url}api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?useStrictDataTypes=true"
        if keys:
            url += f"&keys={keys}"

        res = self.do_get(url)

        if not res:
            return None

        ret = {}
        for k in res:
            ret[k] = res[k][0]["value"]

        return ret
    
    def device_attr(self, device_id: str, scope: Scope = Scope.SERVER, keys: str = "") -> Optional[dict]:
        """returns all attributes from chosen device,
        called by zion_device_attribute

        Args:
            device_id (str): id of device
            scope (Scope, optional): specifies where the data is searched. Defaults to Scope.SERVER.
            keys (str, optional): can be used to filter. Defaults to "".

        Returns:
            Optional[dict]: dict of device attributes
        """
        if not self.config:
            return None
        
        url = f"{self.config.url}api/plugins/telemetry/DEVICE/{device_id}/values/attributes/{scope.value}"
        if keys:
            url += f"?keys={keys}"

        attributes = self.do_get(url)

        if not attributes:
            return None

        ret = {}
        for attr in attributes:
            ret[attr["key"]] = attr["value"]

        return ret
    
    def device_alarm(self, device_id: str, severity: AlarmSeverity = AlarmSeverity.CRITICAL, search_status: AlarmSearchStatus = AlarmSearchStatus.ACTIVE, size: int = 20, page: int = 0) -> Optional[List[dict]]:
        """Returns a page of alarms for the selected device.
        called by zion_device_alarm
        Args:
            device_id (str): id of device
            severity (AlarmSeverity, optional): severity of alarm. Defaults to AlarmSeverity.CRITICAL.
            search_status (AlarmSearchStatus, optional):one of the AlarmStatus enumeration value. Defaults to AlarmSearchStatus.ACTIVE.
            size (int, optional): Maximum amount of entities in a one page. Defaults to 20.
            page (int, optional): Sequence number of page starting from 0. Defaults to 0.

        Returns:
            Optional[List[dict]]: list of dicts
        """
        if not self.config:
            return None
        
        url = f"{self.config.url}api/alarm/DEVICE/{device_id}?searchStatus={search_status.value}&textSearch={severity.value}&pageSize={size}&page={page}"

        alarms = self.do_get(url)

        if not alarms:
            return None

        ret = []
        for alarm in alarms["data"]:
            ret.append({"id": alarm["id"]["id"], "severity": alarm["severity"], "status": alarm["status"], "startTs": alarm["startTs"]})

        if alarms["hasNext"]:
            others = self.device_alarm(device_id, severity, search_status, size, page+1)
            if others:
                ret.extend(others)

        return ret
      
    def send_device_last_telemetry(self, device_id: str, payload: dict) -> bool:
        """Creates or updates the device time-series data based on the device Id and request payload.
        Args:
            device_id (str): id of device
            payload (dict): dict of keys and value we want to send

        Returns:
            bool: response code is 200
        """
        if not self.config:
            return False
        
        url = f"{self.config.url}api/plugins/telemetry/DEVICE/{device_id}/timeseries/ANY?scope=ANY"

        res = self.do_post(url, payload)
        

        if not res:
            return False
        
        return res.status_code == 200
    
    def send_device_attr(self, device_id: str, payload: dict, scope: Scope = Scope.SERVER) -> bool:
        if not self.config:
            return False
        
        url = f"{self.config.url}api/plugins/telemetry/{device_id}/{scope.value}"

    
        res = self.do_post(url, payload)

        if not res:
            return False
        
        return res.status_code == 200
    
    def upsert_device_alarm(self, device_id: str, alarm_name: str, alarm_type: str, severity: AlarmSeverity = AlarmSeverity.CRITICAL, status: AlarmStatus = AlarmStatus.CLEARED_UNACK) -> bool:
        """insert or update device alarm,
         called by zion_send_device_alarm
        Args:
            device_id (str): id of device
            alarm_name (str): alarm's name
            alarm_type (str): alarm's type
            severity (AlarmSeverity, optional): severity of alarm. Defaults to AlarmSeverity.CRITICAL.
            status (AlarmStatus, optional): alarm's status. Defaults to AlarmStatus.CLEARED_UNACK.

        Returns:
            bool: connection was successful
        """
        if not self.config:
            return False
        
        url = f"{self.config.url}api/alarm"

        device = list(filter(lambda d: d.id.id == device_id, self.devices))

        if not device:
            return False
        
        payload = device[0].to_alarm()
        payload["name"] = alarm_name
        payload["type"] = alarm_type
        payload["severity"] = severity.value
        payload["status"] = status.value

        res = self.do_post(url, payload)

        if not res:
            return False

        return True

    def delete_device_attr(self, device_id: str, scope: Scope = Scope.SERVER, key : str="") -> bool:
        """delete device's attribute, 
        called by zion_delete_device_attr

        Args:
            device_id (str): device's id 
            scope (Scope, optional): where the data needs to be searched. Defaults to Scope.SERVER.
            key (str): specifies the key we want to delete. Defaults to "".

        Returns:
            bool: operation result
        """      
        if not self.config:
            return False
        if not self.token:
            token = self.refresh_token(self.config.url, self.config.username, self.config.password)
            if not token:
                return False
            self.token = token
        
        url = f"{self.config.url}api/plugins/telemetry/DEVICE/{device_id}/{scope}?keys={key}"

        res = self.do_delete(url)
    
        if res==200:
            return True
        else:
            return False