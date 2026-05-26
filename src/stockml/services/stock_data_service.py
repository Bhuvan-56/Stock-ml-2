"""Application service for stock market history retrieval."""

from __future__ import annotations

from datetime import date

from stockml.core.config import MarketDataSettings
from stockml.core.exceptions import InvalidRequestError
from stockml.domain.models import StockHistory, StockHistoryRequest
from stockml.domain.protocols import StockDataProvider


class StockDataService:
    """Validate stock history requests and delegate retrieval to a provider."""

    def __init__(self, provider: StockDataProvider, settings: MarketDataSettings) -> None:
        self._provider = provider
        self._settings = settings

    def get_history(
        self,
        *,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str | None = None,
    ) -> StockHistory:
        """Fetch normalized stock history for an explicit date window."""

        request = self.build_request(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )
        return self._provider.get_history(request)

    def get_default_history(
        self,
        *,
        symbol: str,
        as_of: date | None = None,
    ) -> StockHistory:
        """Fetch the default trailing history window configured for the backend."""

        reference_date = as_of or date.today()
        start_date = self._subtract_years(reference_date, self._settings.default_history_years)
        return self.get_history(
            symbol=symbol,
            start_date=start_date,
            end_date=reference_date,
            interval=self._settings.interval,
        )

    def build_request(
        self,
        *,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str | None = None,
    ) -> StockHistoryRequest:
        """Create a validated stock history request for provider consumption."""

        try:
            return StockHistoryRequest(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval or self._settings.interval,
            )
        except ValueError as exc:
            raise InvalidRequestError(str(exc)) from exc

    @staticmethod
    def _subtract_years(value: date, years: int) -> date:
        """Subtract whole calendar years while handling leap-day rollover."""

        try:
            return value.replace(year=value.year - years)
        except ValueError:
            return value.replace(month=2, day=28, year=value.year - years)
