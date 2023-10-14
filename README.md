# Experiment showing how to create a micropython MIP index

## Current limitation

* Only the latest version of main will be deployed!
* No version numbers will be provided
* Old file are not deleted

## Interesting links

 * https://docs.micropython.org/en/latest/reference/packages.html
 * https://github.com/miguelgrinberg/microdot/issues/67
 * https://github.com/markafarrell/microdot/blob/feature/publish-mpy/.github/workflows/publish.yml -> Pushes to https://github.com/miguelgrinberg/microdot/actions
  * https://github.com/micropython/micropython-lib/blob/master/tools/build.py


## Big picture - MIP download

This repo demonstrates how a application may be installed using MIP:

```python
import mip
mip.install("dryer2023", version="main", index="https://hmaerki.github.io/experiment_micropython_mip/mip_index")
```

The download will be controlled by a 'package.json':
```json
{
  "deps": [
    [
      "https://micropython.org/pi/v2/package/6/umqtt.simple/latest.json",
      "dummy"
    ]
  ],
  "hashes": [
    [
      "dryer2023/statemachine.mpy",
      "a47f24f2064b"
    ],
    [
      "dryer2023/__init__.mpy",
      "c4104085da6d"
    ]
  ],
  "version": "0.1"
}
```

Above command will:
 * Download a `package.json`
 * Download the myp-files
 * Download the dependency `umqtt.simple`


## Big picture - Github python index

Commiting to main will

* Start github action `.github/workflows/static.yml`
  * Call `tools/create_mip.py`
    * Call `mpy_cross` for all python files: .py -> .mpy
    * Create the MIP-directory structure under `docs/`
    * Push to the static web page `https://hmaerki.github.io/experiment_micropython_mip`
