from pyquotex.ws.objects.base import Base


class Candle(object):
    """Class for Quotex candle."""

    def __init__(self, candle_data):
        """
        :param candle_data: The list of candles data.
        """
        self.__candle_data = candle_data

    @property
    def candle_time(self):
        """Property to get candle time.

        :returns: The candle time.
        """
        return self.__candle_data[0]

    @property
    def candle_open(self):
        """Property to get candle open value.

        :returns: The candle open value.
        """
        return self.__candle_data[1]

    @property
    def candle_close(self):
        """Property to get candle close value.

        :returns: The candle close value.
        """
        return self.__candle_data[2]

    @property
    def candle_high(self):
        """Property to get candle high value.

        :returns: The candle high value.
        """
        return self.__candle_data[3]

    @property
    def candle_low(self):
        """Property to get candle low value.

        :returns: The candle low value.
        """
        return self.__candle_data[4]

    @property
    def candle_type(self):
        """Property to get candle type value.

        :returns: The candle type value.
        """
        if self.candle_open < self.candle_close:
            return "green"
        elif self.candle_open > self.candle_close:
            return "red"


class Candles(Base):
    """Class for Quotex Candles websocket object.

    Stores candle data per-asset to support concurrent multi-asset
    subscriptions without race conditions.
    """

    def __init__(self):
        super(Candles, self).__init__()
        self.__name = "candles"
        # Dict keyed by asset name — replaces the old single scalar.
        self.__candles_data = {}

    # ------------------------------------------------------------------
    # Per-asset API (preferred for concurrent usage)
    # ------------------------------------------------------------------

    def get(self, asset: str):
        """Return candles data for a specific asset, or None if not set."""
        return self.__candles_data.get(asset)

    def set(self, asset: str, data):
        """Store candles data for a specific asset."""
        self.__candles_data[asset] = data

    def clear(self, asset: str):
        """Reset candles data for a specific asset to None (sentinel value
        used by polling loops to detect when fresh data has arrived)."""
        self.__candles_data[asset] = None

    # ------------------------------------------------------------------
    # Legacy property — exposes the full dict for backward compatibility.
    # Do NOT use for routing; always prefer get()/set()/clear().
    # ------------------------------------------------------------------

    @property
    def candles_data(self):
        """Property to get the full per-asset candles data dict.

        :returns: dict mapping asset names to their candles data.
        """
        return self.__candles_data

    @candles_data.setter
    def candles_data(self, candles_data):
        """Legacy setter — replaces the entire dict."""
        self.__candles_data = candles_data

    # ------------------------------------------------------------------
    # Convenience accessors (operate on the last asset in the dict,
    # kept for backward compatibility only).
    # ------------------------------------------------------------------

    def _last_data(self):
        """Return data for the most recently updated asset, or None."""
        if not self.__candles_data:
            return None
        return next(reversed(self.__candles_data.values()), None)

    @property
    def first_candle(self):
        """Method to get first candle of the last updated asset.

        :returns: The instance of :class:`Candle
            <pyquotex.ws.objects.candles.Candle>`.
        """
        data = self._last_data()
        return Candle(data[0]) if data else None

    @property
    def second_candle(self):
        """Method to get second candle of the last updated asset.

        :returns: The instance of :class:`Candle
            <pyquotex.ws.objects.candles.Candle>`.
        """
        data = self._last_data()
        return Candle(data[1]) if data else None

    @property
    def current_candle(self):
        """Method to get current candle of the last updated asset.

        :returns: The instance of :class:`Candle
            <pyquotex.ws.objects.candles.Candle>`.
        """
        data = self._last_data()
        return Candle(data[-1]) if data else None
