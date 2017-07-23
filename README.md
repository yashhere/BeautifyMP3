<p align="left">
    <a href="https://github.com/yash2696/BeautifyMP3/LICENSE">
		<img alt="License"  src="https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square"/>
	</a>           
</p>

## Table of Contents

- [Features](#features)
- [Dependencies](#dependencies)
- [Installing](#installing)
  - [Source](#source)
- [Usage](#usage)
  - [Options](#options)
- [Contribute](#contribute)
- [License](#license)


## Features

1. Fixes metadata of songs based on data received from Spotify
2. Fetches lyrics from [Genius](https://www.genius.com)
3. Fetches metadata from [Spotify](https://www.spotify.com)
4. Can format filenames of songs
5. Can fetch data for a single song or complete directory

## Dependencies  

### [Genius API](https://genius.com/api-clients) 

1. Create an account and register an application 
2. Grab Access Token
3. Set access token in config file


### [Spotify API](https://developer.spotify.com/my-applications/#!/applications/create) 

1. Create an account and register an application 
2. Grab Client ID and client Secret Code
3. Set both in config file

```sh 
$ python addMetadata.py --config                                               

Enter Genius key : <enter genius key> 

Enter Spotify Secret token : <enter client secret here> 

Enter Spotify Client ID : <enter client id here>                               
```

## Installing

### Source
```sh
$ git clone https://github.com/yash2696/BeautifyMP3
$ cd BeautifyMP3
$ python setup.py install
```

### Options
```sh
(music-tagger) ~/D/music-tagger ❯❯❯ python addMetadata.py -h
usage: addMetadata.py [-h] [-d REPAIR_DIRECTORY] [-s SONG_NAME] [-c] [-n]
                      [-f RENAME_FORMAT]

 ____                   _   _  __       __  __ ____ _____ 
| __ )  ___  __ _ _   _| |_(_)/ _|_   _|  \/  |  _ \___ / 
|  _ \ / _ \/ _` | | | | __| | |_| | | | |\/| | |_) ||_ \ 
| |_) |  __/ (_| | |_| | |_| |  _| |_| | |  | |  __/___) |
|____/ \___|\__,_|\__,_|\__|_|_|  \__, |_|  |_|_|  |____/ 
                                  |___/                   
                                  
______________________________________________________________
|                                                            |
|       Edit Metadata of MP3 files based on file name        |
|____________________________________________________________|

optional arguments:
  -h, --help            show this help message and exit
  -d REPAIR_DIRECTORY, --dir REPAIR_DIRECTORY
                        give path of music files&#96; directory
  -s SONG_NAME, --song SONG_NAME
                        Only fix metadata of the file specified
  -c, --config          Add API Keys to config
  -n, --norename        Does not rename files to song title
  -f RENAME_FORMAT, --format RENAME_FORMAT
                        Specify the Name format used in renaming, Valid
                        Keywords are: {title}{artist}{album} )
```

## TODO
- [ ] Add download functionality from youtube
- [ ] add support for last.fm and soundcloud if spotify fails
- [ ] add support for metrolyrics and other lyrics service if genius api fails
- [ ] add support for searching with existing id3 tags if searching with name fails
- [ ] somehow find a way to properly synchronize the lyrics with sound if possible
- [ ] add support for other file types(aac, flac etc)

## Contribute

Found an issue? Post it in the [issue tracker](https://github.com/yash2696/BeautifyMP3/issues). <br> 
Want to add another awesome feature? [Fork](https://github.com/yash2696/BeautifyMP3/fork) this repository and add your feature, then send a pull request.

## Disclaimer

The inspiration for this project is [MusicRepair](https://github.com/kalbhor/MusicRepair). 

Downloading copyright songs is illegal in most of the countries. I made this tool for educational purposes and was created for my python learning process. Please support the artists by buying their music.

## License
The MIT License (MIT)
Copyright (c) 2017 Yash Agarwal
