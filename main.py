from bs4 import BeautifulSoup
import requests
import os

with open("links.txt", "r") as f:
    for link in [x.strip() for x in f.readlines()]:
        r = requests.get(link)
        if r.status_code != 200:
            print("Failed webpage request: ", link)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')



def write_image(path, image) -> None:
    return 

def find_relev_images(soup) -> list[str]:
    imgs = soup.find_all('img')
    for img in imgs:
        if "/cgi-bin/gallery.cgi?i=" in img['src']:
            imgsoup = soupify_link("https://brickshelf.com" + img['src'])
            
    return []


def soupify_link(link):
    r = requests.get(link)
    if r.status_code != 200:
        print("Error requesting link: ", link)
        exit(-1)

    return BeautifulSoup(r.text, "html.parser")

def get_folders(soup: BeautifulSoup):
    folders = []
    for a in soup.find_all('a'):
        link = a["href"]
        if "/cgi-bin/gallery.cgi?f=" in link and a.string != 'UP' :
            folders.append("https://brickshelf.com" + link)
    return folders

def main():
    cwd = os.getcwd()
    s = []
    discovered = {}
     
    with open("links.txt", "r") as f:
        for link in [x.strip() for x in f.readlines()]:
            s.append(link)

    while s:
        link = s.pop()
        if link not in discovered:
            discovered[link] = 1
            soup = soupify_link(link)
            images = find_relev_images(soup)
            for image in images:
                write_image("images", image)

            folders = get_folders(soup)
            for folder in folders:
                s.append(folder)
            
