from striplog import Lexicon, Legend
from utils.lexicon.lexicon_memoris import LEX_LITHO_MEMORIS, LEX_POL_MEMORIS, LEG_LITHO_MEMORIS

# DEFAULT PROPERTIES VALUES
DEFAULT_BOREHOLE_LENGTH = 0.1
DEFAULT_BOREHOLE_DIAMETER = 0.1
DEFAULT_ATTRIB_VALUE = 'Inconnu'
NOT_EXIST = 'not_exist'
WORDS_WITH_S = ['Gneiss', 'Silex', 'VS', 'vs']
SAMP_TYPE_KW = ['soil', 'water', 'sol', 'eau', 'inconnu']

DEFAULT_LITHO_LEXICON = Lexicon(LEX_LITHO_MEMORIS)  # or Lexicon.default()
DEFAULT_LITHO_LEGEND = Legend.from_csv(text=LEG_LITHO_MEMORIS)

DEFAULT_POL_LEXICON = Lexicon(LEX_POL_MEMORIS)
DEFAULT_CONTAM_LEVELS = ['VR', 'VS', 'VI', 'Inconnu']

# TEXT COLOR PROPERTIES : "\033[text_style; text_color; text_background_color m"
# visit https://ozzmaker.com/add-colour-to-text-in-python/
WARNING_TEXT_CONFIG = {
    'white':    "\033[1;37m",
    'yellow':   "\033[1;33m",
    'green':    "\033[1;32m",
    'blue':     "\033[1;34m",
    'cyan':     "\033[1;36m",
    'red':      "\033[1;31m",
    'magenta':  "\033[1;35m",
    'black':      "\033[1;30m",
    'darkwhite':  "\033[0;37m",
    'darkyellow': "\033[0;33m",
    'darkgreen':  "\033[0;32m",
    'darkblue':   "\033[0;34m",
    'darkcyan':   "\033[0;36m",
    'darkred':    "\033[0;31m",
    'darkmagenta':"\033[0;35m",
    'darkblack':  "\033[0;30m",
    'off':        "\033[0;0m",
    'bold':       "\033[1m",
    'warning':    "\033[93m"
}
