#!/bin/python

import copy

from itertools import product

class Symbol:
    def __init__(self, token, isTerminal = True):
        self.token = token
        self.isTerminal = isTerminal

    def set_terminal(self, isTerminal):
        self.isTerminal = isTerminal

    def __str__(self):
        return self.token


class Generator:
    """ 生成式类

    Attr:
        leftvalue (Symbol) : 生成式的左值，必须是非终极符
        rightvalue (list, Symbol): 生成式的右值，可以是多个符号(list)或者单个符号(Symbol)
    """
    def __init__(self, leftvalue, rightvalue):
        assert(isinstance(rightvalue, (list, tuple, Symbol)))
        assert(isinstance(leftvalue, Symbol) and leftvalue.isTerminal == False)

        self.leftvalue = leftvalue
        self.rightvalue = []

        if isinstance(rightvalue, (list, tuple)):
            for val in rightvalue:
                assert(isinstance(val, Symbol))
                self.rightvalue.append(val)
        else:
            self.rightvalue.append(rightvalue)


    def reverseProduce(self, *args):
        length = len(args)

        if(length != len(self.rightvalue)):
            return None

        for thissymbol, arg in zip(self.rightvalue, args):
            assert(isinstance(arg, (str, Symbol)))
            if isinstance(arg, str) and thissymbol.token != arg:
                return None
            elif isinstance(arg, Symbol) and thissymbol.token != arg.token:
                return None

        return self.leftvalue


class RegularGrammar:
    """ 正则文法类
    """

    def __init__(self, terminals, nterminals):

        self.terminals = terminals
        self.nterminals = nterminals
        self._terminals_tokens = [x.token for x in self.terminals]
        self._nterminals_tokens = [x.token for x in self.nterminals]
        self.generators = []


    def add_generator(self, gen):

        assert(isinstance(gen, Generator))

        # 检查需要添加的生成式的所有字符是否在字符集内
        assert gen.leftvalue in self.terminals,\
             "Left value of generator not in non-terminal sets"

        for val in gen.rightvalue:
            assert val in self.terminals or val in self.nterminals , \
                "Right value of generator not in symbol sets"

        self.generators.append(gen)

    def add_generator_str(self, leftvalue, *rightvalue):
        """ 通过指定生成的左值和右值的字符串的方式添加生成式
        """
        assert(isinstance(leftvalue, str))

        # 在文法定义的非终极符中寻找leftvalue
        gleftval = None
        for x in self.nterminals: 
            if x.token == leftvalue: 
                gleftval = x
                break
        
        assert gleftval != None, "Given leftvalue:{} not in character set of grammar".format(leftvalue)

        gright = []
        for arg in rightvalue:
            grightval = None
            for x in self.nterminals:
                if x.token == arg:
                    grightval = x
                    break
            
            if grightval is None:
                for x in self.terminals:
                    if x.token == arg:
                        grightval = x
                        break

            assert grightval is not None, "Given rightvalue:{} not in character set of grammar".format(arg)
            gright.append(grightval)

        self.generators.append(Generator(gleftval, gright))


def createRegularGrammar():
    """ Give an example of Regular Grammar
    """
    A = Symbol("A",False)
    B = Symbol("B",False)
    a = Symbol("a")
    b = Symbol("b")

    terminals = [a,b]
    nonterminals = [A,B]

    rg = RegularGrammar(terminals, nonterminals)

    rg.add_generator_str("A","a")
    rg.add_generator_str("B","b","A")
    rg.add_generator_str("A","a","B")

    return rg


def recognizeRegularString(rg, detected_string):
    """ 识别给定的字符串是否属于正则文法的语言(是否可以被识别)

    Args:
        rg (RegularGrammar) 正则文法
        detected_string (str) 待识别字符串
    """

    assert(isinstance(rg, RegularGrammar))
    assert(isinstance(detected_string, str))

    # check if all character in detected string in character set of grammar.
    for c in detected_string:
        if c in rg._terminals_tokens:
            continue
        if c in rg._nterminals_tokens:
            continue
        return False

    v = []
    end = detected_string[-1]

    # find generator of grammar which can generate the last symbol of detected string
    for gen in rg.generators:
        cangen = gen.reverseProduce(end)
        if(cangen is None):
            continue
        v.append(cangen)

    i = len(detected_string) - 2
    while i >= 0:
        cthis = detected_string[i]

        s = copy.deepcopy(v)

        while len(s) > 0 :
            nts = s[0]
            s.pop(0)
            v.pop(0)
            
            for gen in rg.generators:
                cangen = gen.reverseProduce(cthis, nts)
                if cangen is None:
                    continue
                v.append(cangen)
                
        i = i - 1

    return len(v) != 0


