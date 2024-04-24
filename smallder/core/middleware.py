import importlib
import logging
import traceback

logger = logging.getLogger(__name__)


class MiddlewareManager:
    """
    MiddlewareManager is responsible for loading, managing, and executing middleware
    for requests and responses within a spider.
    """

    def __init__(self, spider):
        # Assuming 'middleware_settings' is a dict mapping middleware paths to their priorities
        self.spider = spider
        self.middlewares = spider.custom_settings.get("middleware_settings", {})
        self.loaded_middlewares = []

    def load_middlewares(self):
        for mw_path, priority in self.middlewares.items():
            mw_class = self.load_middleware_class(mw_path)
            if mw_class:
                try:
                    instance = mw_class(self.spider)
                    self.loaded_middlewares.append((instance, priority))
                except Exception as e:
                    logger.error(f"Failed to initialize middleware {mw_path}: {e}")

    def load_middleware_class(self, mw_path: str):

        try:
            module_path, class_name = mw_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load middleware class {mw_path}: {e}")
            return None

    def process_request(self, request):

        for mw_instance, _ in sorted(self.loaded_middlewares, key=lambda x: x[1]):
            try:
                request = mw_instance.process_request(request)
            except AttributeError as e:
                logger.exception(e)
        return request

    def process_response(self, response):

        for mw_instance, _ in sorted(self.loaded_middlewares, key=lambda x: x[1]):
            try:
                response = mw_instance.process_response(response)
            except AttributeError as e:
                logger.exception(e)
        return response
