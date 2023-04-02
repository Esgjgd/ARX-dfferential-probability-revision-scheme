# 使用cadical（SAT求解器）搜索差分路径

import os
import time

SIZE = [16, 24, 32, 48, 64]
ROTATIONA = [7, 8, 8, 8, 8]
ROTATIONB = [2, 3, 3, 3, 3]
FULLROUND = [10, 23, 27, 29, 34]

NUM = 0
INDEX = [
    48, 64,
    95, 111,
    142, 158,
    189, 205,
    236, 252,
    283, 299,
    330, 346,
    377, 393,
    424, 440,
]

ChooseCipher = 0

SearchRoundStart = 1
SearchRoundEnd = FULLROUND[ChooseCipher]
InitialLowerBound = 0

ProbabilityBound = list([])
for i in range(SearchRoundEnd + 1):
    ProbabilityBound += [0]


Trail_9 = [
    # round1
    [0, 0, 1, 0,
     1, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 0],

    [0, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 1,
     0, 0, 0, 0],

    # round 10
    [0, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 0,
     0, 1, 0, 0],
    [0, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 1,
     0, 1, 0, 0],
]

EXCLUDE = []

def readSolFile(filename):
    ''' from the file
    eg s SATISFIABLE
       v 0 2 -3 -4 0
    return: [0, 2, -3, -4]
    '''
    ff = open(filename)
    lines = ff.readlines()
    ff.close()

    res = []
    for line in lines:
        if line.find('UNSAT') != -1:
            print(line)
            return []
        if line.find('v ') != -1:
            line = line.lstrip('v ')
            line = line.rstrip(' \n')
            ll = line.split(' ')
            res += list(map(int, ll))
    return res

def findIndex(filename, j):
    res = readSolFile(filename)
    w = 0
    list = []
    for i in res:
        if abs(i) in range(j, j+SIZE[ChooseCipher]):
            if i > 0:
                if i != j + SIZE[ChooseCipher] - 1:
                    w += 1
                list.append((i - j + 1))
    return list

def toBinary(l):
    res = []
    r = [i for i in range(1, 1 + SIZE[ChooseCipher])]
    for i in r:
        if i in l:
            res += [1]
        else:
            res += [0]
    return res

def cnf_for_assignment(numList, valList):
    # assign a list of variables (numbers) with 0-0 values given in valList
    constr = []
    assert len(numList) == len(valList), "incompatible size of lists when assigning?"
    for i in range(len(numList)):
        if valList[i]:
            constr.append("%d 0" % (numList[i]))
        else:
            constr.append("%d 0" % (-numList[i]))
    return constr


def ExtractionResults(File):
    Result = "NoResult"
    Results = ""

    file = open(File, "rb")
    StopResult = 1
    StartResult = 0

    while StopResult:
        result = str(file.readline())
        if "[ result ]" in result:
            StartResult = 1
            continue
        if "run-time profiling" in result:
            StopResult = 0
            break

        if StartResult == 1:
            if "SATISFIABLE" in result:
                Result = "SATISFIABLE"
            if "UNSATISFIABLE" in result:
                Result = "UNSATISFIABLE"
                break
            Results += result
            Results += '\n'

        Results = Results.replace("b'", "")
        Results = Results.replace(" '", "")
        Results = Results.replace("'", "")
        Results = Results.replace("c ", "")
        Results = Results.replace("\\n", "")

    return (Result, Results)

def GenerateAndCountVariables(Round, Probability):
    xin = []
    wvar = []
    xout = []

    count_var_num = 0
    for i in range(Round):
        xin.append([])
        wvar.append([])
        for j in range(2 * SIZE[ChooseCipher]):
            count_var_num += 1
            xin[i].append(count_var_num)

        for j in range(SIZE[ChooseCipher] - 1):
            count_var_num += 1
            wvar[i].append(count_var_num)

    for i in range(Round - 1):
        xout.append([])
        for j in range(2 * SIZE[ChooseCipher]):
            xout[i].append(xin[i + 1][j])
    xout.append([])
    for j in range(2 * SIZE[ChooseCipher]):
        count_var_num += 1
        xout[Round - 1].append(count_var_num)

    auxiliary_var_u = []
    for r in range(1, Round + 1):
        auxiliary_var_u.append([])
        for i in range(SIZE[ChooseCipher] - 1):
            if (r == Round) and (i == SIZE[ChooseCipher] - 2):
                continue
            auxiliary_var_u[r - 1].append([])
            for j in range(0, Probability):
                count_var_num += 1
                auxiliary_var_u[r - 1][i].append(count_var_num)
    return (xin, wvar, xout, auxiliary_var_u, count_var_num)


