# How to: generate documentation for projects using sphinx

## prerequisites

```
pip3 install -U sphinx sphinx_rtd_theme sphinx-tabs
sphinx-build --version
pip3 install --upgrade recommonmark
```

## Generate HEROES main documentation

`sphinx-build -b html ./HEROES/ build`

You can then access the documentation html index/entry point in `build/index.html`.

## Generate HEROES Development documentation

`sphinx-build -b html ./dev/ build-dev`

You can then access the documentation html index/entry point in `build-dev/index.html`.

## Using a different logo

Example:

`sphinx-build -b html ./HEROES ./build -D html_logo='./HEROES/media/image1.png'`

Note that the image file path can be absolute or relative to the `./conf.py` file.
