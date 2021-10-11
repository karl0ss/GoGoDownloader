# Dependencies
import requests as req
import shutil
import re
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from colorama import Fore


@dataclass(init=True)
class Download:
    name: str
    episode_quality: str
    folder: str
    all_episodes: int
    episode_start: int
    episode_end: int
    printed: bool = False

    def get_links(self, source=None) -> list[str]:
        if source is not None:
            source_ep = f"https://gogoanime.pe/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}"
                for i in range(self.episode_start, self.episode_end + 1)
            ]
            episode_links.insert(0, source)
        else:
            source_ep = f"https://gogoanime.pe/{self.name}-episode-"
            episode_links = [
                f"{source_ep}{i}"
                for i in range(self.episode_start, self.episode_end + 1)
            ]
        return episode_links

    def get_download_links(self, episode_link) -> list[str]:
        with req.get(episode_link) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            exist = soup.find("h1", {"class": "entry-title"})
            if exist is None:
                # Episode link == 200
                episode_link = soup.find("li", {"class": "dowloads"})
                return episode_link.a.get("href")
            else:
                # Episode link == 404
                episode_link = f"{episode_link}-"
                with req.get(episode_link) as res:
                    soup = BeautifulSoup(res.content, "html.parser")
                    exist = soup.find("h1", {"class": "entry-title"})
                    if exist is None:
                        episode_link = soup.find("li", {"class": "dowloads"})
                        return episode_link.a.get("href")
                    else:
                        return None

    def get_download_urls(self, download_link) -> list[str]:
        with req.get(download_link) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            link = soup.find("div", {"class": "mirror_link"}).find(
                "div",
                text=re.compile(fr"\b{self.episode_quality}\b"),
                attrs={"class": "dowload"},
            )
            if link is None:
                link = soup.find("div", {"class": "mirror_link"}).find(
                    "div", {"class": "dowload"}
                )
                if not self.printed:
                    CustomMessage(None, self.episode_quality).qual_not_found()
                    self.episode_quality = link.text.split()[1][1:]
                    CustomMessage(None, self.episode_quality).use_default_qual()
                    self.printed = True
        return [
            download_link.split("+")[-1],
            link.a.get("href"),
        ]  # episode_name: str, episode_link: str

    def download_episodes(self, url) -> object:
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://gogoanime.pe/",
            "Connection": "close",
        }
        with req.get(url[1], headers=header, stream=True) as res:
            episode_name = f"EP.{url[0]}.mp4"
            file_loc = os.path.join(self.folder, episode_name)
            with open(file_loc, "wb") as file:
                shutil.copyfileobj(res.raw, file, 8192)


@dataclass(init=True)
class CustomMessage(Exception):
    """Custom message that will accept message as a parameter and it will print it on the console."""

    message: str = None
    episode_quality: str = None

    def print_error(self) -> str:
        print(self.message)

    def qual_not_found(self) -> str:
        print(
            f"[{Fore.RED}-{Fore.RESET}] {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} quality not found."
        )

    def use_default_qual(self) -> str:
        print(
            f"[{Fore.GREEN}+{Fore.RESET}] Using {Fore.LIGHTCYAN_EX}{self.episode_quality}{Fore.RESET} as a default quality."
        )
