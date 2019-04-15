#coding:UTF-8
import os
import xml.etree.ElementTree
import configparser

class AresCheck:
    def __init__(self):
        self.ConfigFile = configparser.ConfigParser()
        self.ConfigFile.read(r'config\ARESCheckConfig.ini')

    def DealFile(self, file):
        print(file)

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
