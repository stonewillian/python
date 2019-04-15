#coding:UTF-8
import re
import os
import xml.etree.ElementTree
import configparser
from public import glbfunc

def CheckStrNCpy(code):
    lines = code.split('\n')

    ptn = re.compile(r'hs_strncpy\s*\(@(.*?),.*?,\s*sizeof\s*\(\s*@(.*?)\)(\s*-*\s*1*)\s*\)\s*;')
    i = 0
    for line in lines:
        i += 1
        vars = re.findall(ptn, line)
        if vars:
            for var in vars:
                if var[0].strip(' ') != var[1].strip(' ') or var[2].replace(' ', '') != '-1':
                    print('hs_strncpy', i, var)

def CheckSnPrintf(code):
    lines = code.split('\n')

    ptn = re.compile(r'hs_snprintf\s*\(@(.*?),\s*sizeof\s*\(\s*@(.*?)\)(\s*-*\s*1*)\s*,.*?\)\s*;')
    i = 0
    for line in lines:
        i += 1
        vars = re.findall(ptn, line)
        if vars:
            for var in vars:
                # print(path + file, i, var)
                if var[0].strip(' ') != var[1].strip(' ') or var[2].replace(' ', '') != '':
                    print('hs_snprintf', i, var)

class AresCheck:
    def __init__(self):
        self.ConfigFile = configparser.ConfigParser()
        self.ConfigFile.read(r'config\ARESCheckConfig.ini')

    def DealFile(self, file):
        Root = xml.etree.ElementTree.parse(file).getroot()

        codeNode = Root.find('code')
        if codeNode != None:
            code = codeNode.text
            if code != None and code != '':
                code = glbfunc.RemoveNote(code).replace('&#xD;', '').replace('&gt;', '>').replace('&lt;', '<')
                CheckStrNCpy(code)
                CheckSnPrintf(code)

    def DealPath(self,filePath):
        if filePath == '':
            filePath = self.ConfigFile.get('Common', 'ProjectPath')

        if filePath[-1] != '\\':
            filePath += '\\'

        for file in os.listdir(filePath):
            if (filePath + file).find('\\uftbusiness') >= 0 or (filePath + file).find('\\uftstructure') >= 0:
                if os.path.isdir(filePath + file):
                    # 如果是目录,目录不能是不用编译、作废、演示等(从module.xml中取cname)
                    if os.path.exists(filePath + file + '\\' + r'module.xml'):
                        Root = xml.etree.ElementTree.parse(filePath + file + '\\' + r'module.xml').getroot()

                        cname = Root.find('info').get('cname')

                        if cname.find('作废') < 0 and cname.find('不用编译') < 0 and cname.find('演示') < 0:
                            self.DealPath(filePath + file)
                    else:
                        self.DealPath(filePath + file)
                else:
                    self.DealFile(filePath + file)
