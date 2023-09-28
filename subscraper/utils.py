import os
from sys import exit
from json import load
from taser import logx
from shutil import copyfile


class ConfigParser:
    # Blank config in .git repo
    default_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'config.json')

    # Default config path on disk
    default_path = os.path.join(os.path.expanduser('~'), '.config', 'subscraper', 'config.json')

    def __init__(self, args):
        self.args = args
        self.first_run_check() if not self.args.config else False
        self.config = self.args.config if self.args.config else self.default_path
        self.parse()

    def first_run_check(self):
        os.makedirs(os.path.dirname(self.default_path), exist_ok=True)

        if not os.path.exists(self.default_path) or self.args.update:
            logx.color("[*] Creating new SubScraper config file...", fg='gray', windows=self.args.no_color) if not self.args.silent else False
            copyfile(self.default_config, self.default_path)
            logx.color(f'[*] New config added to {self.default_path}', fg='gray', windows=self.args.no_color) if not self.args.silent else False

    def parse(self):
        try:
            with open(self.config) as f:
                for k, v in load(f).items():
                    setattr(self, k, v)
        except Exception as e:
            logx.color('[!] Error parsing config file: {}'.format(e), fg='yellow', windows=self.args.no_color)
            exit(1)

###########################################
# Misc utils for parsing subdomain strings
###########################################
def remove_wildcard(sub):
    # Remove wildcard from sub string: *.admin.test.com --> admin.test.com
    return sub.split('*.')[1] if sub.startswith('*.') else sub
