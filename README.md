# cronos

Export your McGill Calendar in 60 seconds.

## Quickstart

Run the following commands to bootstrap the environment:
```bash
git clone ...
cd cronos
python3 -m venv env
env/bin/pip install -r requirements.txt
chmod +x manage.py
```

Next, to run the server:
```bash
./manage.py server
```

## Shell

To open the interactive shell, run:
```bash
./manage.py shell
```

## Tests

To run tests, run:
```bash
./manage.py test
```
Note that this requires that the `MINERVA_USER` 
and `MINERVA_SECRET` environment variables be set.

## Compatibility
Only Python 3.4 is officially supported. 

## Authors
`cronos` was written by `Selim Belhaouane <selim.belhaouane@gmail.com>`_.
