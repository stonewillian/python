#由于一行可能有多个[/*-*/],所以需要递归
def DealLine(line,isNote):
    #print(line)
    sCode = ''

    if isNote:
        n3 = line.find('*/')

        if n3 >= 0:
            tmp = DealLine(line[n3 + len('*/'):], False)

            sCode = sCode + tmp[0] + '\n'

            isNote = tmp[1]

    else:
        n0 = line.find('--')
        n1 = line.find('//')
        n2 = line.find('/*')

        # 如果能发现--、//、/*
        if n0 >= 0 and n1 >= 0 and n2 >= 0:
            n = min(n0, n1)

            # 先找到//或者--
            if n <= n2:
                sCode = sCode + line[0:n] + '\n'
            # 先找到/*
            else:
                sCode = sCode + line[0:n2]

                tmp = DealLine(line[n2 + len('/*'):], True)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]

        elif n0 >= 0 and n1 >= 0 and n2 < 0:

            n = min(n0, n1)

            sCode = sCode + line[0:n] + '\n'

        elif n0 >= 0 and n1 < 0 and n2 >= 0:

            # 先找到--
            if n0 <= n2:
                sCode = sCode + line[0:n0] + '\n'
            # 先找到/*
            else:
                sCode = sCode + line[0:n2]

                tmp = DealLine(line[n2 + len('/*'):], True)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]

        elif n0 >= 0 and n1 < 0 and n2 < 0:

            sCode = sCode + line[0:n0] + '\n'

        elif n0 < 0 and n1 >= 0 and n2 >= 0:
            # 先找到//
            if n1 <= n2:
                sCode = sCode + line[0:n1] + '\n'
            # 先找到/*
            else:
                sCode = sCode + line[0:n2]

                tmp = DealLine(line[n2 + len('/*'):], True)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]

        elif n0 < 0 and n1 >= 0 and n2 < 0:

            sCode = sCode + line[0:n1] + '\n'

        elif n0 < 0 and n1 < 0 and n2 >= 0:

            sCode = sCode + line[0:n2]

            tmp = DealLine(line[n2 + len('/*'):], True)

            sCode = sCode + tmp[0] + '\n'

            isNote = tmp[1]

        else:
            sCode = sCode + line + '\n'

    return [sCode,isNote]

#移除代码中的注释
def RemoveNote(code):

    sCode = ''

    isNote = False

    # [/*,*/]不能嵌套,//只对单行有用,--只对单行有用
    lines = code.split('\n')

    for line in lines:
        n0 = line.find('--')
        n1 = line.find('//')
        n2 = line.find('/*')
        n3 = line.find('*/')

        if isNote == False:

            # 如果能发现--、//、/*
            if n0 >= 0 and n1 >= 0 and n2 >= 0:
                n = min(n0, n1)

                # 先找到//或者--
                if n <= n2:
                    sCode = sCode + line[0:n] + '\n'
                # 先找到/*
                else:
                    sCode = sCode + line[0:n2]

                    tmp = DealLine(line[n2 + len('/*'):],True)

                    sCode = sCode + tmp[0] + '\n'

                    isNote = tmp[1]

            elif n0 >= 0 and n1 >= 0 and n2 < 0:

                n = min(n0, n1)

                sCode = sCode + line[0:n] + '\n'

            elif n0 >= 0 and n1 < 0 and n2 >= 0:

                # 先找到--
                if n0 <= n2:
                    sCode = sCode + line[0:n0] + '\n'
                # 先找到/*
                else:
                    sCode = sCode + line[0:n2]

                    tmp = DealLine(line[n2 + len('/*'):], True)

                    sCode = sCode + tmp[0] + '\n'

                    isNote = tmp[1]

            elif n0 >= 0 and n1 < 0 and n2 < 0:

                sCode = sCode + line[0:n0] + '\n'

            elif n0 < 0 and n1 >= 0 and n2 >= 0:
                # 先找到//
                if n1 <= n2:
                    sCode = sCode + line[0:n1] + '\n'
                # 先找到/*
                else:
                    sCode = sCode + line[0:n2]

                    tmp = DealLine(line[n2 + len('/*'):], True)

                    sCode = sCode + tmp[0] + '\n'

                    isNote = tmp[1]

            elif n0 < 0 and n1 >= 0 and n2 < 0:

                sCode = sCode + line[0:n1] + '\n'

            elif n0 < 0 and n1 < 0 and n2 >= 0:

                sCode = sCode + line[0:n2]

                tmp = DealLine(line[n2 + len('/*'):], True)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]

            else:
                sCode = sCode + line + '\n'
        else:
            # 看本行是否有*/,bExist表示是否找到,ind_begin表示最后找到的位置
            if n3 >= 0:
                tmp = DealLine(line[n3 + len('*/'):], False)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]
            else:
                sCode = sCode + '\n'

    #print(sCode)

    return sCode