"""
Support for Molobot.

For more details about this component, please refer to the documentation at
https://github.com/haoctopus/molobot
"""

from homeassistant.const import (EVENT_HOMEASSISTANT_START,
                                 EVENT_HOMEASSISTANT_STOP, EVENT_STATE_CHANGED)

from .molo_client_config import MOLO_CONFIGS
from .molo_client_app import MOLO_CLIENT_APP
from .utils import LOGGER

DOMAIN = 'molobot'
NOTIFYID = 'molobotnotifyid'
VERSION = 101

def setup(hass, config):
    """Set up molobot component."""
    LOGGER.info("Begin setup molobot!")

    # Load config mode from configuration.yaml.
    cfg = config[DOMAIN]
    cfg.update({"__version__": VERSION})

    if 'mode' in cfg:
        MOLO_CONFIGS.load(cfg['mode'])
    else:
        MOLO_CONFIGS.load('release')

    if 'http' in config and 'server_host' in config['http']:
        tmp_host = config['http']['server_host']
        MOLO_CONFIGS.get_config_object()['ha']['host'] = tmp_host
    if 'http' in config and 'server_port' in config['http']:
        tmp_port = config['http']['server_port']
        MOLO_CONFIGS.get_config_object()['ha']['port'] = tmp_port

    MOLO_CONFIGS.get_config_object()["hassconfig"] = cfg

    async def stop_molobot(event):
        """Stop Molobot while closing ha."""
        LOGGER.info("Begin stop molobot!")
        from .molo_bot_main import stop_aligenie
        stop_aligenie()

    async def start_molobot(event):
        """Start Molobot while starting ha."""
        LOGGER.debug("molobot started!")
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_molobot)

    async def on_state_changed(event):
        """Disable the dismiss button."""
        if MOLO_CLIENT_APP.molo_client:
            MOLO_CLIENT_APP.molo_client.sync_device(True, 2)

    from .molo_bot_main import run_aligenie
    run_aligenie(hass)

    if not cfg.get("disablenotify", False):
        hass.components.persistent_notification.async_create(
            "Welcome to molobot!", "Molo Bot Infomation", "molo_bot_notify")

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, start_molobot)
    hass.bus.async_listen(EVENT_STATE_CHANGED, on_state_changed)

    return True
