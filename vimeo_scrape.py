from bs4 import BeautifulSoup
import requests, sys
import pdb

VIMEO_URL = "http://vimeo.com%s"

class UserVideos:
  VIDEOS_URL = VIMEO_URL % "/%(name)s/videos"

  def __init__(self, name):
    self.name = name

  def download(self):
    map(self.__download_page, self.__pages())

  def __download_page(self, page_url):
    video_links = VideoLinks(page_url, ".browse_videos a")
    urls_and_titles = zip(video_links.urls(), video_links.titles())
    for url_and_title in urls_and_titles:
      video = UserVideo(*url_and_title)
      video.download()

  def __pages(self):
    videos_url = self.VIDEOS_URL % {"name": self.name}
    page_urls = PageLinks(videos_url, "#pagination a").urls()
    return set(page_urls)

class UserVideo:
  VIDEO_FILE = "videos/%(title)s.mp4"

  def __init__(self, url, title):
    self.url = url
    self.title = title

  def download(self):
    file_name = self.VIDEO_FILE % {"title": self.title}
    video_file = open(file_name, "w")
    video_content = requests.get(self.__download_url()).content
    video_file.write(video_content)

  # Vimeo did not want to play nice
  def __download_url(self):
    soup = Soup.make(self.url)
    data_url = soup.select(".player")[0]['data-config-url']
    data = requests.get(data_url).json()
    return data['request']['files']['h264']['sd']['url']

class Soup:
  @staticmethod
  def make(url):
    html = requests.get(url).text
    return BeautifulSoup(html, "html5lib")

class PageLinks:
  def __init__(self, page_url, selector):
    page_soup = Soup.make(page_url)
    self.links = page_soup.select(selector)

  def urls(self):
    return map(self.__url_from_link, self.links)

  def __url_from_link(self, link):
    return VIMEO_URL % link["href"]

class VideoLinks(PageLinks):
  def titles(self):
    return map(self.__title_from_link, self.links)

  def __title_from_link(self, link):
    title_element = link.select(".title")[0]
    return title_element.get_text(strip=True)

user_name = sys.argv[1]
user_videos = UserVideos(user_name)
user_videos.download()