class NoContextGrammar:
    """ 满足乔姆斯基范式的上下文无关语法类
    """
    def __init__(self, terminals, nterminals, start_symbol = "S"):
        assert isinstance(terminals, (list, tuple)) , "Terminals should be a list or tuple"
        assert isinstance(nterminals, (list, tuple)) , "Non terminals should be a list or tuple"

        self.terminals = terminals
        self.nterminals = nterminals
        self.generators = []
        self.starter = Symbol(start_symbol, False)


    def _findTerminal(self, ts):

        for x in self.terminals:
            if x.token == ts:
                return x

        return None
 
    def _findNTerminal(self, nts):

        for x in self.nterminals:
            if x.token == nts:
                return x

        if self.starter.token == nts:
            return self.starter

        return None

    def add_generator(self, gen):

        assert(isinstance(gen, Generator))

        # 检查需要添加的生成式的所有字符是否在字符集内
        assert gen.leftvalue in self.terminals or gen.leftvalue == self.starter,\
             "Left value of generator not in non-terminal sets"

        for val in gen.rightvalue:
            assert val in self.terminals or val in self.nterminals , \
                "Right value of generator not in symbol sets"


    def add_generator_str(self, leftvalue, *rightvalue):

        assert isinstance(leftvalue, str), "Leftvalue must be type of str"

        sleftval = self._findNTerminal(leftvalue)
        assert sleftval is not None, "leftvalue:{} not found in non-terminal sets".format(leftvalue)

        sright = []
        for arg in rightvalue:
            srightval = None
            srightval = self._findNTerminal(arg)
            if srightval is None:
                srightval = self._findTerminal(arg) 
            assert srightval is not None, "rightvalue:{} not found in symbol sets".format(arg)
            sright.append(srightval)

        self.generators.append(Generator(sleftval, sright))

    def find_producable_nts(self, *arg):

        gens = set([])
        for gen in self.generators:
            cangen = gen.reverseProduce(*arg)
            if cangen is None:
                continue
            gens.add(cangen)

        return list(gens)


def createNoContextGrammar():

    terminals = []
    nonterminals = []
    
    for nts in ["A","B","C"]:
        nonterminals.append(Symbol(nts, False))

    for ts in ["a","b"]:
        terminals.append(Symbol(ts))

    nrg = NoContextGrammar(terminals, nonterminals, start_symbol="S")

    nrg.add_generator_str("S","A","B")
    nrg.add_generator_str("B","C","C")
    nrg.add_generator_str("C","A","B")
    nrg.add_generator_str("A","B","A")
    nrg.add_generator_str("S","B","C")
    nrg.add_generator_str("B","b")
    nrg.add_generator_str("C","a")
    nrg.add_generator_str("A","a")

    return nrg


def recognizeNoContextString(nrg, detected_string):
    """ 识别给定的字符串是否是给定的满足乔姆斯基范式的上下文无关文法的语言

    Args:
        nrg (NoContextGrammar) 满足乔姆斯基范式的上下文无关文法
        detected_string (str) 待识别的字符串
    """

    # DP 的 思想

    length = len(detected_string)

    res = [ [[] for i in range(length)] for i in range(length) ]

    for interval in range(length):
        for start in range(length - interval):
            
            substr = detected_string[start:start + interval + 1]
            if interval == 0:
                # directly find
                gens = nrg.find_producable_nts(substr)
                res[start][interval] = gens

            else:
                rlen = interval + 1
                # find split
                genss = set([])
                for splitpoint in range(1, rlen):
                    left = res[start][splitpoint - 1]
                    right = res[start + splitpoint][rlen - splitpoint - 1]

                    for front, back in product(left, right):
                        gens = nrg.find_producable_nts(front, back)
                        if len(gens) > 0:
                            for getnts in gens:
                                genss.add(getnts)

                res[start][interval] = genss


    for i in range(length):
        for j in range(length):
            print("".join([x.token for x in res[i][j]]), end ="\t")
        print()

    for getnts in res[0][length-1]:
        if getnts.token == nrg.starter.token:
            return True

    return False


if __name__ == "__main__":
    """    
    rg = createRegularGrammar()
    s = "ababababa"
    print("{} is recognizable:{}".format(s, recognizeRegularString(rg, s)))
    """

    nrg = createNoContextGrammar()
    s = "baababaab"
    able = recognizeNoContextString(nrg, s)
    print("{} is recognizable:{}".format(s, able))