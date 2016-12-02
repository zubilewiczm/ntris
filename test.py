names = {"1"   : "MONO",
         "2"   : "DI",
         "3"   : "TRI",
         "4"   : "TETRA",
         "5"   : "PENTA",
         "6"   : "HEXA",
         "7"   : "HEPTA",
         "8"   : "OCTA",
         "9"   : "NONA",
         "10"  : "DECA",
         "11"  : "UNDECA",
         "12"  : "DODECA",
         "13"  : "TRIDECA",
         "14"  : "TETRADECA",
         "15"  : "PENTADECA",
         "16"  : "HEXADECA",
         "17"  : "HEPTADECA",
         "18"  : "OCTADECA",
         "19"  : "NONADECA",
         "20"  : "ICOSA",
         "21"  : "HENICOSA",
         "22"  : "DOCOSA",
         "23"  : "TRICOSA",
         "30"  : "TRIACONTA",
         "31"  : "HENTRIACONTA",
         "32"  : "DOTRIACONTA",
         "40"  : "TETRACONTA",
         "50"  : "PENTACONTA",
         "60"  : "HEXACONTA",
         "70"  : "HEPTACONTA",
         "80"  : "OCTACONTA",
         "90"  : "NONACONTA",
         "100" : "HECTA",
         "200" : "DICTA",
         "300" : "TRICTA",
         "400" : "TETRACTA",
         "500" : "PENTACTA",
         "600" : "HEXACTA",
         "700" : "HEPTACTA",
         "800" : "OCTACTA",
         "900" : "NONACTA" }

def name(n):
    if n >= 1000:
        return str(n)+"-TRIS"
    else:
        s = str(n)
        ret = ""
        while s:
            if s in names:
                ret = names[s]+ret
                break
            else:
                if s[0] != "0":
                    ret = names[s[0]+"0"*(len(s)-1)] + ret
                s = s[1:]
        ret = ret[0:-1]+"IS"
        return ret