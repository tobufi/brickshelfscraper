# brickshelfscraper
python script that downloads all the relevant images on brickshelf galleries

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
