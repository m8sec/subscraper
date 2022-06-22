import importlib
from os import listdir, path
from argparse import Namespace
from subscraper.support.cli import highlight

class ModuleLoader():
    module_path = path.join(path.dirname(__file__))

    @classmethod
    def get_moduleClass(cls, module, args, target, report_handler):
        p_path = '.'.join(['subscraper', 'modules', module])
        return importlib.import_module(p_path).SubModule(args, target, report_handler)

    @classmethod
    def list_modules(cls):
        print(highlight("\n  {:15}   {}\n".format('Module Name', 'Description'), 'gray'))
        for module in listdir(cls.module_path):
            if module[-3:] == '.py' and module[:-3] != '__init__':
                mod_class = cls.get_moduleClass(module[:-3], gen_context(), False, False)
                print("  {:20} - {}".format(mod_class.name, mod_class.description))
                for k, v in mod_class.args.items():
                    print('    |_{:24} {:30} (Required:{})'.format(k, v['Description'], v['Required']))

def gen_context():
    # Idle Namespace to list modules
    return Namespace(
        timeout=1,
        wordlist=[],
        censys_id=False,
        censys_secret=False
    )
