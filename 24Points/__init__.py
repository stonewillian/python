#encoding:utf-8
import re

class TwentyFourPoint:
    def __init__(self,arg1,arg2,arg3,arg4):
        self.Arg1 = arg1
        self.Arg2 = arg2
        self.Arg3 = arg3
        self.Arg4 = arg4

        self.Algorithm = []

    def IsOrder(self, arg1, arg2, arg3, arg4, algo):
        #3,1,10,9,'3*(1+10)-9 = 24'
        pat = re.compile(r'([\d]+)', re.S)

        vars = re.findall(pat, algo)

        if vars:
            #print(vars)
            if len(vars) == 4 and \
               int(arg1) == int(vars[0]) and \
               int(arg2) == int(vars[1]) and \
               int(arg3) == int(vars[2]) and \
               int(arg4) == int(vars[3]):

               return True


        return False

    #返回args的所有结果组合及结果
    def Try(self,args):
        if len(args) > 4:
            print('Too many args for Try(*args):{0}',args)

        lst = {}

        #只有一项时,只有一个结果
        if len(args) == 1:
            lst["{0}".format(args[0])] = args[0]

        #有多项时,返回每一项与剩余的递归结果
        else:
            for i in range(len(args)):
                tmpList = self.Try(args[0:i] + args[i + 1:len(args)])

                for tmpKey in tmpList:
                    if len(args) > 2:
                        lst["{0}+{1}".format(args[i], tmpKey)] = args[i] + tmpList[tmpKey]

                        lst["{0}-({1})".format(args[i], tmpKey)] = args[i] - tmpList[tmpKey]

                        lst["{0}*({1})".format(args[i], tmpKey)] = args[i] * tmpList[tmpKey]

                        if tmpList[tmpKey] != 0:
                            lst["{0}÷({1})".format(args[i], tmpKey)] = args[i] / tmpList[tmpKey]

                        lst["{1}+{0}".format(args[i], tmpKey)] = tmpList[tmpKey] + args[i]

                        lst["{1}-{0}".format(args[i], tmpKey)] = tmpList[tmpKey] - args[i]

                        lst["({1})*{0}".format(args[i], tmpKey)] = tmpList[tmpKey] * args[i]

                        if args[i] != 0:
                            lst["({1})÷{0}".format(args[i], tmpKey)] = tmpList[tmpKey] / args[i]
                    else:
                        lst["{0}+{1}".format(args[i], tmpKey)] = args[i] + tmpList[tmpKey]

                        lst["{0}-{1}".format(args[i], tmpKey)] = args[i] - tmpList[tmpKey]

                        lst["{0}*{1}".format(args[i], tmpKey)] = args[i] * tmpList[tmpKey]

                        if tmpList[tmpKey] != 0:
                            lst["{0}÷{1}".format(args[i], tmpKey)] = args[i] / tmpList[tmpKey]


                        lst["{1}+{0}".format(args[i], tmpKey)] = tmpList[tmpKey] + args[i]

                        lst["{1}-{0}".format(args[i], tmpKey)] = tmpList[tmpKey] - args[i]

                        lst["{1}*{0}".format(args[i], tmpKey)] = tmpList[tmpKey] * args[i]

                        if args[i] != 0:
                            lst["{1}÷{0}".format(args[i], tmpKey)] = tmpList[tmpKey] / args[i]

        return lst

    def GetResult(self,NeedOrder = False):
        self.Algorithm.clear()

        res = self.Try((self.Arg1, self.Arg2, self.Arg3, self.Arg4))

        for k in res:
            #print("\t{0} = {1:.0f}".format(k, res[k]))

            if res[k] == 24 and (not NeedOrder or self.IsOrder(self.Arg1, self.Arg2, self.Arg3, self.Arg4, k)):
                self.Algorithm.append("\t{0: <15} = {1:.0f}".format(k,res[k]))

    def PrintResult(self):
        for k in self.Algorithm:
            print(k)

def main():
    #--------------单个测试-------------#
    tfP = TwentyFourPoint(7, 8, 6, 5)

    #有顺序要求
    print('Result in order is:')
    tfP.GetResult(True)
    tfP.PrintResult()

    #无顺序要求
    print('Result with no order is:')
    tfP.GetResult()
    tfP.PrintResult()

    #--------------10以内哪些不能得到24点--------------#
    #for i in range(1,10,1):
    #    for j in range(i,10,1):
    #        for k in range(j,10,1):
    #            for l in range(k,10,1):
    #                tfP = TwentyFourPoint(i,j,k,l)
    #
    #                tfP.GetResult(False)
    #
    #                if(len(tfP.Algorithm) == 0):
    #                    print(i,j,k,l)

    # --------------10以内哪些能得到24点--------------#
    #for i in range(1,10,1):
    #    for j in range(i,10,1):
    #        for k in range(j,10,1):
    #            for l in range(k,10,1):
    #                tfP = TwentyFourPoint(i,j,k,l)
    #
    #                tfP.GetResult(False)
    #
    #                print(i,j,k,l,':')
    #                tfP.PrintResult()

if __name__ == '__main__':

    main()