from pydispatch import dispatcher

from smallder.utils.utils import singleton


@singleton
class CustomSignalManager:
    def __init__(self):
        self.custom_signals = {
            "SPIDER_STARTED": "SPIDER_STARTED",
            "SPIDER_STOPPED": "SPIDER_STOPPED",
            "SPIDER_STATS": "SPIDER_STATS"
        }

    def register_signal(self, signal_name):
        if signal_name not in self.custom_signals:
            self.custom_signals[signal_name] = signal_name
            return signal_name
        else:
            raise ValueError(f"Signal {signal_name} already exists.")

    def connect(self, signal_name, handler):
        if signal_name in self.custom_signals:
            dispatcher.connect(handler, signal=signal_name)
        else:
            raise ValueError(f"Signal {signal_name} not found.")

    def send(self, signal_name, **kwargs):
        if signal_name in self.custom_signals:
            dispatcher.send(signal=signal_name, **kwargs)
        else:
            raise ValueError(f"Signal {signal_name} not found.")
