# brickshelfscraper
python script that downloads all the relevant images on brickshelf galleries

this fork preserves the info from the specified galleries with a json. it also changes the "last modified" date to the actual date from the website. if the image/file is a direct link, then it takes the same date as the folder. this may lead to some inaccurate dates for those images.

there's one changeable variable in the script called "DontCheckFoldersAboveGallery" that is automatically set to true. this prevents your scraper from scraping stuff above the gallery you put in links, which was a problem for me personally for downloading specific stuff. set this to "False" in main.py if you don't care about that.

special thanks to novelqq for the original :-)

!! code here may be ugly !!

## Dependencies
Requires Beautiful Soup 4 and requests
```
python -m pip install requests
python -m pip install bs4
```

## Instructions
Place each brickshelf gallery URL on a new line in links.txt
Run `python main.py` 
The script will scan all subdirectories and download all the images in a folder called gallery and create sub-directories as necessary. It preserves the folder structure on the website.
