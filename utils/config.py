from striplog import Lexicon, Legend
import numpy as np
from utils.lexicon_memoris import LEX_LITHO_MEMORIS, LEX_POL_MEMORIS, LEG_LITHO_MEMORIS, LEG_BOREHOLE
from utils.lexicon_memoris import LEX_BOREHOLE_MEMORIS, LEG_CONTAMINATION_LEV

# DEFAULT PROPERTIES VALUES
DEFAULT_BOREHOLE_LENGTH = 0.1
DEFAULT_BOREHOLE_DIAMETER = 0.1
DEFAULT_BOREHOLE_TYPE = 'Forage'
DEFAULT_Z = 102.0
# DEFAULT_ATTRIB_VALUE = 'Inconnu'
WORDS_WITH_S = ['Gneiss', 'Silex', 'VS', 'vs']
SAMP_TYPE_KW = ['soil', 'water', 'sol', 'eau', 'inconnu']

DEFAULT_LITHO_LEXICON = Lexicon(LEX_LITHO_MEMORIS)  # or Lexicon.default()
DEFAULT_LITHO_LEGEND = Legend.from_csv(text=LEG_LITHO_MEMORIS)
DEFAULT_BOREHOLE_LEGEND = Legend.from_csv(text=LEG_BOREHOLE)
DEFAULT_BOREHOLE_LEXICON = Lexicon(LEX_BOREHOLE_MEMORIS)
DEFAULT_POL_LEGEND = Legend.from_csv(text=LEG_CONTAMINATION_LEV)
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

