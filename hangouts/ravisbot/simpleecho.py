import asyncio, json, logging

from sinks.base_bot_request_handler import AsyncRequestHandler


logger = logging.getLogger(__name__)


class webhookReceiver(AsyncRequestHandler):

    @asyncio.coroutine
    def process_request(self, path, query_string, content):
        path = path.split("/")
        parsed_content = json.loads(content)
        if parsed_content["to"] == "developers":
            dev_convs = self.bot.user_memory_get("0", "devregistered")
            if dev_convs:
                for conv in dev_convs:
                    yield from self.bot.coro_send_message(conv, parsed_content["message"])

        elif parsed_content["to"] == "tpb":
            yield from self.bot.coro_send_message(parsed_content["tpbrecipient"], parsed_content["message"])

        else:
            pass
