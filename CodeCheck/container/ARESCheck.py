#coding:UTF-8
import re
import os
import xml.etree.ElementTree
import configparser
import public.glbfunc

class AresCheckSource:
    def __init__(self):
        self.ConfigFile = configparser.ConfigParser()
        self.ConfigFile.read(r'config\ARESCheckConfig.ini')
        self.StandardFieldList = {}
        self.DataTypeList = {}
        self.UFTBusinessList = {}
        self.DataMgrList = {}

    def InitializeSource(self):
        self.GetStandardFieldList()

        self.GetDataTypeList()

        self.GetModuleList(self.ConfigFile.get('Common', 'ProjectPath'))

    # 'en_branch_no':['HsChar4000', '允许营业部']
    def GetStandardFieldList(self):
        RootField = xml.etree.ElementTree.parse(self.ConfigFile.get('Common', 'ProjectPath') + '\\metadata\\stdfield.stdfield').getroot()

        for stdfield in RootField.findall('items'):
            self.StandardFieldList[stdfield.get('name').strip(' ')] = [stdfield.get('dataType'),
                                                                       stdfield.get('chineseName').strip(' ')]

    # 'HsType':'char(1)'
    def GetDataTypeList(self):
        RootDataType = xml.etree.ElementTree.parse(self.ConfigFile.get('Common', 'ProjectPath') + '\\metadata\\datatype.datatype').getroot()

        for DataType in RootDataType.findall('items'):
            self.DataTypeList[DataType.get('name')] = [DataType.get('stdType'),
                                                       DataType.get('length'),
                                                       DataType.get('precision')]

    # 'libs_settuft_refacctpub.so':['账户公用', ['LS_账户公用_资产账户信息获取'], 'E:\secu\UFTDB_REF\trunk\Sources\DevCodes\分布式清算_REF\uftbusiness\refacct\refacctpub']
    # 'libs_settuft_refarg_datamgr.so':['参数', ['refarg.uftstructure', 'refbusiarg.uftstructure'], 'E:\secu\UFTDB_REF\trunk\Sources\DevCodes\分布式清算_REF\uftstructure\refarg']
    def GetModuleList(self, filePath):
        if filePath[-1] != '\\':
            filePath += '\\'

        for file in os.listdir(filePath):
            fileFullPath = filePath + file
            if fileFullPath.find('\\uftbusiness') >= 0 or fileFullPath.find('\\uftstructure') >= 0:
                if os.path.isdir(fileFullPath):
                    # 如果是目录,目录不能是不用编译、作废、演示等(从module.xml中取cname)
                    if os.path.exists(fileFullPath + '\\' + r'module.xml'):
                        Root = xml.etree.ElementTree.parse(fileFullPath + '\\' + r'module.xml').getroot()

                        cname = Root.find('info').get('cname')

                        if cname.find('作废') < 0 and cname.find('演示') < 0:
                            self.GetModuleList(fileFullPath)
                    else:
                        self.GetModuleList(fileFullPath)
                elif fileFullPath.find('\\uftstructure') >= 0 and file == 'module.xml':
                    tableList = []
                    for f in os.listdir(filePath):
                        if os.path.splitext(f)[1] == '.uftstructure':
                            tableList.append(f)

                    if len(tableList) > 0:
                        so = filePath.rstrip('\\').split('\\')[-1]

                        Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

                        cname = Root.find('info').get('cname')

                        self.DataMgrList['libs_settuft_' + so + '_datamgr.so'] = [cname, tableList, filePath]

                elif fileFullPath.find('\\uftbusiness') >= 0 and file == 'module.xml':
                    functionList = []
                    for f in os.listdir(filePath):
                        if os.path.splitext(f)[1] in ['.uftservice', '.uftfunction']:
                            functionList.append(f)

                    if len(functionList) > 0:
                        so = filePath.rstrip('/').split('/')[-1]

                        Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

                        cname = Root.find('info').get('cname')

                        self.UFTBusinessList['libs_settuft_' + so + '.so'] = [cname, functionList ,filePath]