# it used to rename pollutants columns in dataframe
POL_NAMES_MODEL = {'Arsenic': 'As', 'Cobalt': 'Co', 'Cadmium': 'Cd', 'Chrome': 'Cr', 'Chrome VI': 'Cr_VI', 'Chrome (VI)': 'Cr_VI', 'Chrome_total': 'Cr_tot', 'Cuivre': 'Cu', 'Mercure': 'Hg', 'Plomb': 'Pb', 'Nickel': 'Ni', 'Zinc': 'Zn', 'Cyanure(?:s)? (?libre(?:s)?)?': 'CN_libre', 'Cyanures (totaux)': 'CN_tot', 'CN_totaux': 'CN_tot', 'Cyanures (APE)': 'CN_tot_APE', 'Cyanures totaux APE':'CN_tot_APE', 'cyanure complex': 'CN_cplx', "Cyanures (libres) - NEN-EN-ISO 14403": 'CN_libre', 'Cyanures (libres)': 'CN_libre', 'CN_libres': 'CN_libre', 'thiocyanate': 'ThioCN', 'Benzène': 'Bnz', 'Toluène': 'Toln', 'Éthylbenzène': 'EthBnz', 'Orthoxylène': 'O-Xyl', 'O-xylènes': 'O-Xyl', 'mp-xylènes': 'P-M-Xyl', 'Para- et métaxylène': 'P-M-Xyl', 'Xylènes': 'Xyl', 'Styrène': 'Styr', 'BTEX totaux': 'BTEX_tot', 'Phénol': 'Phenol', 'Indice phénol': 'IPh', 'Naphtalène': 'Naphta', 'Acénaphtylène': 'Acenaphtyl', 'Acénaphtène': 'Acenaphtn', 'Fluorène': 'Flrn', 'Phénanthrène': 'Phenanthr', 'Anthracène': 'Anthrc', 'Fluoranthène': 'Flranth', 'Pyrène': 'Pyr', 'Benzo(a)anthracène': 'Bnz(a)anthrc', 'Chrysène': 'Chrys', 'Benzo(b)fluoranthène': 'Bnz(b)flranth', 'Benzo(k)fluoranthène': 'Bnz(k)flranth', 'Benzo(a)pyrène': 'Bnz(a)pyr', 'Dibenzo(ah)anthracène': 'Dibnz(ah)anthrc', 'Benzo(ghi)pérylène': 'Bnz(ghi)peryl', 'Indéno(1,2,3-cd)pyrène': 'Indeno(1.2.3-cd)pyr', 'HAP Totaux (16) - EPA': 'HAP_tot_EPA', '1,1-Dichloroéthane': '1.1-DCE', '1,2-Dichloroéthane': '1.2-DCE', '1,1-dichloroéthène': '1.1-DCEn', 'Cis-1,2-dichloroéthène': 'Cis-1.2-DCEn', 'Trans 1,2-dichloroéthylène': 'Trans-1.2-DCEyl', 'Dichlorométhane': 'DCM', 'dibromochlorométhane': 'DiBCM', 'bromodichlorométhane': 'BromoDCM', 'Totaux (cis,trans) 1,2-dichloroéthènes': '(cis.trans)-1.2-DCEn_tot', '1,2-dichloropropane': '1.2-DCP', 'Tétrachloroéthylène': 'TetraCEyn', 'Tétrachlorométhane': 'TCM', '1,1,1-Trichloroéthane': '1.1.1-TCE', '1,1,2-Trichloroéthane': '1.1.2-TCE', 'Trichloroéthylène': 'TCEyn', 'Chlorure de vinyle': 'CVinyl', '3-éthylphénol': '3-EthPhn', 'métacrésol': 'M-cresol', 'o-crésol': 'O-cresol', 'p-crésol': 'P-cresol', 'crésols (total)': 'Cresol_tot', '2,4-dimethylphénol': '2.4-DMetPhn', '2,5-dimethylphénol': '2.5-DMetPhn', '3,5+2,3-dimethylphénol+4-ethylphénol': 'DMetPhn_4-EthPhn', '2,6-dimethylphénol': '2.6-DMetPhn', '3,4-dimethylphénol': '3.4-DMetPhn', 'alkylphénols C2 total': 'AlkPhn_C2_tot', '2-éthylphénol': '2-EthPhn', 'para(tert)butylphénol': 'P(T)ButPhn', 'alkylphénols C4 total': 'AlkPhn_C4_tot', '2,3,5-triméthylphénol': '2.3.5-TMPethn', '3,4,5-triméthylphénol': '3.4.5-TMetPhn', '2-isopropylphénol': '2-IsoPropPhn', 'alkylphénols C3 total': 'AlkPhn_C3_tot', 'HAP totaux (10) VROM': 'HAP_tot_vrom', 'monochlorobenzène': 'MonoCBzn', '1,2-dichlorobenzène': '1.2-DCBzn', '1,3-dichlorobenzène': '1.3-DCBzn', '1,4-Dichlorobenzène': '1.4-DCBzn', '1,2,3-trichlorobenzène': '1.2.3-TCBzn', '1,2,4-trichlorobenzène': '1.2.4-TCBzn', '1,3,5-trichlorobenzène': '1.3.5-TCBzn', '1,2,4,5- et 1,2,3,5-tétrachlorobenzènes': '1.2.3.4_5-TCBzn', '1,2,3,4-tétrachlorobenzène': '1.2.3.4-TCBzn', 'hexachlorobenzène': 'HCBzn', '2-chlorophénol': '2-CPhn', '4-chlorophénol': '4-CPhn', '3-chlorophénol': '3-CPhn', 'monochlorophénol total': 'MonoCPhn_tot', '2,3-dichlorophénol': '2.3-DCPhn', '2,4+2,5-dichlorophénol': '2.4_5-DCPhn', '2,6-dichlorophénol': '2.6-DCPhn', '3,4-dichlorophénol': '3.4-DCPhn', '3,5-dichlorophénol': '3.5-DCPhn', 'dichlorophénol total': 'DCPhn_tot', '2,3,4-trichlorophénol': '2.3.4-TCPhn', '2,3,5-trichlorophénol': '2.3.5-TCPhn', '2,3,6-trichlorophénol': '2.3.6-TCPhn', '2,4,5-trichlorophénol': '2.4.5-TCPhn', '2,4,6-trichlorophénol': '2.4.6-TCPhn', '3,4,5-trichlorophénol': '3.4.5-TCPhn', 'trichlorophénol total': 'TriCPhn_tot', '2,3,5,6-tétrachlorophénol': '2.3.5.6-TCPhn', '2,3,4,6- tétrachlorophénol': '2.3.4.6-TCPhn', '2,3,4,5- tétrachlorophénol': '2.3.4.5-TCPhn', 'tétrachlorophénol total': 'TCPhn_tot', 'pentachlorobenzène': 'PCBzn', 'pentachlorophénol': 'PCPhn', 'chlorophénol total': 'CPhn_tot', 'EOX': 'EOX', 'fraction aromat. >C6-C7': 'Ar_C6-C7', 'fraction aromat. >C7-C8': 'Ar_C7-C8', 'fraction aromat. >C8-C10': 'Ar_C8-C10', 'fraction aliphat. C5-C6': 'Alp_C5-C6', 'fraction aliphat. >C6-C8': 'Alp_C6-C8', 'fraction aliphat. >C8-C10': 'Alp_C8-C10', 'Fraction C5-C8': 'C5-C8', 'Fraction C8-C10': 'C8-C10', 'Fraction C10-C12': 'C10-C12', 'Fraction C12-C16': 'C12-C16', 'Fraction C16-C21': 'C16-C21', 'Fraction C21 - C35': 'C21-C35', 'Fraction C35 - C40': 'C35-C40', 'C16 - C21': 'C16-C21', 'C21 - C35': 'C21-C35', 'C30 - C40': 'C30-C40', 'C35 - C40': 'C35-C40', 'aromat.>C6-C7': 'Ar_C6-C7', 'aromat.>C7-C8': 'Ar_C7-C8', 'aromat.>C8-C10': 'Ar_C8-C10', 'aromat.>C10-C12': 'Ar_C10-C12', 'aromat.>C12-C16': 'Ar_C12-C16', 'aromat.>C16-C21': 'Ar_C16-C21', 'aromat.>C21-C35': 'Ar_C21-C35', 'aliphat.>C5-C6': 'Alp_C5-C6', 'aliphat.>C6-C8': 'Alp_C6-C8', 'aliphat.>C8-C10': 'Alp_C8-C10', 'aliphat.>C10-C12': 'Alp_C10-C12', 'aliphat.>C12-C16': 'Alp_C12-C16', 'aliphat.>C16-C35': 'Alp_C16-C35', 'Hydrocarbures totaux C10-C35': 'HC_tot_C10-C35', 'totaux C10-C35': 'HC_tot_C10-C35', 'Totaux C10-C40': 'HC_tot_C10-C40', 'Hydrocarbures totaux C10-C40': 'HC_tot_C10-C40', 'MTBE': 'MTBE', 'PCB 28': 'PCB_28', 'PCB 52': 'PCB_52', 'PCB 101': 'PCB_101', 'PCB 118': 'PCB_118', 'PCB 138': 'PCB_138', 'PCB 153': 'PCB_153', 'PCB 180': 'PCB_180', 'PCB totaux (7)?': 'PCB_tot', 'Chlorure(?:s)?': 'Chlorure', 'Soufre Total': 'S_tot', 'sulfite(?:s)?': 'sulfite', 'sulfate(?:s)?': 'sulfate', 'COT': 'COT', 'DBO (5 jours)': 'DBO_5j', 'DCO': 'DCO', 'Ammonium': 'NH4', 'ammoniaque libre': 'NH3_libre', 'Nitrate': 'HNO3', 'Nitrite': 'HNO2', 'azote Kjeldahl': 'N_Kjdl', 'sulfures totaux': 'Sulfure_tot', 'sulfure(?:s)? (libre(?:s)?)': 'Sulfure_libre', 'calcium': 'Ca', 'potassium': 'K', 'magnésium': 'Mg', 'manganèse': 'Mn', 'sodium': "Na", 'fer': 'Fe', 'phosphore (total)': 'P_tot', 'phosphates (totaux)': 'Phosphate_tot', 'carbonate': 'CaCO3', 'bicarbonate': 'Bicarb', 'fer ((Fe))? total': 'Fe_tot', 'fer (2+)': 'Fe2', 'fluorure(?:s)?': 'Fluorure', 'chlorures': 'Chlorure', 'chloroformes': 'Chloroforme', 'bromoformes': 'Bromoforme', 'bromure (libre)': 'Br_libre', 'Iph.': 'IPh', 'CN_NCl': 'CN_NCl', '2-naphtol': '2-Naphtol', 'thymol': 'Thymol', 'chloroforme': 'Chloroforme', 'bromoforme': 'Bromoforme', 'C12-C20': 'C12-C20', 'C20-C30': 'C20-C30', 'Non chloro destruct.':'Non_chloro_destr', 'SOM VROM 10':'HAP_tot_vrom','SOM EPA 16':'HAP_tot_EPA', 'SOM_C5_C35':'HC_tot_C15-C35', 'SOM_C10_C40':'HC_tot_C10-C40', 'SOM BTEX':'BTEX_tot','C5_C8':'C5-C8', 'C8_C10':'C8-C10', 'C10_C12':'C10-C12', 'C12_C16':'C12-C16', 'C30_C35':'C30-C35','aluminium':'Al', 'phosphore':'P'}
