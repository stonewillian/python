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

def CheckCIFExpression(file, IFExpression):
    #print('\t' + IFExpression)
    ptn = re.compile('([^\=\!\<\>]=[^=])', re.S)
    vars = re.findall(ptn, IFExpression)
    if vars:
        print(file, IFExpression)

    ptn = re.compile('(<>)', re.S)
    vars = re.findall(ptn, IFExpression)
    if vars:
        print(file, IFExpression)

def CheckC(file, code):
    #print(file)
    pIndex = 0
    while pIndex < len(code):
        pIndex = code.find('if', pIndex)
        if pIndex < 0:
            pIndex = len(code)
        else:
            #确认是if关键字,而不是diff这类代码
            if pIndex > 0 and code[pIndex - 1] not in [' ', '\t', '\n']:
                #print(code[pIndex - 1], pIndex, code)
                pIndex += len('if')
            elif pIndex + len('if') < len(code) - 1 and code[pIndex + len('if')] not in [' ', '\t', '\n', '(']:
                #print(code[pIndex + 1], pIndex, code)
                pIndex += len('if')
            else:
                #print(pIndex, code)
                pIndex += len('if')
                while code[pIndex] in [' ', '\n', '\t']:
                    pIndex += 1

                if code[pIndex] != '(':
                    print('\t无法从if后获取"("信息,请确认语法是否正确', code[pIndex:])
                else:
                    IFExpression = ''

                    IFExpression += code[pIndex]
                    pIndex += 1
                    dept = 1
                    while dept > 0:
                        if code[pIndex] == '(':
                            dept += 1
                        elif code[pIndex] == ')':
                            dept -= 1

                        IFExpression += code[pIndex]
                        pIndex += 1

                    CheckCIFExpression(file, IFExpression)

def CheckPROCIFExpression(file, IFExpression):
    #print('\t' + IFExpression)
    ptn = re.compile('([=!]=)', re.S)
    vars = re.findall(ptn, IFExpression)
    if vars:
        print(file, IFExpression)

def CheckPROC(file, code):
    #print(file, 'PRO*C', code)
    pIndex = 0
    while pIndex < len(code):
        pIndex = code.find('if', pIndex)
        if pIndex < 0:
            pIndex = len(code)
        else:
            #是否需要跳过这个if, 需要考虑到if/elsif/end if多种情况
            Escape = False

            indEnd = pIndex - 1
            while code[indEnd] in [' ', '\n', '\t']:
                indEnd -= 1

            indCommon = pIndex + len('if')
            while code[indEnd] in [' ', '\n', '\t']:
                indCommon += 1

            if code[indEnd - 2 : indEnd + 1] == 'end' and code[indCommon] == ';':
                #说明是'end if;'
                Escape = True
            elif code[pIndex - 3 : pIndex + 2] == 'elsif':
                #说明是elsif
                Escape = False
            elif pIndex > 0 and code[pIndex - 1] not in [' ', '\n', '\t']:
                #说明是hs_datediff这类代码
                Escape = True
            elif pIndex + len('if') < len(code) - 1 and code[pIndex + len('if')] not in ['(', ' ', '\n', '\t']:
                # 说明是hs_datediff这类代码
                Escape = True

            if Escape:
                pIndex += len('if')
            else:
                thenIndex = code.find('then', pIndex)
                if thenIndex < 0:
                    print('\t无法从if后获取"then"信息,请确认语法是否正确', code[pIndex:])
                else:
                    CheckPROCIFExpression(file, code[pIndex + len('if') : thenIndex])
                    pIndex = thenIndex

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
                print('[模块调用校验失败]:<{0}>不允许调用<{1}>'.format(func, funcCall))

    #########################检查同一模块的AP,是否被调用AP在前面#############################
    for func in cresCheckSource.FunctionList:
        if func[0:3] == 'AP_':
            for funcCall in cresCheckSource.FunctionList[func][2]:
                if funcCall[0:3] == 'AP_':
                    if func.split('_')[1] == funcCall.split('_')[1] and cresCheckSource.FunctionList[func][0] < cresCheckSource.FunctionList[funcCall][0]:
                        print('[AP依赖校验失败]:被依赖AP<{0}>应该在AP<{1}>前面'.format(func, funcCall))

    ########################检查是否存在if里面应该用==但是用了=的情况
    for func in cresCheckSource.FunctionList:
        #print(cresCheckSource.FunctionList[func][3])
        fileFullPath = cresCheckSource.FunctionList[func][3]
        Root = xml.etree.ElementTree.parse(fileFullPath).getroot()

        codeNode = Root.find('code')

        if codeNode != None:
            code = codeNode.text

            if code != None and code != '':
                code = public.glbfunc.RemoveNote(code).replace('&gt;', '>').replace('&lt;', '<')

                if os.path.splitext(cresCheckSource.FunctionList[func][3].split('\\')[-1])[1] in ['.service_design', '.function_design']:
                    CheckC(fileFullPath, code)
                elif os.path.splitext(cresCheckSource.FunctionList[func][3].split('\\')[-1])[1] in ['.procedure_design']:
                    CheckPROC(fileFullPath, code)
                else:
                    codeTmp = code

                    inPROC = False
                    while codeTmp != '':
                        if inPROC:
                            endIndex = codeTmp.find('[PRO*C语句块结束]')
                            if endIndex < 0:
                                CheckPROC(fileFullPath, codeTmp)
                                codeTmp = ''
                            else:
                                CheckPROC(fileFullPath, codeTmp[0:endIndex])
                                codeTmp = codeTmp[endIndex + len('[PRO*C语句块结束]'):]
                                inPROC = False
                        else:
                            beginIndex = codeTmp.find('[PRO*C语句块开始]')
                            if beginIndex < 0:
                                CheckC(fileFullPath, codeTmp)
                                codeTmp = ''
                            else:
                                CheckC(fileFullPath, codeTmp[0:beginIndex])
                                codeTmp = codeTmp[beginIndex + len('[PRO*C语句块开始]'):]
                                inPROC = True
