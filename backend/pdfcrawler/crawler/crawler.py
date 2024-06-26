from .helper import get_content_type, call, clean_url, normalize_url
from .crawl_methods import get_hrefs_html, get_hrefs_js_simple, ClickCrawler
from flask_socketio import emit
from flask import current_app
import time

class Crawler:
    def __init__(self, app, stop_event, socketio, downloader, get_handlers=None, head_handlers=None, follow_foreign_hosts=False, crawl_method="normal", gecko_path="geckodriver", process_handler=None, base_url=None, crawl_in_depth=False):

        # Crawler internals test 
        self.app = app
        self.base_url = base_url
        self.stop_event = stop_event
        self.downloader = downloader
        self.crawl_in_depth = crawl_in_depth
        #self.stop_crawler = stop_crawler
        #self.initial_url = None
        self.socketio = socketio
        self.get_handlers = get_handlers or {}
        self.head_handlers = head_handlers or {}
        self.session = self.downloader.session()
        self.process_handler = process_handler
        # Crawler information
        self.handled = set()
        self.follow_foreign = follow_foreign_hosts
        self.executable_path_gecko = gecko_path
        # these file endings are excluded to speed up the crawling (assumed that urls ending with these strings are actual files)
        self.file_endings_exclude = [".mp3", ".wav", ".mkv", ".flv", ".vob", ".ogv", ".ogg", ".gif", ".avi", ".mov", ".wmv", ".mp4", ".mp3", ".mpg"]

        # 3 possible values:
        # "normal" (default) => simple html crawling (no js),
        # "rendered" => renders page,
        # "rendered-all" => renders page and clicks all buttons/other elements to collect all links that only appear when something is clicked (javascript pagination etc.)
        self.crawl_method = crawl_method

        # load already handled files from folder if available
        # for k, Handler in self.head_handlers.items():
        #     print(Handler)
        #     handled_list = Handler.get_handled_list()
        #     for handled_entry in handled_list:
        #         print("adicionei este url a lista !!!!!!!!!!!!!!!!!!!!")
        #         print(handled_entry)
        #         self.handled.add(clean_url(handled_entry))

    def crawl(self, url, depth, previous_url=None, follow=True):
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        if self.stop_event.is_set():
            return       
        url = clean_url(url)
       # print(f"base url: {self.base_url}")
        #base_url = clean_url(self.base_url)
        # print(f"Base url: {base_url}")
        # if self.initial_url is None:
        #     self.initial_url = url

        if url in self.handled and url[-4:] in self.file_endings_exclude:
            #print(f"Already handled {url}")
            return
        print(f"Crawling {url} with depth {depth} and follow {follow}")
        response = call(self.session, url)
      #  print(f"Response: {response}")
        if not response:
            return

        final_url = clean_url(response.url)

        if final_url in self.handled or final_url[-4:] in self.file_endings_exclude:
         #   print(f"Already handled {final_url}")
            return

        with self.app.app_context():
            self.socketio.emit('new_url', {'url': final_url})

        content_type = get_content_type(response)
        #print(f"Content type: {content_type}")
        #print(f"response: {response} response.url: {response.url}")
        local_name = None

        get_handler = self.get_handlers.get(content_type)
        if get_handler:
            local_name = get_handler.handle(response)

        head_handler = self.head_handlers.get(content_type.strip())
        if head_handler:
            head_handler.handle(response, depth, previous_url, local_name, local_name)
     
        if content_type == "text/html" and depth > 0 and follow:
            print(f"depth: {depth}, follow: {follow}")
            urls = self.get_urls(response)
            self.handled.add(final_url)
           # print(self.handled)

            for next_url in urls:
                contains_pdf = 'pdf' in next_url['url'].lower()
                new_depth = depth if contains_pdf else depth - 1
                if self.base_url is not None and self.crawl_in_depth:
                    #print("Aqui")
                    print(f"Base url: {normalize_url(self.base_url).lower()}")
                    print(f"Next url: {normalize_url(next_url['url']).lower()}")
                    if (normalize_url(self.base_url).lower() not in normalize_url(next_url['url']).lower()) and  not contains_pdf:
                     #   print("False")
                        new_follow = False
                    else:
                        #print("True")
                        new_follow = True
                if not self.crawl_in_depth:
                    new_follow = True
                if new_depth > 0 and new_follow:
                    try:
                    #    print(f"Next url: {next_url['url']}")
                        self.crawl(next_url['url'], new_depth, previous_url=final_url, follow=next_url['follow'])
                    except Exception as e:
                        print(f"Error crawling {next_url['url']}: {e}")
        else:
            self.handled.add(final_url)
            print("no crawling done")

    def get_urls(self, response):
        #print("Getting urls from page...")
        if self.crawl_method == "rendered":
            urls = get_hrefs_js_simple(response, self.follow_foreign)
        elif self.crawl_method == "rendered-all":
            click_crawler = ClickCrawler(self.process_handler, self.executable_path_gecko, response, self.follow_foreign)
            urls = click_crawler.get_hrefs_js_complex()
        else:
            # plain html
            if self.crawl_method is not None and self.crawl_method != "normal":
                print("Invalid crawl method specified, default used (normal)")
            urls = get_hrefs_html(response, self.follow_foreign)

        return urls
