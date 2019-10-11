class ExampleModule():
    def __init__(self, args, target, handler):
        self.description = "Example module"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.handler     = handler
        self.target      = target

    def execute(self):
        '''
        Add your subdomain enumeration method here.
        Once finished, pass newly found subdomains to the sub_handler
        to tie into SubScraper default output.

        Dont forget to add the filename + classname
        to the dictionary in subscraper.modules MODULES.
        This will ensure the method is called during enumeration.
        '''
        sub = 'Newly Found Subdomain'
        self.handler.sub_handler({'Name': sub, 'Source': 'Example-Module'})