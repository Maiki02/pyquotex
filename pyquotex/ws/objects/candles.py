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

    # ------------------------------------------------------------------
    # Legacy positional accessors — REMOVED for concurrent safety.
    #
    # first_candle / second_candle / current_candle previously relied on
    # _last_data(), which returned whichever asset happened to have been
    # updated last in the dict.  In a multi-asset environment this is
    # non-deterministic: a GBPUSD tick arriving a millisecond before you
    # call current_candle will silently return GBPUSD data even if you
    # expected EURUSD.
    #
    # Use Candles.get(asset) directly and index the list yourself:
    #
    #   data = self.api.candles.get("EURUSD")
    #   if data:
    #       open_price  = data[0][1]
    #       close_price = data[0][2]
    # ------------------------------------------------------------------

    def _last_data(self):  # pragma: no cover
        raise NotImplementedError(
            "_last_data() is unsafe in a multi-asset context and has been removed. "
            "Use Candles.get(asset) to retrieve data for a specific asset."
        )

    @property
    def first_candle(self):  # pragma: no cover
        raise NotImplementedError(
            "first_candle is unsafe in a multi-asset context: it returned data for "
            "whichever asset was updated last, which is non-deterministic under "
            "concurrent subscriptions. Use candles.get(asset)[0] instead."
        )

    @property
    def second_candle(self):  # pragma: no cover
        raise NotImplementedError(
            "second_candle is unsafe in a multi-asset context. "
            "Use candles.get(asset)[1] instead."
        )

    @property
    def current_candle(self):  # pragma: no cover
        raise NotImplementedError(
            "current_candle is unsafe in a multi-asset context. "
            "Use candles.get(asset)[-1] instead."
        )
