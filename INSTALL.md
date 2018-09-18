Installation
---
This document aims to be a step-by-step guide to installing Lopez.  
It probably fails in this.

1. Install and configure `postgresql`
  1. You must have at least one database with at least one user who can create and modify tables. Make sure it matches up with the details in `config.py`
2. Install Lopez's Python module requirements
  1. `discord.py`: `pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py` (Lopez does not require voice.)
  2. `asyncpg`: `pip install -U asyncpg`
2. Run `setup.py`
3. Set up systemd unit (technically optional)
  1. See [the DO tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units) for now. You will likely need to create a launcher script to `cd` into your copy of Lopez to properly load `footers.json` and other files.