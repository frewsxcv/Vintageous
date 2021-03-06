from collections import namedtuple

from Vintageous.tests import ViewTest
from Vintageous.vi.utils import modes

test_data = namedtuple('test_data', 'text startRegion findChar mode expectedRegion msg')

NORMAL_CASES = (
    test_data('0a23x5', (1, 1), 'x', modes.NORMAL, (3, 3), 'Find ahead'),
    test_data('0ax345', (1, 1), 'x', modes.NORMAL, (1, 1), 'Find next'),
    test_data('0x2345', (1, 1), 'x', modes.NORMAL, (1, 1), 'Find self'),
    test_data('0a2xx5', (1, 1), 'x', modes.NORMAL, (2, 2), 'Find multiple'),
    test_data('0x2x45', (1, 1), 'x', modes.NORMAL, (2, 2), 'Find self multiple'),
)

INTERNAL_NORMAL_CASES = (
    test_data('0a23x5', (1, 1), 'x', modes.INTERNAL_NORMAL, (1, 4), 'Find ahead'),
    test_data('0ax345', (1, 1), 'x', modes.INTERNAL_NORMAL, (1, 2), 'Find next'),
    test_data('0x2345', (1, 1), 'x', modes.INTERNAL_NORMAL, (1, 1), 'Find self'),
    test_data('0a2xx5', (1, 1), 'x', modes.INTERNAL_NORMAL, (1, 3), 'Find multiple'),
    test_data('0x2x45', (1, 1), 'x', modes.INTERNAL_NORMAL, (1, 3), 'Find self multiple'),
)

VISUAL_MULTI_CHAR_CASES = (
    test_data('0ab3x5', (1, 3), 'x', modes.VISUAL, (1, 4), 'Forward'),
    test_data('0a23x5', (1, 5), 'x', modes.VISUAL, (1, 5), 'Forward find b'),
    test_data('0b2xa5', (5, 1), 'x', modes.VISUAL, (5, 2), 'Reverse no crossover'),
    test_data('0ba3x5', (3, 1), 'x', modes.VISUAL, (2, 4), 'Reverse crossover'),
    test_data('0b2x45', (4, 1), 'x', modes.VISUAL, (4, 2), 'Reverse find a'),
    test_data('0x2a45', (4, 1), 'x', modes.VISUAL, (4, 1), 'Reverse find b'),
    test_data('0a2bx5', (1, 4), 'x', modes.VISUAL, (1, 4), 'Forward find b+1'),
    test_data('0bx3a5', (5, 1), 'x', modes.VISUAL, (5, 1), 'Reverse find b+1'),
    test_data('0b2ax5', (4, 1), 'x', modes.VISUAL, (4, 3), 'Reverse find a+1'),
)

VISUAL_ONE_CHAR_CASES = (
    test_data('ax', (0, 2), 'x', modes.VISUAL, (0, 2), 'Forward find b'),
    test_data('bx', (2, 0), 'x', modes.VISUAL, (2, 0), 'Reverse find a'),
    test_data('fx', (0, 1), 'x', modes.VISUAL, (0, 1), 'Forward find next'),
    test_data('rx', (1, 0), 'x', modes.VISUAL, (1, 0), 'Reverse find next'),
    test_data('f',  (0, 1), 'f', modes.VISUAL, (0, 1), 'Forward find self'),
    test_data('r',  (1, 0), 'r', modes.VISUAL, (1, 0), 'Reverse find self'),
)

VISUAL_MULTI_MATCHES_CASES = (
    test_data('0abxx5', (1, 3), 'x', modes.VISUAL, (1, 3), 'Forward find first'),
    test_data('0axx45', (1, 3), 'x', modes.VISUAL, (1, 3), 'Forward find b'),
    test_data('0bxx45', (3, 1), 'x', modes.VISUAL, (3, 1), 'Reverse find a'),
    test_data('0bxx45', (4, 1), 'x', modes.VISUAL, (4, 1), 'Reverse find a'),
    test_data('0xax45', (3, 1), 'x', modes.VISUAL, (3, 2), 'Reverse find b'),
)

VISUAL_MULTI_LINE_CASES = (
    test_data('012\n456',   (0, 5), '2', modes.VISUAL, (0, 5), 'Select L1->L2, find on L1'),
    test_data('012\n456',   (0, 5), '6', modes.VISUAL, (0, 6), 'Select L1->L2, find on L2'),
    test_data('012\n456',   (0, 4), '2', modes.VISUAL, (0, 4), 'Select L1->LF, find on L1'),
    test_data('012\n456',   (0, 4), '6', modes.VISUAL, (0, 4), 'Select L1->LF, find on L2'),
    test_data('012\n456',   (5, 0), '2', modes.VISUAL, (5, 1), 'Select L2->L1, find on L1'),
    test_data('012\n456',   (5, 0), '6', modes.VISUAL, (5, 0), 'Select L2->L1, find on L2'),
    test_data('012\n456',   (5, 3), '2', modes.VISUAL, (5, 3), 'Select L2->LF, find on L1'),
    test_data('012\n456',   (5, 3), '6', modes.VISUAL, (5, 3), 'Select L2->LF, find on L2'),
    test_data('0123\n5678', (7, 5), '8', modes.VISUAL, (6, 8), 'Select L2->LF+1, find on L2'),
)

class Test_vi_t(ViewTest):
    def runTests(self, data):
        for (i, data) in enumerate(data):
            self.write(data.text)
            self.clear_sel()
            self.add_sel(self.R(*data.startRegion))
            self.view.run_command('_vi_find_in_line',
                {'mode': data.mode, 'count': 1, 'char': data.findChar, 'inclusive': False})
            self.assert_equal_regions(self.R(*data.expectedRegion), self.first_sel(),
                "Failed on index {} {} : Text:\"{}\" Region:{} Find:'{}'"
                    .format(i, data.msg, data.text, data.startRegion, data.findChar))

    def testNormalCases(self):
        self.runTests(NORMAL_CASES)

    def testInternalNormalCases(self):
        self.runTests(INTERNAL_NORMAL_CASES)

    def testVisualMultipleCharacterCases(self):
        self.runTests(VISUAL_MULTI_CHAR_CASES)

    def testVisualSingleCharacterCases(self):
        self.runTests(VISUAL_ONE_CHAR_CASES)

    def testVisualMultipleMatchesCases(self):
        self.runTests(VISUAL_MULTI_MATCHES_CASES)

    def testVisualMultipleLinesCases(self):
        self.runTests(VISUAL_MULTI_LINE_CASES)
