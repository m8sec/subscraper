import argparse
from os import path
from sys import argv

from taser import logx
from taser.utils import delimiter2list, file_exists

def banner(args):
    version = '4.0.1'
    banner = """                 
     ___      _    ___                            
    / __|_  _| |__/ __| __ _ _ __ _ _ __  ___ _ _ 
    \__ \ || | '_ \__ \/ _| '_/ _` | '_ \/ -_) '_|
    |___/\_,_|_.__/___/\__|_| \__,_| .__/\___|_| v{}
                                   |_|           @m8sec
    """.format(version)
    logx.color(banner, fg='gray', windows=args.no_color)


def cmd_parser():
    args = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    opt = args.add_argument_group("SubScraper Options")
    opt.add_argument('-debug',action='store_true', help='Enable debug logging')
    opt.add_argument('-update', action='store_true', help='Update config file (Will remove existing entries)')
    opt.add_argument('-config', type=str, default=False, help="Override default config location")
    opt.add_argument('-silent', action='store_true', help='Show subdomains only in output')
    opt.add_argument('-threads', '-T', type=int, default=65, help='Max threads for enumeration (65*).')
    opt.add_argument('-t', dest='timeout', type=int, default=3, help='set connection timeouts (3*)' )
    opt.add_argument('-d', "--domain", default=[], help="Target domain input (domain, .txt, STDIN, etc.")

    mod = args.add_argument_group("Module Options")
    mod.add_argument('-ls', dest="list_modules", action='store_true', help='List SubScraper enumeration modules.' )
    mod.add_argument('-m', dest="modules", type=str, default='*', help="Execute module(s) by name or group (all*)." )
    mod.add_argument('-module-only', action='store_true', help='Execute modules only not brute force' )

    brute = args.add_argument_group("Bruteforce Options")
    brute.add_argument('-w', dest='wordlist', default=path.join(path.dirname(path.realpath(__file__)), 'data', 'subdomains.txt'), type=lambda x: file_exists(args, x, False), help='Custom wordlist for DNS brute force.')
    brute.add_argument('-ns',default=[], type=lambda x: delimiter2list(x), help="Comma separated nameservers to use")

    enum = args.add_argument_group("Enumeration Options")
    enum.add_argument('-r', '-resolve', dest='resolve', action='store_true', help='Resolve DNS names.')
    enum.add_argument('-c', '-cname', dest='cname', action='store_true', help='CNAME lookup for subdomain takeover')
    enum.add_argument('-http', action='store_true', help='Probe for active HTTP services.')
    enum.add_argument('-http-port', default='80,443', type=lambda x: delimiter2list(x), help='HTTP ports to check, comma separated (80,443*)')

    out = args.add_argument_group("Output Options")
    out.add_argument('-nc', '-no-color', dest='no_color', action='store_true', help='Disable color output')
    out.add_argument('-active', action='store_true',help='Only report active subdomains with resolved IP')
    out.add_argument('-csv', action='store_true', help='Create CSV output report')
    out.add_argument('-o', dest='report', type=str, default='./sub_report.txt', help="Output file")

    if len(argv) < 2: args.print_help(); exit(0)
    return args.parse_args()