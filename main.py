from bs4 import BeautifulSoup
import requests
import os

def write_image(imagesrc) -> None:
    r = requests.get("https://brickshelf.com" + imagesrc, stream=True)
    if r.status_code != 200:
        print("Error requesting image: ", imagesrc)
        exit(-2)
    
    cwd = os.getcwd()
    path = os.path.join(cwd, *imagesrc.split('/')[:-1])
    #print("dir path:", path)
    if not os.path.exists(path):
        os.makedirs(path)
    fpath = os.path.join(cwd, *imagesrc.split('/'))
    #print("file path to write: ", fpath)
    with open(fpath, 'wb') as f:
        for chunk in r:
            f.write(chunk)
    print("file ", fpath, " written successfully")
    return
def find_relev_images(soup) -> list[str]:
    ret_imgs = []
    imgs = soup.find_all('a')
    #print("imgsoup: ", imgs)
    for img in imgs:
        if "/cgi-bin/gallery.cgi?i=" in img['href']:
            #print("found img page: ", img['href'])
            imgsoup = soupify_link("https://brickshelf.com" + img['href'])
            imgsrc = imgsoup.find_all('img')[1]["src"]
            #print("got image src: ", imgsrc)
            ret_imgs.append(imgsrc)
    #print("ret_imgs: ", ret_imgs)
    return ret_imgs


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
    s = []
    discovered = {}
     
    with open("links.txt", "r") as f:
        for link in [x.strip() for x in f.readlines()]:
            s.append(link)
    print("scraping these links: ", s)
    while s:
        link = s.pop()
        if link not in discovered:
            print("new link being scraped: ", link)
            discovered[link] = 1
            soup = soupify_link(link)
            #print("calling find_relev_images...")
            images = find_relev_images(soup)
            #print("image src urls: ", images)
            for image in images:
                #print("attempt writing image: ", image)
                write_image(image)

            folders = get_folders(soup)
            for folder in folders:
                s.append(folder)

if __name__ == "__main__":
    main()

