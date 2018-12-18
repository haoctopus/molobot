"""Client protocol class for Molobot."""
import re
import copy
import asyncore
import queue
import socket
import time
import json
import hashlib
import traceback

from homeassistant.const import __short_version__

from .const import (BUFFER_SIZE, CLIENT_VERSION, CONFIG_FILE_NAME)
from .molo_client_app import MOLO_CLIENT_APP
from .molo_client_config import MOLO_CONFIGS
from .molo_socket_helper import MoloSocketHelper
from .molo_tcp_pack import MoloTcpPack
from .utils import LOGGER, dns_open, get_rand_char, save_local_seed
from homeassistant.helpers.json import JSONEncoder


class MoloBotClient(asyncore.dispatcher):
    """Client protocol class for Molobot."""

    tunnel = {}
    tunnel['protocol'] = 'http'
    tunnel['hostname'] = ''
    tunnel['subdomain'] = ''
    tunnel['rport'] = 0
    tunnel['lhost'] = MOLO_CONFIGS.get_config_object()['ha']['host']
    tunnel['lport'] = MOLO_CONFIGS.get_config_object()['ha']['port']

    client_id = ''
    client_token = ''

    protocol_func_bind_map = {}

    def __init__(self, host, port, map):
        """Initialize protocol arguments."""
        asyncore.dispatcher.__init__(self, map=map)
        self.host = host
        self.port = port
        self.molo_tcp_pack = MoloTcpPack()
        self.ping_dequeue = queue.Queue()
        self.append_recv_buffer = None
        self.append_send_buffer = None
        self.append_connect = None
        self.client_status = None
        self._last_report_device = 0
        self._phone_sign = ''
        self._sync_config = False
        self.clear()
        self.init_func_bind_map()

    def handle_connect(self):
        """When connected, this method will be call."""
        LOGGER.debug("server connected")
        self.append_connect = False
        self.send_dict_pack(
            MoloSocketHelper.molo_auth(CLIENT_VERSION,
                                       MOLO_CLIENT_APP.hass_context,
                                       __short_version__))

    def handle_close(self):
        """When closed, this method will be call. clean itself."""
        LOGGER.debug("server closed")
        self.clear()
        self.close()

        # close all and restart
        asyncore.close_all()

    def handle_read(self):
        """Handle read message."""
        try:
            buff = self.recv(BUFFER_SIZE)
            self.append_recv_buffer += buff
            self.process_molo_tcp_pack()
        except Exception as e:
            LOGGER.info("recv error: %s", e)

    def get_phonesign(self):
        if self._phone_sign:
            return self._phone_sign
        hassconfig = MOLO_CONFIGS.get_config_object().get("hassconfig", {})
        phone = hassconfig.get("phone", "")
        password = hassconfig.get("password", "")
        phone = str(phone and phone or "").strip()
        password = str(password and password or "").strip()
        if not phone or not re.match(r'1\d{10}', phone):
            MOLO_CLIENT_APP.hass_context.components.persistent_notification.async_create(
                "Invalid phone number, please check your configuration.",
                "Molo Bot Infomation", "molo_bot_notify")
            LOGGER.error("hass configuration.yaml haweb phone error")
            self._phone_sign = "null"
            return self._phone_sign

        hkey = ("molobot:%s:%s" % (phone, password)).encode('utf-8')
        self._phone_sign = hashlib.sha1(hkey).hexdigest()
        return self._phone_sign

    def sync_device(self, force=False, interval=180):
        now = time.time()
        if (not force) and (now - self._last_report_device < interval):
            return None
        self._last_report_device = now

        self._phone_sign = self.get_phonesign()
        if self._phone_sign == "null":
            return None

        devicelist = MOLO_CLIENT_APP.hass_context.states.async_all()
        jlist = json.dumps(
            devicelist, sort_keys=True, cls=JSONEncoder).encode('UTF-8')
        if not self.client_token or not jlist:
            return None

        body = {
            'Type': 'SyncDevice',
            'Payload': {
                "ClientId": self.client_id,
                'PhoneSign': self._phone_sign,
                'Token': self.client_token,
                'Action': "synclist",
                'List': jlist.decode("UTF-8")
            }
        }
        self.send_dict_pack(body)

    def sync_config(self):
        self._phone_sign = self.get_phonesign()
        if self._phone_sign == "null":
            return False
        
        hassconfig = MOLO_CONFIGS.get_config_object().get("hassconfig", {})
        configcopy =  copy.deepcopy(hassconfig)
        configcopy.update({"phone":"", "password":""})

        jlist = json.dumps(configcopy)
        if not self.client_token or not jlist:
            return False

        body = {
            'Type': 'SyncDevice',
            'Payload': {
                "ClientId": self.client_id,
                'PhoneSign': self._phone_sign,
                'Token': self.client_token,
                'Action': "syncconfig",
                'Data': jlist
            }
        }

        self.send_dict_pack(body)
        return True

    def writable(self):
        """If the socket send buffer writable."""
        ping_buffer = MOLO_CLIENT_APP.get_ping_buffer()
        if ping_buffer:
            self.append_send_buffer += ping_buffer

        if not self._sync_config:
            self._sync_config = self.sync_config()

        self.sync_device()
        return self.append_connect or (self.append_send_buffer)

    def handle_write(self):
        """Write socket send buffer."""
        sent = self.send(self.append_send_buffer)
        self.append_send_buffer = self.append_send_buffer[sent:]

    # The above are base class methods.
    def clear(self):
        """Reset client protocol arguments."""
        self.molo_tcp_pack.clear()
        self.append_recv_buffer = bytes()
        self.append_send_buffer = bytes()
        self.append_connect = True
        self.client_status = None

    def sock_connect(self):
        """Connect to host:port."""
        self.clear()
        dns_ip = dns_open(self.host)
        if not dns_ip:
            return
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((dns_ip, self.port))

    def on_bind_status(self, jdata):
        """Handle on_bind_status json packet."""
        LOGGER.debug("on_bind_status %s", str(jdata))
        jpayload = jdata['Payload']
        self.client_status = jpayload['Status']
        jpayload['token'] = self.client_token

    def on_auth_resp(self, jdata):
        """Handle on_auth_resp json packet."""
        LOGGER.debug('on_auth_resp %s', str(jdata))
        self.client_id = jdata['Payload']['ClientId']

        self.send_dict_pack(
            MoloSocketHelper.req_tunnel(self.tunnel['protocol'],
                                        self.tunnel['hostname'],
                                        self.tunnel['subdomain'],
                                        self.tunnel['rport'], self.client_id))

    def on_new_tunnel(self, jdata):
        """Handle on_new_tunnel json packet."""
        LOGGER.debug("on_new_tunnel %s", str(jdata))
        if 'ping_interval' in jdata['OnlineConfig']:
            MOLO_CLIENT_APP.ping_interval = jdata['OnlineConfig'][
                'ping_interval']
        if jdata['Payload']['Error'] != '':
            LOGGER.error('Server failed to allocate tunnel: %s',
                         jdata['Payload']['Error'])
            return

        self.client_token = jdata['Payload']['token']
        self.on_bind_status(jdata)

    def on_token_expired(self, jdata):
        """Handle on_token_expired json packet."""
        LOGGER.debug('on_token_expired %s', str(jdata))
        if 'Payload' not in jdata:
            return
        data = jdata['Payload']
        self.client_token = data['token']

    def on_pong(self, jdata):
        """Handle on_pong json packet."""
        LOGGER.debug('on_pong %s, self token: %s', str(jdata),
                     self.client_token)

    def on_reset_clientid(self, jdata):
        """Handle on_reset_clientid json packet."""
        local_seed = get_rand_char(32).lower()
        save_local_seed(
            MOLO_CLIENT_APP.hass_context.config.path(CONFIG_FILE_NAME),
            local_seed)
        LOGGER.debug("reset clientid %s to %s", self.client_id, local_seed)
        self.handle_close()

    def process_molo_tcp_pack(self):
        """Handle received TCP packet."""
        ret = True
        while ret:
            ret = self.molo_tcp_pack.recv_buffer(self.append_recv_buffer)
            if ret and self.molo_tcp_pack.error_code == MoloTcpPack.ERR_OK:
                self.process_json_pack(self.molo_tcp_pack.body_jdata)
            self.append_recv_buffer = self.molo_tcp_pack.tmp_buffer
        if self.molo_tcp_pack.error_code == MoloTcpPack.ERR_MALFORMED:
            LOGGER.error("tcp pack malformed!")
            self.handle_close()

    def process_json_pack(self, jdata):
        """Handle received json packet."""
        LOGGER.debug("process_json_pack %s", str(jdata))
        if jdata['Type'] in self.protocol_func_bind_map:
            MOLO_CLIENT_APP.reset_activate_time()
            self.protocol_func_bind_map[jdata['Type']](jdata)

    def process_new_tunnel(self, jdata):
        """Handle new tunnel."""
        jpayload = jdata['Payload']
        self.client_id = jpayload['clientid']
        self.client_token = jpayload['token']
        LOGGER.debug("Get client id:%s token:%s", self.client_id,
                     self.client_token)
        data = {}
        data['clientid'] = self.client_id
        data['token'] = self.client_token

    def send_raw_pack(self, raw_data):
        """Send raw data packet."""
        if self.append_connect:
            return
        self.append_send_buffer += raw_data
        self.handle_write()

    def send_dict_pack(self, dict_data):
        """Convert and send dict packet."""
        if self.append_connect:
            return
        body = MoloTcpPack.generate_tcp_buffer(dict_data)
        self.send_raw_pack(body)

    def ping_server_buffer(self):
        """Get ping buffer."""
        if not self.client_status:
            return
        body = MoloTcpPack.generate_tcp_buffer(
            MoloSocketHelper.ping(self.client_token, self.client_status))
        return body

    def on_device_state(self, jdata):
        LOGGER.info("receive device state:%s", jdata)
        jpayload = jdata['Payload']
        action = jpayload.get("action")
        header = jpayload.get("header")
        if action == "control":
            data = jpayload.get("data")
            extdata = "extdata" in data and data.pop("extdata") or None
            exc = {}
            try:
                if isinstance(extdata, (tuple, list)) and len(extdata)>0:
                    ndata = []
                    for info in extdata:
                        dexc = MOLO_CLIENT_APP.hass_context.services.call(
                            info.get("domain"), info.get("service"), info.get("data"), blocking=True)
                        ndata.append(dexc)
                    exc.update(data)
                    exc["extdata"] = ndata
                else:
                    domain = jpayload.get("domain")
                    service = jpayload.get("service")
                    exc = MOLO_CLIENT_APP.hass_context.services.call(
                        domain, service, data, blocking=True)
            except Exception as e:
                exc = traceback.format_exc()

            body = {  # return state where server query
                'Type': 'SyncDevice',
                'Payload': {
                    "Header": header,
                    "ClientId": self.client_id,
                    'PhoneSign': self._phone_sign,
                    'Token': self.client_token,
                    'Action': "synccontrol",
                    'Data': exc
                }
            }
            self.send_dict_pack(body)

        elif action == "query":
            data = jpayload.get("data")
            extdata = "extdata" in data and data.pop("extdata") or None
            state = {}
            if isinstance(extdata, (tuple, list)) and len(extdata)>0:
                ndata = []
                for ent in extdata:
                    st = MOLO_CLIENT_APP.hass_context.states.get(ent)
                    if st:
                        ndata.append(st)
                state.update(data)
                state["extdata"] = ndata
                if len(ndata)<1:
                    return None
            else:
                state = MOLO_CLIENT_APP.hass_context.states.get(
                    data.get("entity_id"))
                if not state:
                    return None

            strst = json.dumps(state, sort_keys=True, cls=JSONEncoder)
            self._phone_sign = self.get_phonesign()
            if self._phone_sign == "null":
                return None

            body = {  # return state where server query
                'Type': 'SyncDevice',
                'Payload': {
                    "Header": header,
                    "ClientId": self.client_id,
                    'PhoneSign': self._phone_sign,
                    'Token': self.client_token,
                    'Action': "syncstate",
                    'Data': strst
                }
            }
            self.send_dict_pack(body)

    def init_func_bind_map(self):
        """Initialize protocol function bind map."""
        self.protocol_func_bind_map = {
            "BindStatus": self.on_bind_status,
            "AuthResp": self.on_auth_resp,
            "NewTunnel": self.on_new_tunnel,
            "TokenExpired": self.on_token_expired,
            "Pong": self.on_pong,
            "ResetClientid": self.on_reset_clientid,
            "DeviceState": self.on_device_state
        }