def DoAresCheck():
    aresCheckSource = AresCheckSource()
    aresCheckSource.InitializeSource()

    ########################检查是否有用hs_strcpy的地方########################
    for uftBusiness in aresCheckSource.UFTBusinessList:
        for function in aresCheckSource.UFTBusinessList[uftBusiness][1]:
            fileName = aresCheckSource.UFTBusinessList[uftBusiness][2] + function

            Root = xml.etree.ElementTree.parse(fileName).getroot()

            codeNode = Root.find('code')
            if codeNode != None:
                code = codeNode.text

                if code != None and code != '':
                    code = public.glbfunc.RemoveNote(code).replace('&#xD;', '')
                    lines = code.split('\n')

                    ptn = re.compile(r'(hs_strcpy\s*\(.*?\)\s*;)')
                    i = 0
                    for line in lines:
                        i += 1
                        vars = re.findall(ptn, line)
                        if vars:
                            for var in vars:
                                if var[0].strip(' ') != var[1].strip(' ') or var[2].replace(' ', '') != '-1':
                                    print('[hs_strcpy]校验失败:请改用hs_strncpy,文件<{0}>,行号<{1}>,内容<{2}>'.format('\\'.join(fileName.split('\\')[-2:]), i, var))

    ########################检查hs_strncpy########################
    for uftBusiness in aresCheckSource.UFTBusinessList:
        for function in aresCheckSource.UFTBusinessList[uftBusiness][1]:
            fileName = aresCheckSource.UFTBusinessList[uftBusiness][2] + function

            Root = xml.etree.ElementTree.parse(fileName).getroot()

            codeNode = Root.find('code')
            if codeNode != None:
                code = codeNode.text

                if code != None and code != '':
                    code = public.glbfunc.RemoveNote(code).replace('&#xD;','')
                    lines = code.split('\n')

                    ptn = re.compile(r'hs_strncpy\s*\(@(.*?),.*?,\s*sizeof\s*\(\s*@(.*?)\)(\s*-*\s*1*)\s*\)\s*;')
                    i = 0
                    for line in lines:
                        i += 1
                        vars = re.findall(ptn, line)
                        if vars:
                            for var in vars:
                                if var[0].strip(' ') != var[1].strip(' ') or var[2].replace(' ', '') != '-1':
                                    print('[hs_strncpy]校验失败:未使用字段本身长度减1,文件<{0}>,行号<{1}>,内容<{2}>'.format('\\'.join(fileName.split('\\')[-2:]), i, var))

    ########################检查hs_snprintf########################
    for uftBusiness in aresCheckSource.UFTBusinessList:
        for function in aresCheckSource.UFTBusinessList[uftBusiness][1]:
            fileName = aresCheckSource.UFTBusinessList[uftBusiness][2] + function

            Root = xml.etree.ElementTree.parse(fileName).getroot()

            codeNode = Root.find('code')
            if codeNode != None:
                code = codeNode.text

                if code != None and code != '':
                    code = public.glbfunc.RemoveNote(code).replace('&#xD;','')
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
                                    print('[hs_snprintf]校验失败:未使用字段本身长度,文件<{0}>,行号<{1}>,内容<{2}>'.format('\\'.join(fileName.split('\\')[-2:]), i, var))

    ########################检查hs_strcmp########################
    for uftBusiness in aresCheckSource.UFTBusinessList:
        for function in aresCheckSource.UFTBusinessList[uftBusiness][1]:
            fileName = aresCheckSource.UFTBusinessList[uftBusiness][2] + function

            Root = xml.etree.ElementTree.parse(fileName).getroot()

            codeNode = Root.find('code')
            if codeNode != None:
                code = codeNode.text

                if code != None and code != '':
                    code = public.glbfunc.RemoveNote(code).replace('&#xD;', '')
                    lines = code.split('\n')

                    ptn = re.compile(r'(\d+\s*[!=]=\s*)?hs_strcmp\s*\(.*?,.*?\)(\s*[!=]=\s*\d+)?')
                    i = 0
                    for line in lines:
                        i += 1
                        vars = re.findall(ptn, line)
                        if vars:
                            for var in vars:
                                #print(fileName, i, var)
                                if var[0].replace(' ', '') not in ['0==', '0!='] and var[1].replace(' ', '') not in ['==0', '!=0']:
                                    print('[hs_strcmp]校验失败:少了==或者!=,文件<{0}>,行号<{1}>,内容<{2}>'.format('\\'.join(fileName.split('\\')[-2:]), i, var))

    ########################检查UFT对象长度大于120的字段########################
    for dataMgr in aresCheckSource.DataMgrList:
        #print(dataMgr, aresCheckSource.DataMgrList[dataMgr])
        path = aresCheckSource.DataMgrList[dataMgr][2]
        for uftStructure in aresCheckSource.DataMgrList[dataMgr][1]:
            #print(path + uftStructure)
            RootUftStructure = xml.etree.ElementTree.parse(path + uftStructure).getroot()

            for Properties in RootUftStructure.findall('properties'):
                stdField = Properties.get('id')

                dataType = aresCheckSource.StandardFieldList[stdField.strip(' ')][0]

                RealType = aresCheckSource.DataTypeList[dataType]

                if RealType[0] == 'String' and int(RealType[1]) >= 120:
                    print(path + uftStructure, stdField, RealType[1])