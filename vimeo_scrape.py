from bs4 import BeautifulSoup
import requests, sys
import pdb

VIMEO_URL = "http://vimeo.com%s"

class UserVideos:
  VIDEOS_URL = VIMEO_URL % "/%(name)s/videos"

  def __init__(self, name):
    self.name = name

  def download(self):
    for page in self.__pages(): page.download()

  def __pages(self):
    videos_url = self.VIDEOS_URL % {"name": self.name}
    page_urls = PageLinks(videos_url, "#pagination a").urls()
    return map(VideosPage, set(page_urls))

class VideosPage:
  def __init__(self, url):
    self.url = url

  def download(self):
    video_links = VideoLinks(self.url, ".browse_videos a")
    for video in video_links.videos(): video.download()

class Video:
  VIDEO_FILE = "videos/%(title)s.mp4"

  def __init__(self, url, title):
    self.url = url
    self.title = title

  def download(self):
    file_name = self.VIDEO_FILE % {"title": self.title}
    video_file = open(file_name, "w")
    video_content = requests.get(self.__download_url()).content
    video_file.write(video_content)

  def __download_url(self):
    dom = Dom.build(self.url)
    data_url = dom.select(".player")[0]['data-config-url']
    data = requests.get(data_url).json()
    return data['request']['files']['h264']['sd']['url']

class Dom:
  @staticmethod
  def build(url):
    html = requests.get(url).text
    return BeautifulSoup(html, "html5lib")

class PageLinks:
  def __init__(self, url, selector):
    dom = Dom.build(url)
    self.links = dom.select(selector)

  def urls(self):
    return map(self.__url_from_link, self.links)

  def __url_from_link(self, link):
    return VIMEO_URL % link["href"]

class VideoLinks(PageLinks):
  def titles(self):
    return map(self.__title_from_link, self.links)

  def videos(self):
    urls_and_titles = zip(self.urls(), self.titles())
    return [Video(*url_and_title) for url_and_title in urls_and_titles]

  def __title_from_link(self, link):
    title_element = link.select(".title")[0]
    return title_element.get_text(strip=True)

user_name = sys.argv[1]
user_videos = UserVideos(user_name)
user_videos.download()
