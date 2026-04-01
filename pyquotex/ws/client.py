"""Module for Quotex websocket."""
import json
import os
import time
import logging
from pathlib import Path
import websocket

logger = logging.getLogger(__name__)


class WebsocketClient:
    """Class for work with Quotex API websocket."""

    def __init__(self, api):
        """
        :param api: The instance of :class:`QuotexAPI
            <pyquotex.api.QuotexAPI>`.
        trace_ws: Enables and disable `enableTrace` in WebSocket Client.
        """
        self.api = api
        self.state = api.state
        self.headers = {
            "User-Agent": self.api.session_data.get("user_agent"),
            "Origin": self.api.https_url,
            "Host": f"ws2.{self.api.host}",
        }

        websocket.enableTrace(self.api.trace_ws)
        self.wss = websocket.WebSocketApp(
            self.api.wss_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
            header=self.headers,
            cookie=self.api.session_data.get("cookies")
        )

    def on_message(self, wss, msg):
        """Method to process websocket messages."""
        self.state.ssl_Mutual_exclusion = True
        current_time = time.localtime()
        if current_time.tm_sec in [0, 5, 10, 15, 20, 30, 40, 50]:
            self.wss.send('42["tick"]')
        try:
            if "authorization/reject" in str(msg):
                logger.warning("Token rejected, making automatic reconnection.")
                self.state.check_rejected_connection = 1
            elif "s_authorization" in str(msg):
                self.state.check_accepted_connection = 1
                self.state.check_rejected_connection = 0
            elif "instruments/list" in str(msg):
                self.state.started_listen_instruments = True

            msg_str = msg.decode("utf-8", errors="ignore") if isinstance(msg, bytes) else str(msg)
            message = msg_str # Keep the full string as default if logic downstream expects it
            
            if len(msg_str) > 1:
                msg_parsed_str = msg_str[1:]
                logger.debug(msg_parsed_str)
                try:
                    message_json = json.loads(msg_parsed_str)
                    message = message_json # Overwrite with dict only if parsing succeeds
                    self.api.wss_message = message
                    if "call" in str(message) or 'put' in str(message):
                        self.api.instruments = message
                except (ValueError, TypeError):
                    pass
                if isinstance(message, dict):
                    if message.get("signals"):
                        time_in = message.get("time")
                        for i in message["signals"]:
                            try:
                                self.api.signal_data[i[0]] = {}
                                self.api.signal_data[i[0]][i[2]] = {}
                                self.api.signal_data[i[0]][i[2]]["dir"] = i[1][0]["signal"]
                                self.api.signal_data[i[0]][i[2]]["duration"] = i[1][0]["timeFrame"]
                            except (KeyError, IndexError, TypeError):
                                self.api.signal_data[i[0]] = {}
                                self.api.signal_data[i[0]][time_in] = {}
                                self.api.signal_data[i[0]][time_in]["dir"] = i[1][0][1]
                                self.api.signal_data[i[0]][time_in]["duration"] = i[1][0][0]
                    elif message.get("liveBalance") or message.get("demoBalance"):
                        self.api.account_balance = message
                    elif message.get("position"):
                        self.api.top_list_leader = message
                    elif len(message) == 1 and message.get("profit", -1) > -1:
                        self.api.profit_today = message
                    elif message.get("index"):
                        # Correlation ID pattern: resolve which asset this
                        # response belongs to via _pending_history_requests.
                        idx = message.get("index")
                        asset = self.api._pending_history_requests.pop(idx, None)
                        if asset is not None:
                            self.api.historical_candles[asset] = message
                        else:
                            logger.warning(
                                "history/load/line response with unknown index %s — "
                                "response dropped to avoid routing to wrong asset.", idx
                            )
                        if message.get("closeTimestamp"):
                            self.api.timesync.server_timestamp = message.get("closeTimestamp")
                    if message.get("pending"):
                        # Index by ticket so concurrent open_pending calls stay isolated.
                        ticket = message["pending"]["ticket"]
                        self.api.pending_successful[ticket] = message
                        self.api.pending_id[ticket] = ticket
                    elif message.get("id") and not message.get("ticket"):
                        # Index by operation_id so concurrent buy calls stay isolated.
                        op_id = message["id"]
                        self.api.buy_successful[op_id] = message
                        self.api.buy_id[op_id] = op_id
                        if message.get("closeTimestamp"):
                            self.api.timesync.server_timestamp = message.get("closeTimestamp")
                    elif message.get("ticket") and not message.get("id"):
                        self.api.sold_options_respond = message
                    elif message.get("deals"):
                        for get_m in message["deals"]:
                            deal_id = get_m.get("id")
                            self.api.profit_in_operation[deal_id] = get_m["profit"]
                            get_m["win"] = True if get_m["profit"] > 0 else False
                            get_m["game_state"] = 1
                            self.api.listinfodata.set(
                                get_m["win"],
                                get_m["game_state"],
                                deal_id
                            )
                    elif message.get("isDemo") and message.get("balance"):
                        self.api.training_balance_edit_request = message
                    elif message.get("error"):
                        self.state.websocket_error_reason = message.get("error")
                        self.state.check_websocket_if_error = True
                        if self.state.websocket_error_reason == "not_money":
                            self.api.account_balance = {"liveBalance": 0}
                    elif not message.get("list") == []:
                        self.api.wss_message = message
            if str(message) == "41":
                logger.info("Disconnection event triggered by the platform, causing automatic reconnection.")
                self.state.check_websocket_if_connect = 0
            if "51-" in str(message):
                self.api._temp_status = str(message)
            elif self.api._temp_status == """451-["settings/list",{"_placeholder":true,"num":0}]""":
                self.api.settings_list = message
                self.api._temp_status = ""
            elif self.api._temp_status == """451-["history/list/v2",{"_placeholder":true,"num":0}]""":
                message_asset = message.get("asset")
                if message_asset:
                    # Route by asset from payload — never use current_asset
                    # here, as multiple concurrent requests would collide.
                    self.api.candles.set(message_asset, message.get("history"))
                    self.api.candle_v2_data[message_asset] = message
                    self.api.candle_v2_data[message_asset]["candles"] = [{
                        "time": candle[0],
                        "open": candle[1],
                        "close": candle[2],
                        "high": candle[3],
                        "low": candle[4],
                        "ticks": candle[5]
                    } for candle in message["candles"]]
                self.api._temp_status = ""
            elif isinstance(message, list) and len(message) > 0 and isinstance(message[0], list) and len(message[0]) == 4:
                result = {
                    "time": message[0][1],
                    "price": message[0][2]
                }
                # Asset name is position [0][0] in the payload — use it
                # directly instead of the global current_asset.
                asset_name = message[0][0]
                if asset_name in self.api.realtime_price:
                    self.api.realtime_price[asset_name].append(result)
                    if len(self.api.realtime_price[asset_name]) > 1000:
                        self.api.realtime_price[asset_name].pop(0)
                self.api.realtime_candles[asset_name] = message[0]
            elif isinstance(message, list) and len(message) > 0 and isinstance(message[0], list) and len(message[0]) == 2:
                for i in message:
                    result = {
                        "sentiment": {
                            "sell": 100 - int(i[1]),
                            "buy": int(i[1])
                        }
                    }
                    self.api.realtime_sentiment[i[0]] = result
        except Exception as e:
            logger.error("Unhandled error in on_message: %s", e)
        self.state.ssl_Mutual_exclusion = False

    def on_error(self, wss, error):
        """Method to process websocket errors."""
        logger.error(error)
        self.state.websocket_error_reason = str(error)
        self.state.check_websocket_if_error = True

    def on_open(self, wss):
        """Method to process websocket open.

        No asset-specific subscriptions are sent here. Restoring all active
        instrument subscriptions after a (re)connect is the exclusive
        responsibility of stable_api.re_subscribe_stream(), which holds
        the full authoritative list (subscribe_candle, subscribe_candle_all_size,
        subscribe_mood) and can correctly restore *all* instruments — not just
        a single global default asset.
        """
        logger.info("Websocket client connected.")
        self.state.check_websocket_if_connect = 1
        self.wss.send('42["tick"]')
        self.wss.send('42["indicator/list"]')
        self.wss.send('42["drawing/load"]')
        self.wss.send('42["pending/list"]')
        self.wss.send('42["chart_notification/get"]')
        self.wss.send('42["tick"]')

    def on_close(self, wss, close_status_code, close_msg):
        """Method to process websocket close."""
        logger.info("Websocket connection closed.")
        self.state.check_websocket_if_connect = 0

    def on_ping(self, wss, ping_msg):
        pass

    def on_pong(self, wss, pong_msg):
        self.wss.send("2")
