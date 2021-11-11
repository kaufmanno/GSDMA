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

# i put it here to facilitate processing but must be removed and kept in the notebook
# it used to rename pollutants columns in dataframe
pol_field_model = {'Arsenic': 'As', 'Cobalt':'Co', 'Cadmium': 'Cd', 'Chrome': 'Cr', 'Chrome VI': 'Cr_VI', 'Cuivre': 'Cu', 'Mercure': 'Hg', 'Plomb': 'Pb', 'Nickel': 'Ni', 'Zinc': 'Zn', 'Cyanure(?:s)? (?libre(?:s)?)?': 'CN_libre', 'Cyanures (totaux)': 'CN_tot','Cyanure (totaux)': 'CN_tot', 'CN_totaux':'CN_tot','Cyanures (APE)': 'CN_APE', 'cyanure (totaux)':'CN_tot', 'cyanure (APE)':'CN_APE', 'cyanure complex': 'CN_cplx','Cyanure (APE)': 'CN_APE', "Cyanures (libres) - NEN-EN-ISO 14403": 'CN_libre', 'Cyanures (libres)':'CN_libre', 'thiocyanate': 'thioCN', 'Benzène': 'Bnz', 'Toluène': 'Toln', 'Éthylbenzène': 'EthylBnz', 'Orthoxylène': 'O-Xyl', 'Para- et métaxylène': 'P-M-Xyl', 'Xylènes': 'Xyl', 'Styrène': 'Styr', 'BTEX totaux': 'BTEX_tot', 'Phénol': 'Phenol', 'Indice phénol': 'Idc_Phenol', 'Naphtalène': 'Naphta', 'Acénaphtylène': 'Acenaphtyl', 'Acénaphtène': 'Acenaphtn', 'Fluorène': 'Fluorene', 'Phénanthrène': 'Phenanthr', 'Anthracène': 'Anthrc', 'Fluoranthène': 'Flranth', 'Pyrène': 'Pyr', 'Benzo(a)anthracène': 'Bnz(a)anthrc', 'Chrysène': 'Chrys', 'Benzo(b)fluoranthène': 'Bnz(b)flranth', 'Benzo(k)fluoranthène': 'Bnz(k)flranth', 'Benzo(a)pyrène': 'Bnz(a)pyr','Dibenzo(ah)anthracène': 'Dibnz(ah)anthrc', 'Benzo(ghi)pérylène': 'Bnz(ghi)peryl', 'Indéno(1,2,3-cd)pyrène': 'Indeno(1.2.3-cd)pyr', 'HAP Totaux (16) - EPA': 'HAP_tot_EPA', '1.1-Dichloroéthane': '1.1-DCE', '1.2-Dichloroéthane': '1.2-DCE', '1.1-dichloroéthène': '1.1-DCEn', 'Cis-1.2-dichloroéthène': 'Cis-1.2-DCEn', 'Trans 1.2-dichloroéthylène': 'Trans 1,2-DCEyl', 'Dichlorométhane': 'DCM', 'Totaux (cis,trans) 1,2-dichloroéthènes': '(cis,trans) 1,2-DCE_tot', '1,2-dichloropropane': '1,2-DCP', 'Tétrachloroéthylène': 'TetraCEyn', 'Tétrachlorométhane': 'TCM', '1,1,1-Trichloroéthane': '1.1.1-TCE', '1,1,2-Trichloroéthane': '1.1.2-TCE', 'Trichloroéthylène': 'TCEyn', 'Chloroforme': 'Chloroforme', 'Chlorure de vinyle': 'CVinyl', 'EOX': 'EOX', 'fraction aromat. >C6-C7': 'Arom_C6-C7', 'fraction aromat. >C7-C8': 'Arom_C7-C8', 'fraction aromat. >C8-C10': 'Arom_C8-C10', 'fraction aliphat. C5-C6': 'Aliphat_C5-C6', 'fraction aliphat. >C6-C8': 'Aliphat_C6-C8', 'fraction aliphat. >C8-C10': 'Aliphat_C8-C10', 'Fraction C5-C8': 'C5-C8', 'Fraction C8-C10': 'C8-C10', 'Fraction C10-C12': 'C10-C12', 'Fraction C12-C16': 'C12-C16', 'Fraction C16-C21': 'C16-C21', 'Fraction C21 - C35': 'C21-C35', 'Fraction C35 - C40': 'C35-C40', 'Hydrocarbures totaux C10-C35': 'HC_tot_C10-C35','totaux C10-C35':'HC_tot_C10-C35', 'Totaux C10-C40':'HC_tot_C10-C40', 'Hydrocarbures totaux C10-C40':'HC_tot_C10-C40', 'MTBE': 'MTBE', 'PCB 28': 'PCB_28', 'PCB 52': 'PCB_52', 'PCB 101': 'PCB_101', 'PCB 118': 'PCB_118', 'PCB 138': 'PCB_138', 'PCB 153': 'PCB_153', 'PCB 180': 'PCB_180', 'PCB totaux (7)?': 'PCB_tot', 'Chlorure(?:s)?': 'Chlorure', 'Soufre Total': 'S_tot', 'sulfite(?:s)?': 'sulfite', 'sulfate(?:s)?': 'sulfate', 'COT':'COT','DBO (5 jours)':'DBO_5j','DCO':'DCO', 'Ammonium':'NH4','ammoniaque libre':'NH3_libre','Nitrate':'HNO3', 'Nitrite':'HNO2','azote Kjeldahl':'N_Kjdl','sulfures totaux':'Sulfure_tot', 'sulfure(?:s)? (libre(?:s)?)':'Sulfure_libre','calcium':'Ca','potassium':'K', 'magnésium':'Mg', 'manganèse':'Mn', 'sodium':"Na", 'fer':'Fe','phosphore (total)':'P_tot','carbonate':'CaCO3', 'bicarbonate':'Bicarb','Phoshore':'P', 'fer ((Fe))? total':'Fe_tot', 'fer (2\+)':'Fe2','fluorure(?:s)?':'Fluorure','bromure (libre)': 'Br_libre'}