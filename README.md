astrology app with 4 panes

made using gtk4 & python

uses swisseph via pyswisseph lib

![current development stage](https://github.com/aum7/astrogt/blob/master/ui/imgs/astrogt250821.png)

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License - see the [LICENSE.md](LICENSE.md) file for details.

You are free to:

    Share — copy and redistribute the material in any medium or format
    Adapt — remix, transform, and build upon the material

Under the following terms:

    Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
    NonCommercial — You may not use the material for commercial purposes.

[![License: CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc/4.0/)

installation

linux (ubuntu / mint)

- install virtual environment, ie

`$ python3 -m venv <your_dev_folder>`

- clone `astrogt` repository inside <your_dev_folder>

`$ git clone https://github.com/aum7/astrogt.git`

- next install dependencies, as listed in `requirements.txt`

- open a terminal, activate & enter your virtual environment
- run 

`$ sudo apt install libgirepository-2.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0`

to install the build dependencies and gtk
- run 

`$ pip3 install pycairo`

to build and install pycairo
- run 

`$ pip3 install pygobject`

to build and install pygobject

- download `ephe` folder, from

https://github.com/aloistr/swisseph

and put it into astrogt/sweph/ folder

users of swiss ephemeris are bound to swisseph license

- change the working directory to astrogt, where `main.py` script is
- run

`$ python3 main.py`

windows

follow instructions on :
https://pygobject.gnome.org/getting_started.html

macos

also follow instruction on :
https://pygobject.gnome.org/getting_started.html

note : app was developed on linux mint os, for any other os, if you run into installation troubles, you are on your own (hint : use chatgpt to help you with installation)

on app start, press [h] for quick manual, including hotkeys

hover mouse over input fields / buttons / text for tooltips
