#����һ�п����ж��[/*-*/],������Ҫ�ݹ�
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

        # ����ܷ���--��//��/*
        if n0 >= 0 and n1 >= 0 and n2 >= 0:
            n = min(n0, n1)

            # ���ҵ�//����--
            if n <= n2:
                sCode = sCode + line[0:n] + '\n'
            # ���ҵ�/*
            else:
                sCode = sCode + line[0:n2]

                tmp = DealLine(line[n2 + len('/*'):], True)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]

        elif n0 >= 0 and n1 >= 0 and n2 < 0:

            n = min(n0, n1)

            sCode = sCode + line[0:n] + '\n'

        elif n0 >= 0 and n1 < 0 and n2 >= 0:

            # ���ҵ�--
            if n0 <= n2:
                sCode = sCode + line[0:n0] + '\n'
            # ���ҵ�/*
            else:
                sCode = sCode + line[0:n2]

                tmp = DealLine(line[n2 + len('/*'):], True)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]

        elif n0 >= 0 and n1 < 0 and n2 < 0:

            sCode = sCode + line[0:n0] + '\n'

        elif n0 < 0 and n1 >= 0 and n2 >= 0:
            # ���ҵ�//
            if n1 <= n2:
                sCode = sCode + line[0:n1] + '\n'
            # ���ҵ�/*
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

#�Ƴ������е�ע��
def RemoveNote(code):

    sCode = ''

    isNote = False

    # [/*,*/]����Ƕ��,//ֻ�Ե�������,--ֻ�Ե�������
    lines = code.split('\n')

    for line in lines:
        n0 = line.find('--')
        n1 = line.find('//')
        n2 = line.find('/*')
        n3 = line.find('*/')

        if isNote == False:

            # ����ܷ���--��//��/*
            if n0 >= 0 and n1 >= 0 and n2 >= 0:
                n = min(n0, n1)

                # ���ҵ�//����--
                if n <= n2:
                    sCode = sCode + line[0:n] + '\n'
                # ���ҵ�/*
                else:
                    sCode = sCode + line[0:n2]

                    tmp = DealLine(line[n2 + len('/*'):],True)

                    sCode = sCode + tmp[0] + '\n'

                    isNote = tmp[1]

            elif n0 >= 0 and n1 >= 0 and n2 < 0:

                n = min(n0, n1)

                sCode = sCode + line[0:n] + '\n'

            elif n0 >= 0 and n1 < 0 and n2 >= 0:

                # ���ҵ�--
                if n0 <= n2:
                    sCode = sCode + line[0:n0] + '\n'
                # ���ҵ�/*
                else:
                    sCode = sCode + line[0:n2]

                    tmp = DealLine(line[n2 + len('/*'):], True)

                    sCode = sCode + tmp[0] + '\n'

                    isNote = tmp[1]

            elif n0 >= 0 and n1 < 0 and n2 < 0:

                sCode = sCode + line[0:n0] + '\n'

            elif n0 < 0 and n1 >= 0 and n2 >= 0:
                # ���ҵ�//
                if n1 <= n2:
                    sCode = sCode + line[0:n1] + '\n'
                # ���ҵ�/*
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
            # �������Ƿ���*/,bExist��ʾ�Ƿ��ҵ�,ind_begin��ʾ����ҵ���λ��
            if n3 >= 0:
                tmp = DealLine(line[n3 + len('*/'):], False)

                sCode = sCode + tmp[0] + '\n'

                isNote = tmp[1]
            else:
                sCode = sCode + '\n'

    #print(sCode)

    return sCode