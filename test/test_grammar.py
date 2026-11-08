import sys
import unittest
sys.path.append('./')
from iheartla.la_grammar.LA_ebnf import LA
import tatsu

class GrammarTest(unittest.TestCase):
    def testGrammar(self):
        try:
            model = tatsu.compile(LA)
        except Exception as e:
            self.fail("Unexpected exception %s" % e)

        assert True

        try:
            ast = model.parse('''Proof: Induction(n)
\tIH:
\t\tsum_(i for i <= $n) i = $n($n+1)/2

\tBase: n=1
\t\tsum_(i for i <= 1) 1 = 1 = 1⋅(2)/2

\tIS: n=>n+1
\t\tsum_(i for i <= $s) i = $IHh + $s = $IHc + $s = $n($n+1)/2 + $s⋅2/2 = $s($n + 2)/2 = frac{($s)⋅($n + 1 + 1)}{2}
        ''') # , trace=True) Activate for debug
        except Exception as e:
            self.fail("Unexpected exception %s" % e)

        print(ast)
