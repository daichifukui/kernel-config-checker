'''
Copyright (C) 2018 Intel Corporation

SPDX-License-Identifier: GPL-3.0

cli for kernel config checker
'''
import re
import sys
import argparse
from typing import Iterator

from .kconfig import Kconfig
from .query import KernelSelfProtectionProject
from .defaults import MUST_BE_SET, MUST_BE_SET_OR_MODULE, MUST_BE_UNSET

def get_expected_opt(opt, msg: str):
    msg = msg.strip()
    match = re.search("is not set but is required to be set to y or m", msg)
    if match:
        return opt + "=Y \n"  
    match = re.search("is not set but is required to be set to y", msg)
    if match:
        return opt + "=Y \n"  
    match = re.search("is set but is required to be not set ", msg)
    if match:
        return "# " + opt + " is not set \n"  
    match = re.search("is set as =m but is required to be set to y", msg)
    if match:
        return opt + "=Y \n"  
    match = re.search("is set as =m but is required to be not set", msg)
    if match:
        return "# " + opt + " is not set \n"  
    match = re.search("is not set but is required to be set to m", msg)
    if match:
        return opt + "=M \n"  
    match = re.search("is set  but is required to be set to m", msg)
    if match:
        return opt + "=M \n"  
    return ""
    

def run(*,
        config_file: str = '',
        query: bool = False,
        expected: bool = False):
    if query:
        must_be_set, must_be_set_or_module, must_be_unset = \
                KernelSelfProtectionProject()
        must_be_set.update(MUST_BE_SET)
        must_be_set_or_module.update(MUST_BE_SET_OR_MODULE)
        must_be_unset.update(MUST_BE_UNSET)
        kconfig = Kconfig(must_be_set=must_be_set,
            must_be_set_or_module=must_be_set_or_module,
            must_be_unset=must_be_unset)
    else:
        kconfig = Kconfig.default()

    results = kconfig.check(config_file)
    if not results:
        return
    if expected:
        f = open('expected_config',mode='w')
    for opt, msg in results.items():
        print(opt, msg)
        if expected: 
            expect = get_expected_opt(opt, msg)
            f.write(expect)
    if expected:
        f.close()
        
    return 1

def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs='?', type=argparse.FileType('r'),
            default=sys.stdin)
    parser.add_argument('--query', default=False, action='store_true')
    parser.add_argument('--expected', default=False, action='store_true')
    args = parser.parse_args()
    ret = run(**vars(args))
    args.config_file.close()
    if isinstance(ret, int):
        sys.exit(ret)
