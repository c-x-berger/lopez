Installation
---
This document aims to be a step-by-step guide to installing Lopez.  
It ~~probably~~ fails in this.

## For all purposes
1. Install and configure `postgresql`
    1. You must have at least one database with at least one user who can create and modify tables. Make sure it matches up with the details in `config.py`
2. Install Lopez's Python module requirements with `pip install -r requirements.txt`
3. Run `setup.py` to set up Postgres tables
4. Create `creds.txt`. It should contain only the Discord bot token you want to use to log in on a single line.

Now that you've done basic setup, you need to decide if you want to develop or run Lopez.
Remember: running your own instance of Lopez is discouraged, and a [public instance is available.](https://discordapp.com/oauth2/authorize?client_id=436251140376494080&scope=bot&permissions=335899840)

## Developing
1. `git checkout develop`
2. Install `pre-commit`. You can do this with a simple `pip install -r requirements-dev.txt`
    1. Install the `black` commit hook with `pre-commit install`. This insures all committed code conforms to the same highly opinionated style spec.
3. Write code. Send it back as a pull request. Get a sense of pride and accomplishment.
4. Be sure to check [the most recent revision of this file](https://github.com/BHSSFRC/lopez/blob/develop/INSTALL.md) in the unlikely event that the requirements change. 

## Running
[Last chance to use the stable, well serviced public instance instead!](https://discordapp.com/oauth2/authorize?client_id=436251140376494080&scope=bot&permissions=335899840)

1. Set up systemd unit (technically optional)
   1. See [the DO tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units) for now. You will likely need to create a launcher script to `cd` into your copy of Lopez to properly load `footers.json` and other files.
