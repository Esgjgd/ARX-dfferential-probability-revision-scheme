# 把所有差分路径调用ARX Toolkit处理，生成csv文件



import os


os.chdir('/home/es/Desktop/arxtoolkit/arxtools/arxtools')

# create .csv
csv = open('50.csv', 'a+')
csv.write('id,w,k0,k1,k2_15,k2_14,k2_13,k2_12,k2_11,k2_10,k2_9,k2_8,k2_7,k2_6,k2_5,k2_4,k2_3,k2_2,k2_1,k2_0,k3_15,'
          'k3_14,k3_13,k3_12,k3_11,k3_10,k3_9,k3_8,k3_7,k3_6,k3_5,k3_4,k3_3,k3_2,k3_1,k3_0,k4_15,k4_14,k4_13,k4_12,'
          'k4_11,k4_10,k4_9,k4_8,k4_7,k4_6,k4_5,k4_4,k4_3,k4_2,k4_1,k4_0,k5_15,k5_14,k5_13,k5_12,k5_11,k5_10,k5_9,'
          'k5_8,k5_7,k5_6,k5_5,k5_4,k5_3,k5_2,k5_1,k5_0,k6_15,k6_14,k6_13,k6_12,k6_11,k6_10,k6_9,k6_8,k6_7,k6_6,k6_5,'
          'k6_4,k6_3,k6_2,k6_1,k6_0,k7_15,k7_14,k7_13,k7_12,k7_11,k7_10,k7_9,k7_8,k7_7,k7_6,k7_5,k7_4,k7_3,k7_2,k7_1,'
          'k7_0,k8,k9' + '\n')

# p:path num
dic = {'35': 1, '36': 1, '37': 4, '38': 23, '39': 45, '40': 115, '41': 188, '42': 268,
       '43': 465, '44': 624, '45': 909, '46': 1383, '47': 2113, '48': 3371, '49': 5639, '50': 10106}


powlist = []
base = 1
for i in range(len(dic)):
    powlist.append(base)
    base *= 2
powlist.reverse()
# print(powlist)
# print(dic.keys())
# print(dic.values())
totalsum = 0
base = 1
powindex = 0
for keys in dic.keys():
    p = keys
    pnum = dic[keys]
    w = powlist[powindex]

    # read all paths and generate a .path
    inputfile = open("/root/PycharmProjects/pythonProject4/W40/SPECK32_" + p + ".txt", "r")
    q = inputfile.readlines()

    for num in range(0, pnum):
        for i in range(1, 12):
            locals()['l' + str(i)] = q[i + 14 * num][0:4]
            locals()['r' + str(i)] = q[i + 14 * num][5:9]
            # print(locals()['l' + str(i)],locals()['r' + str(i)])
        outputfile = open("/home/es/Desktop/arxtoolkit/arxtools/arxtools/paths/2.24/path/temp.path", "w")
        outputfile.write('''@conf wordsize = 16;
@vbox;
@vbox;
@state L0_0      	: #''' + l1 + '''
@state R0_0      	: #''' + r1 + '''
//
@state L0_1=L0_0%9
@state L0_2=L0_1+R0_0
@state k0        : ----------------
@state L1_0=L0_2^k0   	: #''' + l2 + ''' 
@state R0_1=R0_0%2
@state R1_0=R0_1^L1_0  	: #''' + r2 + ''' 
//
@state L1_1=L1_0%9
@state L1_2=L1_1+R1_0
@state k1        : ----------------
@state L2_0=L1_2^k1  	: #''' + l3 + ''' 
@state R1_1=R1_0%2
@state R2_0=R1_1^L2_0  	: #''' + r3 + '''
//
@state L2_1=L2_0%9
@state L2_2=L2_1+R2_0  	
@state k2        : ----------------
@state L3_0=L2_2^k2  	: #''' + l4 + '''  
@state R2_1=R2_0%2
@state R3_0=R2_1^L3_0  	: #''' + r4 + '''
//
@state L3_1=L3_0%9
@state L3_2=L3_1+R3_0	
@state k3		: ----------------
@state L4_0=L3_2^k3    	: #''' + l5 + '''   
@state R3_1=R3_0%2
@state R4_0=R3_1^L4_0  	: #''' + r5 + '''
//
@state L4_1=L4_0%9
@state L4_2=L4_1+R4_0	
@state k4		: ----------------
@state L5_0=L4_2^k4    	: #''' + l6 + '''   
@state R4_1=R4_0%2
@state R5_0=R4_1^L5_0  	: #''' + r6 + '''
//
@state L5_1=L5_0%9
@state L5_2=L5_1+R5_0	
@state k5		: ----------------
@state L6_0=L5_2^k5    	: #''' + l7 + '''     
@state R5_1=R5_0%2
@state R6_0=R5_1^L6_0  	: #''' + r7 + '''
//
@state L6_1=L6_0%9  
@state L6_2=L6_1+R6_0	
@state k6		: ----------------
@state L7_0=L6_2^k6    	: #''' + l8 + '''     
@state R6_1=R6_0%2
@state R7_0=R6_1^L7_0  	: #''' + r8 + '''
//
@state L7_1=L7_0%9 
@state L7_2=L7_1+R7_0	
@state k7		: ----------------
@state L8_0=L7_2^k7    	: #''' + l9 + ''' 
@state R7_1=R7_0%2
@state R8_0=R7_1^L8_0  	: #''' + r9 + '''
//
@state L8_1=L8_0%9 
@state L8_2=L8_1+R8_0	
@state k8		: ----------------
@state L9_0=L8_2^k8    	: #''' + l10 + ''' 
@state R8_1=R8_0%2
@state R9_0=R8_1^L9_0  	: #''' + r10 + '''
//
@state L9_1=L9_0%9 
@state L9_2=L9_1+R9_0	
@state k9		: ----------------
@state L10_0=L9_2^k9    : #''' + l11 + ''' 
@state R9_1=R9_0%2
@state R10_0=R9_1^L10_0 : #''' + r11 + '''
@end;
@end;
''')
        outputfile.close()

        # arxtoolkit run
        os.system('./pathtool2 paths/2.24/path/temp.path')

        # read result
        result = open('result', 'r+')
        resultline = result.readlines()

        # write csv
        index = 7
        addlist = []
        addlist.append(p + '_' + str(num) + ',' + str(w) + ',')
        for i in range(0, 10):
            # print(resultline[index + 6 * i][17:])
            if i == 0 or i == 1 or i == 8 or i == 9:
                addlist.append(',')
            else:
                if resultline[index + 6 * i][17:] == '----------------\n':
                    addlist.append(',,,,,,,,,,,,,,,,')
                else:
                    for j in resultline[index + 6 * i][17:-1]:
                        if j == '(':
                            continue
                        elif j == ')':
                            addlist.append(',')
                        elif j == '!' or j == '=' or j == '-':
                            addlist.append(j + ',')
                        else:
                            addlist.append(j)
        addlist.append('\n')
        # print(addlist)
        # print(''.join(addlist))
        csv.write(''.join(addlist))
        print('No.' + str(totalsum) + ' is finished.')
        totalsum += 1
    powindex += 1
li = []
for i in range(101):
    li.append(',-1')
csv.write('sum_!' + ''.join(li) + '\n')
csv.write('sum_=' + ''.join(li) + '\n')
csv.write('min(!_=)' + ''.join(li) + '\n')
csv.close()