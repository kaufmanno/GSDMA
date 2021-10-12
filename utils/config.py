from striplog import Lexicon, Legend
from utils.lexicon.lexicon_memoris import LEX_LITHO_MEMORIS, LEX_POL_MEMORIS, LEG_LITHO_MEMORIS

# DEFAULT PROPERTIES VALUES
DEFAULT_BOREHOLE_LENGTH = 3.
DEFAULT_BOREHOLE_DIAMETER = 0.1
DEFAULT_ATTRIB_VALUE = 'Inconnu'
DEFAULT_CONTAM_LEVELS = ['VR', 'VS', 'VI', 'Inconnu']
WORDS_WITH_S = ['Gneiss', 'Silex', 'VS', 'vs']
# COMP_TYPE_KW= ['lithology', 'pollutant', 'lithologie', 'polluant']
SAMP_TYPE_KW = ['soil', 'water', 'sol', 'eau', 'inconnu']
DEFAULT_LITHO_LEXICON = Lexicon(LEX_LITHO_MEMORIS)  # or Lexicon.default()
DEFAULT_POL_LEXICON = Lexicon(LEX_POL_MEMORIS)
DEFAULT_LITHO_LEGEND = Legend.from_csv(text=LEG_LITHO_MEMORIS)
