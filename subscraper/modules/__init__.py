import sys
import importlib
from taser import logx
from os import listdir, path


class ModuleLoader():
    module_path = path.join(path.dirname(__file__))

    @classmethod
    def get_moduleClass(cls, module, args, target, report_handler, config):
        p_path = '.'.join(['subscraper', 'modules', module])
        return importlib.import_module(p_path).SubModule(args, target, report_handler, config)

    @classmethod
    def list_modules(cls, args):
        print(logx.highlight("\n{:20}   {}\n".format('Module Name', 'Description'), fg='gray', windows=args.no_color))
        for module in listdir(cls.module_path):
            if module[-3:] == '.py' and module[:-3] != '__init__':
                m = cls.get_moduleClass(module[:-3], False, False, False, False)
                api_req = logx.highlight("(API Key Req)", fg='red', windows=args.no_color) if m.api_key else ''
                print("{:20} - {} {}".format(m.name, m.description,  api_req))
        print('\n')
        sys.exit(0)
