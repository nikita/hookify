#!/usr/bin/env python

import sys

UNKNOWN_TYPE = "CDUnknownBlockType"


def map_format_specifier(_type):
    if _type == "int":
        return "%d"
    if _type in ["BOOL", "_Bool", "bool"]:
        return "%u"
    if _type == "long long":
        return "%lld"
    if _type == "float":
        return "%f"
    if _type == "unsigned long long":
        return "%llu"
    if _type == "double":
        return "%f"
    else:
        return "%@"


class ObjcMethod():
    def __init__(self, line, interface):
        self.line = line.replace(UNKNOWN_TYPE, 'id')
        self.ret_type = self.get_ret_type()
        self.interface = interface
        self.name = self.get_name()
        self.full_name = "[%s %s]" % (interface, self.name)

    def get_name(self):
        splits = self.line.split(')')
        splits = splits[1].split(':')
        splits = splits[0].split(';')
        name = splits[0]
        return name

    def get_ret_type(self):
        splits = self.line[3:].split(')', 1)
        ret_type = splits[0]
        if ret_type is not UNKNOWN_TYPE:
            return ret_type
        return "id"

    def hook(self):
        if self.ret_type == "void":
            print('%s {[LogTool logDataFromNSString:@">>>> - %s"];%%log; %%orig;[LogTool logDataFromNSString:@"<<<< - %s"]; }' %
                  (self.line[:-2], self.full_name, self.full_name))
        else:
            print('%s {[LogTool logDataFromNSString:@">>>> - %s"];%%log; %s ret = %%orig;[LogTool logDataFromNSString:[NSString stringWithFormat: @"<<<< - %s ==> ret value: %s", ret]];return ret; }' %
                  (self.line[:-2], self.full_name, self.ret_type, self.full_name, map_format_specifier(self.ret_type)))


class HeaderParser():
    def __init__(self, filepath):
        self.file = open(filepath)
        self.lines = self.file.readlines()
        self.interface = self.get_interface_name()
        self.methods = self.get_methods()

    def get_interface_name(self):
        for line in self.lines:
            if "@interface" in line:
                splits = line.split(' ')
                return splits[1]

    def get_methods(self):
        methods = []
        for line in self.lines:
            if line[:3] == "- (" or line[:3] == "+ (":
                method = ObjcMethod(line, self.interface)
                methods.append(method)
        return methods


def main(args):
    filepath = args[1]
    parser = HeaderParser(filepath)
    print("%hook", parser.interface)
    for method in parser.methods:
        if method.name not in ".cxx_destruct":
            method.hook()
    print("%end")


main(sys.argv)
