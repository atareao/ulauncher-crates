import requests
import logging
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

logger = logging.getLogger(__name__)


class CratesExtension(Extension):

    def __init__(self):
        super(CratesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        # self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        searchKeyword = event.get_argument()
        searchSize = extension.preferences['crates_max_search_result_size']
        if not searchKeyword:
            return

        url = f"https://crates.io/api/v1/crates?search={searchKeyword}&per_page={searchSize}&page=1"
        # logger.debug(url)

        response = requests.get(url, headers={'User-Agent': 'ulauncher-crates'})
        if response is not None and response.status_code != 200:
            return

        data = response.json()
        # logger.debug(data)

        items = []
        for crate in data['crates']:
            # logger.debug(package)
            description = f"{crate['description']} ({crate['downloads']})"
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=crate['name'],
                                             description=description,
                                             on_enter=OpenUrlAction(crate['repository'])))

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        return RenderResultListAction([ExtensionResultItem(icon='images/icon.png',
                                                           name=data['name'],
                                                           description=data['description'],
                                                           on_enter=OpenUrlAction(data['respository']))])


if __name__ == '__main__':
    CratesExtension().run()
