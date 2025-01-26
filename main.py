from bs4 import BeautifulSoup
import requests
import os
import re
import time
import datetime
import json

# Prevents scrapper from scraping folders above the gallery you want. Turn this to False (case-sensitive) if you don't care 
DontCheckFoldersAboveGallery = True 

imgset = {}
dateData = ["uploaded", "created", "modified"]

def get_data(text, string, *args):
    #text = soup.get_text()
    myItem = ""
    for item in text.splitlines():
        if "©1998-2020 Brickshelf II, LLC." in item: # skip footer
            continue 
        if string in item: 
            myItem = item
            break 
                
    if myItem == "": 
        return 
        
    # translate to datetime if date
    skipDateTime = False 
    for arg in args: 
        skipDateTime = True 
    
    for date in dateData:
        if date in myItem: 
            if skipDateTime == False: 
                num = [int(x) for x in re.findall(r'\d+', myItem)]
                return datetime.datetime(num[0], num[1], num[2], num[3], num[4], num[5])
            else: # remove first two words 
                myItem = myItem.partition(': ')[2] # Not generally good, but works here 

    return myItem

def write_image(imagesrc) -> None:
    cwd = os.getcwd()
    path = os.path.join(cwd, *imagesrc.split('/')[:-1])
    print("dir imagesrc:", imagesrc)
    if not os.path.exists(path):
        os.makedirs(path)
    fpath = os.path.join(cwd, *imagesrc.split('/'))
    print("file to write: ", fpath)
    
    timeout_delay = 5
    while True:
        try:
            print("Requesting URL: https://brickshelf.com", imagesrc)
            r = requests.get("https://brickshelf.com" +
                             imagesrc, stream=True, timeout=timeout_delay)
            r.raise_for_status()
            if r.status_code == 200:
                break
        except requests.exceptions.Timeout:
            print("Request timed out. Retrying...")
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error")
            print(errh.args[0])
        except requests.exceptions.ConnectionError as conerr:
            print("Connection error: ", conerr)
        except requests.exceptions.RequestException as err:
            print("General Error???", err, "Retrying...")
        timeout_delay += 5

    try: 
        length = int(r.headers['Content-length'])

        with open(fpath, 'wb') as f:
            for i, chunk in enumerate(r.iter_content(1024 * 1024)):
                print("%2.2f  percent written       \r" %
                      (i*1024*1024/length*100), end='', flush=True)
                f.write(chunk)
    except: # directly download data
        with open(fpath, 'wb') as f: 
            f.write(r.content)
    
    for item, value in imgset.items(): 
        if item in fpath: 
            os.utime(fpath, (value["date"], value["date"]))
            
    print("file ", fpath, " written successfully")
    return

def write_info(desc, img, soup, link) -> None:
    cwd = os.getcwd()
    path = os.path.join(cwd, *img.split('/')[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    pathName = os.path.basename(path)
    path = os.path.join(path, "info.json")
    
    soupText = soup.get_text()
    created = get_data(soupText, "created", True)
    modified = get_data(soupText, "modified", True)
    views = get_data(soupText, "Views")
    tags = get_data(soupText, "Keywords")

    fileset = {}
    for item, value in imgset.items():
        date = datetime.datetime.fromtimestamp(value["date"]).strftime('%Y/%m/%d %H:%M:%S')
        mySet = { # this is kinda stupid
            "Link":value["link"],
            "Uploaded":date,
            "Views":value["views"]
        }
        fileset[item] = mySet
    
    myTags = tags.split(" ")
    myTags.remove("Folder")
    myTags.remove("Keywords:")
    myJson = {
        "Link":link,
        "Title":pathName,
        "Description":desc,
        "Created":created,
        "Modified":modified, 
        "Views":[int(x) for x in re.findall(r'\d+', views)][0],
        "Tags":myTags,
        "Files":fileset
    }
    
    #json_object = json.dumps(myJson, indent=8)
    with open(path, 'w') as f:
        json.dump(myJson, f)
        #f.write(json_object)
                
    print("file ", path, " written successfully")
    return   

def src_name(imgsrc):
    listforname = imgsrc.split("/")
    name = listforname[len(listforname)-1]
    return name 

def find_relev_images(soup) -> list[str]:
    ret_imgs = []
    imgs = soup.find_all('a')
    # print("imgsoup: ", imgs)
    p = re.compile(r"/gallery/.+\..+")
    
    soupText = soup.get_text()
    gallerydate = get_data(soupText, "created").timestamp()
    #print(str(gallerydate))

    for img in imgs:
        m = p.match(img["href"])
        if "/cgi-bin/gallery.cgi?i=" in img['href']:
            imgsoup = soupify_link("https://brickshelf.com" + img['href'])
            imgtext = imgsoup.get_text()
            imgsrc = imgsoup.find_all('img')[1]["src"]
            imgdate = get_data(imgtext, "uploaded").timestamp()
            imgviews = get_data(imgtext, "Views")
            imgset[src_name(imgsrc)] = {
                "date":imgdate, 
                "views":[int(x) for x in re.findall(r'\d+', imgviews)][0], 
                "link":"https://brickshelf.com" + img['href']
            } 
            ret_imgs.append(imgsrc)
        elif m is not None:
            imgset[src_name(img['href'])] = {"date":gallerydate, "views":None, "link":"https://brickshelf.com" + img['href']}
            ret_imgs.append(img['href'])
    return ret_imgs


def soupify_link(link):
    sleeper = 1
    while True:
        try:
            r = requests.get(link, timeout=5)
            if r.status_code != 200:
                print("Error requesting link: ", link)
            else:
                break
        except requests.exceptions.Timeout:
            print("Request timed out. Retrying in ", sleeper, "s")
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error")
            print(errh.args[0])
        except requests.exceptions.ConnectionError as conerr:
            print("Connection error: ", conerr)
        time.sleep(sleeper)
        sleeper += 1

    return BeautifulSoup(r.text, "html.parser")


def get_folders(soup: BeautifulSoup):
    folders = []
    for a in soup.find_all('a'):
        link = a["href"]
        if "/cgi-bin/gallery.cgi?f=" in link and a.string != 'UP':
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
        imgset.clear()
        if link not in discovered:
            print("new link being scraped: ", link)
            discovered[link] = 1
            soup = soupify_link(link)
            # print("calling find_relev_images...")
            images = find_relev_images(soup)
            # print("image src urls: ", images)
            desc_list = soup.find_all(attrs={"name": "description"})

            if len(desc_list) > 0 and len(images) > 0:
                #write_desc(desc_list[0]["content"], images[0], soup)
                write_info(desc_list[0]["content"], images[0], soup, link)

            for image in images:
                # print("attempt writing image: ", image)
                write_image(image)

            folders = get_folders(soup)
            for folder in folders:
                skip = False
                for link in soup.find_all('a'):
                    if "Up" in link: 
                        skip = True 
                        
                if skip == False or DontCheckFoldersAboveGallery == False:
                    s.append(folder)


if __name__ == "__main__":
    main()