def CountClausesInRoundFunction(Round, count_clause_num):
    count_clause_num += 1
    count_clause_num += Round * (4 + 13 * (SIZE[ChooseCipher] - 1) + 4 * (SIZE[ChooseCipher]))
    if Round == FULLROUND[ChooseCipher]:
        count_clause_num += SIZE[ChooseCipher] * 4
        count_clause_num += NUM
    return count_clause_num

def cnf_for_not_equal(numList, valList):
    # assign a list of variables (numbers) with 0-0 values given in valList
    ans = []
    assert len(numList) == len(valList), "incompatible size of lists when assigning?"
    for i in range(len(numList)):
        assert len(numList[i]) == len(valList[i])
        constr = ''
        for j in range(len(valList[i])):
            assert len(numList[i][j]) == len(valList[i][j])
            for k in range(len(valList[i][j])):
                if valList[i][j][k]:
                    constr += ('-' + str(numList[i][j][k]) + ' ')
                else:
                    constr += (str(numList[i][j][k]) + ' ')
        constr += "0\n"
        ans.append(constr)
    return ans

def GenRoundConstrain(TotalRound, xin, wvar, xout, file):
    clauseseq = ""
    for i in range(2 * SIZE[ChooseCipher]):
        clauseseq += str(xin[0][i]) + " "
    clauseseq += "0\n"
    file.write(clauseseq)

    for r in range(TotalRound):
        Lxin = []
        Rxin = []
        Lxout = []
        Rxout = []
        LRotationAxin = []
        RRotationBxin = []
        for i in range(SIZE[ChooseCipher]):
            Lxin.append(xin[r][i])
            Rxin.append(xin[r][i + SIZE[ChooseCipher]])
            Lxout.append(xout[r][i])
            Rxout.append(xout[r][i + SIZE[ChooseCipher]])
        for i in range(SIZE[ChooseCipher]):
            LRotationAxin.append(Lxin[(i - ROTATIONA[ChooseCipher]) % SIZE[ChooseCipher]])
            RRotationBxin.append(Rxin[(i + ROTATIONB[ChooseCipher]) % SIZE[ChooseCipher]])

        if r == TotalRound - 1:
            cnt = 0
            Lxin1 = []
            Rxin1 = []

            for i in range(SIZE[ChooseCipher]):
                Lxin1.append(xin[0][i])
                Rxin1.append(xin[0][i + SIZE[ChooseCipher]])

            file.write("c constraints of Lxin\n")
            C1 = cnf_for_assignment(Lxin1, Trail_9[cnt])
            out1 = []
            out1.extend("\n".join(C1) + "\n")
            file.write("".join(out1))
            cnt += 1
            file.write("c constraints of Rxin\n")
            C2 = cnf_for_assignment(Rxin1, Trail_9[cnt])
            out2 = []
            out2.extend("\n".join(C2) + "\n")
            file.write("".join(out2))
            cnt += 1

            # fix the first 9 rounds
            file.write("c fix the input and output of the diff_9\n")

            # only fix the first and last round
            Lxout1 = []
            Rxout1 = []

            for i in range(SIZE[ChooseCipher]):
                Lxout1.append(xout[r][i])
                Rxout1.append(xout[r][i + SIZE[ChooseCipher]])

            file.write("c constraints of Lxout\n")
            C3 = cnf_for_assignment(Lxout1, Trail_9[cnt])
            out3 = []
            out3.extend("\n".join(C3) + "\n")
            file.write("".join(out3))
            cnt += 1
            file.write("c constraints of Rxout\n")
            C4 = cnf_for_assignment(Rxout1, Trail_9[cnt])
            out4 = []
            out4.extend("\n".join(C4) + "\n")
            file.write("".join(out4))

            cnt = 0
            numList = []
            for t in range(NUM):
                numList.append([])
                # exclude the previous solutions
                Lxout2 = []
                Rxout2 = []

                for i in range(SIZE[ChooseCipher]):
                    Lxout2.append(xout[0][i])
                    Rxout2.append(xout[0][i + SIZE[ChooseCipher]])

                numList[t].append(Lxout2)
                numList[t].append(Rxout2)

                # for 2nd to rth round
                for i in range(1, r):
                    Lxout2 = []
                    Rxout2 = []
                    for j in range(SIZE[ChooseCipher]):
                        Lxout2.append(xout[i][j])
                        Rxout2.append(xout[i][j + SIZE[ChooseCipher]])
                    numList[t].append(Lxout2)
                    numList[t].append(Rxout2)


            if NUM > 0:
                file.write("c exclude the previous solutions\n")
                C1 = cnf_for_not_equal(numList, EXCLUDE)
                out1 = []
                out1.extend("".join(C1) + "\n")
                file.write("".join(out1))

        i = SIZE[ChooseCipher] - 1
        clauseseq = str(LRotationAxin[i]) + " " + str(Rxin[i]) + " " + str(-(Lxout[i])) + " 0\n"
        file.write(clauseseq)
        clauseseq = str(LRotationAxin[i]) + " " + str(-(Rxin[i])) + " " + str(Lxout[i]) + " 0\n"
        file.write(clauseseq)
        clauseseq = str(-(LRotationAxin[i])) + " " + str(Rxin[i]) + " " + str(Lxout[i]) + " 0\n"
        file.write(clauseseq)
        clauseseq = str(-(LRotationAxin[i])) + " " + str(-(Rxin[i])) + " " + str(-(Lxout[i])) + " 0\n"
        file.write(clauseseq)

        file.write("c the variables of LRotationAxin、Rxin、Lxout\n")
        for i in range(0, SIZE[ChooseCipher] - 1):
            clauseseq = str(LRotationAxin[i]) + " " + str(Rxin[i]) + " " + str(-(Lxout[i])) + " " + str(
                LRotationAxin[i + 1]) + " " + str(Rxin[i + 1]) + " " + str(Lxout[i + 1]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(LRotationAxin[i]) + " " + str(-(Rxin[i])) + " " + str(Lxout[i]) + " " + str(
                LRotationAxin[i + 1]) + " " + str(Rxin[i + 1]) + " " + str(Lxout[i + 1]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(LRotationAxin[i])) + " " + str(Rxin[i]) + " " + str(Lxout[i]) + " " + str(
                LRotationAxin[i + 1]) + " " + str(Rxin[i + 1]) + " " + str(Lxout[i + 1]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(LRotationAxin[i])) + " " + str(-(Rxin[i])) + " " + str(-(Lxout[i])) + " " + str(
                LRotationAxin[i + 1]) + " " + str(Rxin[i + 1]) + " " + str(Lxout[i + 1]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(LRotationAxin[i]) + " " + str(Rxin[i]) + " " + str(Lxout[i]) + " " + str(
                -(LRotationAxin[i + 1])) + " " + str(-(Rxin[i + 1])) + " " + str(-(Lxout[i + 1])) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(LRotationAxin[i]) + " " + str(-(Rxin[i])) + " " + str(-(Lxout[i])) + " " + str(
                -(LRotationAxin[i + 1])) + " " + str(-(Rxin[i + 1])) + " " + str(-(Lxout[i + 1])) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(LRotationAxin[i])) + " " + str(Rxin[i]) + " " + str(-(Lxout[i])) + " " + str(
                -(LRotationAxin[i + 1])) + " " + str(-(Rxin[i + 1])) + " " + str(-(Lxout[i + 1])) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(LRotationAxin[i])) + " " + str(-(Rxin[i])) + " " + str(Lxout[i]) + " " + str(
                -(LRotationAxin[i + 1])) + " " + str(-(Rxin[i + 1])) + " " + str(-(Lxout[i + 1])) + " 0\n"
            file.write(clauseseq)

        for i in range(0, SIZE[ChooseCipher] - 1):
            clauseseq = str(-(LRotationAxin[i + 1])) + " " + str(Lxout[i + 1]) + " " + str(wvar[r][i]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(Rxin[i + 1]) + " " + str(-(Lxout[i + 1])) + " " + str(wvar[r][i]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(LRotationAxin[i + 1]) + " " + str(-(Rxin[i + 1])) + " " + str(wvar[r][i]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(LRotationAxin[i + 1]) + " " + str(Rxin[i + 1]) + " " + str(Lxout[i + 1]) + " " + str(
                -(wvar[r][i])) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(LRotationAxin[i + 1])) + " " + str(-(Rxin[i + 1])) + " " + str(
                -(Lxout[i + 1])) + " " + str(-(wvar[r][i])) + " 0\n"
            file.write(clauseseq)

        file.write("c the variables of Lxout、RRotationBxin、Rxout\n")
        for i in range(0, SIZE[ChooseCipher]):
            clauseseq = str(Lxout[i]) + " " + str(RRotationBxin[i]) + " " + str(-(Rxout[i])) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(Lxout[i]) + " " + str(-(RRotationBxin[i])) + " " + str(Rxout[i]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(Lxout[i])) + " " + str(RRotationBxin[i]) + " " + str(Rxout[i]) + " 0\n"
            file.write(clauseseq)
            clauseseq = str(-(Lxout[i])) + " " + str(-(RRotationBxin[i])) + " " + str(-(Rxout[i])) + " 0\n"
            file.write(clauseseq)


def CountClausesForMatsuiStrategy(Wvars, Uvars, Probability, left, right, m, count_clause_num):
    if (m > 0):
        if ((left == 0) and (right < len(Wvars) - 1)):
            for i in range(1, right + 1):
                count_clause_num += 1
        if ((left > 0) and (right == len(Wvars) - 1)):
            for i in range(0, Probability - m):
                count_clause_num += 1
            for i in range(0, Probability - m + 1):
                count_clause_num += 1
        if ((left > 0) and (right < len(Wvars) - 1)):
            for i in range(0, Probability - m):
                count_clause_num += 1
    if (m == 0):
        for i in range(left, right + 1):
            count_clause_num += 1
    return (count_clause_num)


def GenMatsuiConstraint(Wvars, Uvars, Probability, left, right, m, file):
    if (m > 0):
        if ((left == 0) and (right < len(Wvars) - 1)):
            for i in range(1, right + 1):
                clauseseq = "-" + str(Wvars[i]) + " " + "-" + str(Uvars[i - 1][m - 1]) + " 0" + "\n"
                file.write(clauseseq)
        if ((left > 0) and (right == len(Wvars) - 1)):
            for i in range(0, Probability - m):
                clauseseq = str(Uvars[left - 1][i]) + " " + "-" + str(Uvars[right - 1][i + m]) + " 0" + "\n"
                file.write(clauseseq)
            for i in range(0, Probability - m + 1):
                clauseseq = str(Uvars[left - 1][i]) + " " + "-" + str(Uvars[right]) + " " + "-" + str(
                    Uvars[right - 1][i + m - 1]) + " 0" + "\n"
                file.write(clauseseq)
        if ((left > 0) and (right < len(Wvars) - 1)):
            for i in range(0, Probability - m):
                clauseseq = str(Uvars[left - 1][i]) + " " + "-" + str(Uvars[right][i + m]) + " 0" + "\n"
                file.write(clauseseq)
    if (m == 0):
        for i in range(left, right + 1):
            clauseseq = "-" + str(Wvars[i]) + " 0" + "\n"
            file.write(clauseseq)


def CountClausesInSequentialEncoding(TotalRound, Probability, Wvars, Uvars, count_clause_num):
    if (Probability > 0):
        count_clause_num += 1
        for i in range(1, Probability):
            count_clause_num += 1

        for i in range(1, len(Wvars) - 1):
            count_clause_num += 1
            count_clause_num += 1
            count_clause_num += 1
        for j in range(1, Probability):
            for i in range(1, len(Wvars) - 1):
                count_clause_num += 1
                count_clause_num += 1
        count_clause_num += 1

    elif (Probability == 0):
        for i in range(len(Wvars)):
            count_clause_num += 1

    return (count_clause_num)


def GenSequentialEncoding(TotalRound, Probability, Wvars, Uvars, file):
    if (Probability > 0):
        clauseseq = "-" + str(Wvars[0]) + " " + str(Uvars[0][0]) + " 0" + "\n"
        file.write(clauseseq)
        for i in range(1, Probability):
            clauseseq = "-" + str(Uvars[0][i]) + " 0" + "\n"
            file.write(clauseseq)

        for i in range(1, len(Wvars) - 1):
            clauseseq = "-" + str(Wvars[i]) + " " + str(Uvars[i][0]) + " 0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(Uvars[i - 1][0]) + " " + str(Uvars[i][0]) + " 0" + "\n"
            file.write(clauseseq)
            clauseseq = "-" + str(Wvars[i]) + " " + "-" + str(Uvars[i - 1][Probability - 1]) + " 0" + "\n"
            file.write(clauseseq)
        for j in range(1, Probability):
            for i in range(1, len(Wvars) - 1):
                clauseseq = "-" + str(Wvars[i]) + " " + "-" + str(Uvars[i - 1][j - 1]) + " " + str(
                    Uvars[i][j]) + " 0" + "\n"
                file.write(clauseseq)
                clauseseq = "-" + str(Uvars[i - 1][j]) + " " + str(Uvars[i][j]) + " 0" + "\n"
                file.write(clauseseq)
        clauseseq = "-" + str(Wvars[len(Wvars) - 1]) + " " + "-" + str(
            Uvars[len(Wvars) - 2][Probability - 1]) + " 0" + "\n"
        file.write(clauseseq)

    elif (Probability == 0):
        for i in range(len(Wvars)):
            clauseseq = "-" + str(Wvars[i]) + " 0\n"
            file.write(clauseseq)


def Decision(TotalRound, MatsuiRoundIndex):
    Probability = ProbabilityBound[TotalRound]
    time_start = time.time()
    count_var_num = 0
    count_clause_num = 0

    (xin, wvar, xout, auxiliary_var_u, count_var_num) = GenerateAndCountVariables(TotalRound, Probability)
    Wvars = []
    for var in wvar:
        Wvars += var
    Uvars = []
    for uvar in auxiliary_var_u:
        Uvars += uvar

    count_clause_num = CountClausesInRoundFunction(TotalRound, count_clause_num)
    count_clause_num = CountClausesInSequentialEncoding(TotalRound, Probability, Wvars, Uvars, count_clause_num)

    file = open("W40/Problem-Round" + str(TotalRound) + "-Probability" + str(Probability) + "_" + str(NUM) + ".cnf", "w")
    file.write("p cnf " + str(count_var_num) + " " + str(count_clause_num) + "\n")

    GenRoundConstrain(TotalRound, xin, wvar, xout, file)
    GenSequentialEncoding(TotalRound, Probability, Wvars, Uvars, file)

    file.close()
    time_start = time.time()

    order = "/home/es/Desktop/cadical-master/build/cadical " + "W40/Problem-Round" + str(TotalRound) + "-Probability" + str(
        Probability) + "_" + str(NUM) + ".cnf > W40/Round" + str(TotalRound) + "-Probability" + str(Probability) + "_" + str(NUM) + "-solution.txt"
    os.system(order)
    time_end = time.time()

    (Result, Results) = ExtractionResults(
        "W40/Round" + str(TotalRound) + "-Probability" + str(Probability) + "_" + str(NUM) + "-solution.txt")
    time_end = time.time()
    if Result == "SATISFIABLE":
        wvarResult = []
        for var in wvar:
            for v in var:
                wvarResult.append(Results[v - 1])

    if (Result == "SATISFIABLE"):
        print("Round:" + str(TotalRound) + "; Probability: " + str(Probability) + "; Sat; TotalCost: " + str(
            time_end - time_start))
    else:
        print("Round:" + str(TotalRound) + "; Probability: " + str(Probability) + "; Unsat; TotalCost: " + str(
            time_end - time_start))

    fileResult = open("ProcessResult.txt", "a")
    if (Result == "SATISFIABLE"):
        fileResult.write(
            "\n Round:" + str(TotalRound) + "; Probability: " + str(Probability) + "; Sat; TotalCost: " + str(
                time_end - time_start) + " p: " + str(count_var_num) + " cnf: " + str(count_clause_num))
    else:
        fileResult.write(
            "\n Round:" + str(TotalRound) + "; Probability: " + str(Probability) + "; Unsat; TotalCost: " + str(
                time_end - time_start) + " p: " + str(count_var_num) + " cnf: " + str(count_clause_num))

    fileResult.close()

    order = "rm W40/Problem-Round" + str(TotalRound) + "-Probability" + str(Probability) + "_" + str(NUM) + ".cnf"
    os.system(order)

    return (Result, count_var_num, count_clause_num, time_end - time_start)


Total_var_num = 0
Total_clause_num = 0
Total_Solve_time = 0

count = 0
for totalround in range(SearchRoundEnd, SearchRoundEnd + 1):
    count_var_num = 0
    count_clause_num = 0
    count_time = 0

    Result = "SATISFIABLE"
    # ProbabilityBound[totalround] = ProbabilityBound[totalround - 0] + ProbabilityBound[0]
    ProbabilityBound[totalround] = 50
    MatsuiCount = 0
    MatsuiRoundIndex = []
    for Round in range(1, totalround + 1):
        MatsuiRoundIndex.append([])
        MatsuiRoundIndex[MatsuiCount].append(0)
        MatsuiRoundIndex[MatsuiCount].append(Round)
        MatsuiCount += 1

    file = open("MatsuiCondition.out", "a")
    resultseq = "Round: " + str(totalround) + "; Partial Constraint Num: " + str(MatsuiCount) + "\n"
    file.write(resultseq)
    file.write(str(MatsuiRoundIndex) + "\n")
    file.close()
    pre_sum = 0
    for i in range(1):
        while (Result == "SATISFIABLE"):
            print(count)
            count += 1
            (Result, var_num, clause_num, Time) = Decision(totalround, MatsuiRoundIndex)

            count_var_num += var_num
            count_clause_num += clause_num
            count_time += Time

            if(Result == "UNSATISFIABLE"):
                break;

            (result, results) = ExtractionResults(
                "W40/Round" + str(totalround) + "-Probability" + str(ProbabilityBound[totalround]) + "_" + str(
                    NUM) + "-solution.txt")

            file1 = open("Result-Round" + str(totalround) + "-Probability" + str(ProbabilityBound[totalround]) + "_" + str(
                    NUM) + "-solution.txt", "w")
            file1.write(results)
            EXCLUDE.append([])
            for i in INDEX:
                EXCLUDE[NUM].append(
                        toBinary(findIndex("Result-Round" + str(totalround) + "-Probability" + str(ProbabilityBound[totalround]) + "_" + str(
                    NUM) + "-solution.txt", i)))
            order = "rm Result-Round" + str(totalround) + "-Probability" + str(ProbabilityBound[totalround]) + "_" + str(
                    NUM) + "-solution.txt"
            os.system(order)
            NUM += 1
        file2 = open("TrailSummaries.out", "a")
        file2.write(str(ProbabilityBound[totalround]) + ": " + str(NUM - pre_sum) + "\n")
        ProbabilityBound[totalround] += 1
        Result = "SATISFIABLE"
        pre_sum =NUM

    Total_var_num += count_var_num
    Total_clause_num += count_clause_num
    Total_Solve_time += count_time

    file = open("RunTimeSummarise.out", "a")
    resultseq = "Round: " + str(totalround) + "; Probability: " + str(
        ProbabilityBound[totalround]) + "; Runtime: " + str(count_time) + " count_var_num: " + str(
        count_var_num) + " count_clause_num: " + str(count_clause_num) + " Total_var_num: " + str(
        Total_var_num) + " Total_clause_num: " + str(Total_clause_num) + " Total_Solver_time: " + str(
        Total_Solve_time) + "\n"
    file.write(resultseq)
    file.close()

print(str(ProbabilityBound))
file = open("RunTimeSummarise.out", "a")
resultseq = "Total Time of Solving SAT Model: " + str(Total_Solve_time) + " Total_var_num: " + str(
    Total_var_num) + " Total_clause_num" + str(Total_clause_num)
file.write(resultseq)
file.close()






# 差分路径按概率保存为文本文件

SIZE = 16
weight = []
def readSolFile(filename):
    ''' from the file
    eg s SATISFIABLE
       v 0 2 -3 -4 0
    return: [0, 2, -3, -4]
    '''
    ff = open(filename)
    lines = ff.readlines()
    ff.close()

    res = []
    for line in lines:
        if line.find('UNSAT') != -1:
            print(line)
            return []
        if line.find('v ') != -1:
            line = line.lstrip('v ')
            line = line.rstrip(' \n')
            ll = line.split(' ')
            res += list(map(int, ll))
    return res

def findIndex(filename, j):
    res = readSolFile(filename)
    w = 0
    list = []
    for i in res:
        if abs(i) in range(j, j+SIZE):
            if i > 0:
                if i != j + SIZE - 1:
                    w += 1
                list.append((i - j + 1))
    return list

def findIndex2(filename, j):
    res = readSolFile(filename)
    w = 0
    list = []
    for i in res:
        if abs(i) in range(j, j+SIZE):
            if i > 0:
                if i != j + SIZE - 1:
                    w += 1
                list.append((i - j + 1))
    weight.append(w)
    return list

def toBinary(l):
    res = []
    r = [i for i in range(1, 1 + SIZE)]
    for i in r:
        if i in l:
            res += [1]
        else:
            res += [0]
    return res

def toHex(l):
    res = ""
    for i in l:
        res += str(i)
    ans = hex(int(res, 2))[2:]
    while(len(ans) < SIZE / 4):
        ans = "0" + ans
    return ans


def ExtractionResults(File):
    Result = "NoResult"
    Results = ""

    file = open(File, "rb")
    StopResult = 1
    StartResult = 0

    while StopResult:
        result = str(file.readline())
        if "[ result ]" in result:
            StartResult = 1
            continue
        if "run-time profiling" in result:
            StopResult = 0
            break

        if StartResult == 1:
            if "SATISFIABLE" in result:
                Result = "SATISFIABLE"
            if "UNSATISFIABLE" in result:
                Result = "UNSATISFIABLE"
                break
            Results += result
            Results += '\n'

        Results = Results.replace("b'", "")
        Results = Results.replace(" '", "")
        Results = Results.replace("'", "")
        Results = Results.replace("c ", "")
        Results = Results.replace("\\n", "")

    return (Result, Results)

index = [
    # SPECK32
    1, 17,
    48, 64,
    95, 111,
    142, 158,
    189, 205,
    236, 252,
    283, 299,
    330, 346,
    377, 393,
    424, 440,
    471, 487,
]

wt = [
    # SPECK32
    33, 80, 127, 174, 221, 268, 315, 362,
    409,
    456
]


for i in range(35, 51):
    locals()['file' + str(i)] = open("W40/SPECK" + str(SIZE * 2) + "_" + str(i) + ".txt", "w")
    locals()['num' + str(i)] = 0

# 25255 50
for i in range(25255):
    weight = []
    Array = []
    (result, results) = ExtractionResults("W40/Round10-Probability50_" + str(i) + "-solution.txt")
    with open("test.txt", "w") as file:
        file.write(results)
    for i in index:
        print(toBinary(findIndex("test.txt", i)), ',')
        Array.append(toBinary(findIndex("test.txt", i)))

    for j in wt:
        findIndex2("test.txt", j)
    print(weight)
    print(sum(weight))

    locals()['file' + str(sum(weight))].write('No.' + str(locals()['num' + str(sum(weight))]) + "\n")
    locals()['num' + str(sum(weight))] += 1
    cnt = 0
    for l in Array:
        cnt += 1
        if cnt < 2:
            locals()['file' + str(sum(weight))].write(toHex(l) + " ")
        else:
            locals()['file' + str(sum(weight))].write(toHex(l) + "\n")
            cnt = 0
    locals()['file' + str(sum(weight))].write(str(sum(weight)) + ": ")
    locals()['file' + str(sum(weight))].write(str(weight) + "\n")
    locals()['file' + str(sum(weight))].write("=================\n")

    print("=======================")
