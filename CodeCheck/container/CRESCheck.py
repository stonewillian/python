#coding:UTF-8
import re
import os
import xml.etree.ElementTree
import configparser
import public.glbfunc

# 初始化资源(比如标准字段/数据字典/模块属性等)
class CresCheckSource:
    def __init__(self):
        self.ConfigFile = configparser.ConfigParser()
        self.ConfigFile.read(r'config\CRESCheckConfig.ini')
        self.StandardFieldList = {}
        self.DataTypeList = {}
        self.ModuleList = {}
        self.FunctionList = {}

    def InitializeSource(self):
        self.GetStandardFieldList(self.ConfigFile.get('Common', 'ProjectPath') + '\\公共资源\\stdfields.xml')

        self.GetDataTypeList(self.ConfigFile.get('Common', 'ProjectPath') + '\\公共资源\\datatypes.xml')

        self.GetModuleList(self.ConfigFile.get('Common', 'ProjectPath'), '', 0)

    # 'en_branch_no':['HsChar4000', '允许营业部']
    def GetStandardFieldList(self, fieldFile):
        RootField = xml.etree.ElementTree.parse(fieldFile).getroot()

        for stdfield in RootField.findall('stdfield'):
            self.StandardFieldList[stdfield.get('name').strip(' ')] = [stdfield.get('type'),
                                                                       stdfield.get('cname').strip(' ')]

    # 'HsType':'char(1)'
    def GetDataTypeList(self, dataTypeFile):
        RootDataType = xml.etree.ElementTree.parse(dataTypeFile).getroot()

        for DataType in RootDataType.findall('userType'):
            self.DataTypeList[DataType.get('name')] = DataType.find('database').find('map').get('value')

    # 'libs_as_refsettplusflow.10.so':['AS', 19, 'REFDB', 'E:\secu\UFTDB_REF\trunk\Sources\DevCodes\分布式清算_参数_REF\原子\转融通日终']
    # 'LS_转融通日终_初始化业务处理':[940350, 'LS_REFSETT_INITBUSIN_DEAL', ['LF_转融通日终_初始化日期获取'], 'E:\secu\UFTDB_REF\trunk\Sources\DevCodes\分布式清算_参数_REF\业务逻辑\转融通日终\服务\LS_转融通日终_初始化业务处理.service_design']
    def GetModuleList(self, path, db, subsysid):
        if path[-1] != '\\':
            path += '\\'

        for file in os.listdir(path):
            fileFullPath = path + file
            #if fileFullPath.find('作废') >= 0 or fileFullPath.find('不用编译') >= 0 or fileFullPath.find('演示') >= 0:
            if fileFullPath.find('作废') >= 0 or fileFullPath.find('演示') >= 0:
                continue

            if fileFullPath.find('\\业务逻辑') < 0 and fileFullPath.find('\\原子') < 0 and fileFullPath.find('\\数据库') < 0:
                continue

            if os.path.isdir(fileFullPath):
                if os.path.exists(fileFullPath + '\\module.xml'):
                    Root = xml.etree.ElementTree.parse(fileFullPath + '\\module.xml')
                    DataBase = Root.find('info').get('database')
                    SubSystem = Root.find('info').get('sub_system')

                    db = DataBase if DataBase != '' else db
                    subsysid = int(SubSystem) if SubSystem != '' else subsysid

                self.GetModuleList(fileFullPath, db, subsysid)
            elif fileFullPath.find('\\业务逻辑') >= 0 and file == 'module.xml':
                Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

                ModuleName = 'libs_ls_' + Root.find('info').get('ename') + 'flow.10.so'
                Type = 'LS'
                SubSystem = 0 if Root.find('info').get('sub_system') == '' else int(Root.find('info').get('sub_system'))
                DataBase = Root.find('info').get('database')

                self.ModuleList[ModuleName] = [Type, SubSystem, DataBase, path]
            elif fileFullPath.find('\\原子') >= 0 and file == 'module.xml':
                Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

                ModuleName = 'libs_as_' + Root.find('info').get('ename') + 'flow.10.so'
                Type = 'AS'
                SubSystem = 0 if Root.find('info').get('sub_system') == '' else int(Root.find('info').get('sub_system'))
                DataBase = Root.find('info').get('database')

                self.ModuleList[ModuleName] = [Type, SubSystem, DataBase, path]
            elif fileFullPath.find('\\数据库') >= 0 and file == 'module.xml':
                exists = False
                for f in os.listdir(path):
                    if os.path.splitext(file)[1] == '.table_design':
                        exists = True

                if exists:
                    Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

                    ModuleName = path.split('\\')[-2]
                    Type = 'DB'
                    SubSystem = 0 if Root.find('info').get('sub_system') == '' else int(
                        Root.find('info').get('sub_system'))
                    DataBase = Root.find('info').get('database')

                    self.ModuleList[ModuleName] = [Type, SubSystem, DataBase, path]
            elif os.path.splitext(file)[1] in ['.service_design',
                                               '.function_design',
                                               '.aservice_design',
                                               '.afunction_design',
                                               '.procedure_design']:
                Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

                FunctionCName = os.path.splitext(file)[0]
                FunctionID = int(Root.find('basic').find('basic').get('objectId'))
                FunctionEName = Root.find('basic').find('basic').get('englishName')

                FunctionCall = []
                codeNode = Root.find('code')
                if codeNode != None:
                    code = codeNode.text

                    if code != None and code != '':
                        code = public.glbfunc.RemoveNote(code).replace('&gt;', '>').replace('&lt;', '<')

                        # 原子调用
                        patternA = re.compile(r'\[(A.*?)\]', re.S)
                        funcDeals = re.findall(patternA, code)
                        if funcDeals:
                            for funcDeal in funcDeals:
                                if funcDeal not in FunctionCall:
                                    FunctionCall.append(funcDeal)

                        # 逻辑调用
                        patternL = re.compile(r'\[(L.*?)\]', re.S)
                        funcDeals = re.findall(patternL, code)
                        if funcDeals:
                            for funcDeal in funcDeals:
                                # print('\t',funcDeal)
                                if funcDeal not in funcDeals:
                                    funcDeals.append(funcDeal)

                self.FunctionList[FunctionCName] = [FunctionID, FunctionEName, FunctionCall, fileFullPath]

def DoCresCheck():
    #########################初始化资源#########################
    cresCheckSource = CresCheckSource()
    cresCheckSource.InitializeSource()

    #########################检查是否存在跨模块调用#######################
    for func in cresCheckSource.FunctionList:
        moduleName = func.split('_')[1]

        for funcCall in cresCheckSource.FunctionList[func][2]:
            moduleNameCall = funcCall.split('_')[1]

            if cresCheckSource.FunctionList[funcCall][3].find('公用') < 0 and \
                cresCheckSource.FunctionList[funcCall][3].find('外部接口') < 0 and \
                funcCall[0:3] != 'AS_' and \
                moduleName != moduleNameCall:
                print('[{0}]非法调用[{1}]'.format(func, funcCall))

    #########################检查同一模块的AP,是否被调用AP在前面#############################
    for func in cresCheckSource.FunctionList:
        if func[0:3] == 'AP_':
            for funcCall in cresCheckSource.FunctionList[func][2]:
                if funcCall[0:3] == 'AP_':
                    if func.split('_')[1] == funcCall.split('_')[1] and cresCheckSource.FunctionList[func][0] < cresCheckSource.FunctionList[funcCall][0]:
                        print('被依赖AP[{0}]应该在AP[{1}]前面'.format(func, funcCall))
