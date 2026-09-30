from abc import ABC, abstractmethod


class IPlatformSettingsRepository(ABC):
    @abstractmethod
    def get_pricing_promotion(self) -> dict:
        ...

    @abstractmethod
    def set_pricing_promotion(self, settings: dict) -> dict:
        ...
