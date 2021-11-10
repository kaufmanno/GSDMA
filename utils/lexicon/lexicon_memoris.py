"""
Definition de mots clés pour les descriptions de cuttings de forages.
:copyright: 2021  Y. N'DEPO & O. Kaufmann 
"""

import numpy as np

# ==================== LEXIQUES ================================
# lithologies lexicon
LEX_LITHO_MEMORIS = {'lithology': ['Not_exist', 'Remblai(?:s)?', 'Alluvion(?:s)?', 'Boue(?:s)?', 'Laitier', 'B[e|é]ton', 'Scorie(?:s)?', 'Ballast(?:s)?', 'Briquaille(?:s)?', 'Caillasse(?:s)?', 'Anthracite(?:s)?', 'Porphyre(?:s)?', 'Houille(?:s)?', 'Diorite(?:s)?', 'Cargneule(?:s)?', 'Molasse(?:s)?', 'Jaspe(?:s)?', 'Gravier(?:s)?', 'Leptynite(?:s)?', 'Pyroxénite(?:s)?', 'Pierre coquillière(?:s)?', 'Grès(?:s)?', 'Obsidienne(?:s)?', 'Basalte(?:s)?', 'Charbon(?:s)?', 'Anhydrite(?:s)?', 'Andésite(?:s)?', 'Ardoise(?:s)?', 'Carbonatite(?:s)?', 'Dolérite(?:s)?', 'Cendres(?:s)?', 'Poudingue(?:s)?', 'Alios(?:s)?', 'Quartzite(?:s)?', 'Calcaire(?:s)?', 'Gypse(?:s)?', 'Limon(?:s)?', 'Phonolite(?:s)?', 'Arkose(?:s)?', 'Pegmatite(?:s)?', 'Bauxite(?:s)?', 'Pierre coquillère(?:s)?', 'Gneiss', 'Mort-terrain(?:s)?', 'Silcrète(?:s)?', 'Lignite(?:s)?', 'Conglomérat(?:s)?', 'Glauconie(?:s)?', 'Ponce(?:s)?', 'Péridotite(?:s)?', 'Combarbalite(?:s)?', 'Glauconite(?:s)?', 'Anatexite(?:s)?', 'Amphibolite(?:s)?', 'Greisen(?:s)?', 'Tuffeau(?:s)?', 'Granite(?:s)?', 'Gr(?:è|e|é)s', 'Brèche(?:s)?', 'Dolomie(?:s)?', 'Tuf volcanique(?:s)?', 'Halite(?:s)?', "Granite d'anatexie(?:s)?", 'Ignimbrite(?:s)?', 'Bentonite(?:s)?', 'Monzonite(?:s)?', 'Rhyolite(?:s)?', 'Monazite(?:s)?', 'Silex', 'Gabbro(?:s)?', 'Argile(?:s)?', 'Syénite(?:s)?', 'Kimberlite(?:s)?', 'Cendre(?:s)?', 'Cinérite(?:s)?', 'Tourbe(?:s)?', 'Aplite(?:s)?', 'Grè(?:s)?', 'Marne(?:s)?', 'Dacite(?:s)?', 'Micaschiste(?:s)?', 'Molasse (?:s)?', 'Tillite(?:s)?', 'Schiste(?:s)?', 'Granodiorite(?:s)?', 'Phtanite(?:s)?', 'Tuf(?:s)?', 'Sable(?:s)?', 'Trachyte(?:s)?',  'Marbre(?:s)?', 'Ophite(?:s)?', 'Éclogite(?:s)?', 'Cipolin(?:s)?', 'Kersantite(?:s)?', 'Lapillis(?:s)?', 'Diatomite(?:s)?', 'Craie(?:s)?'],

                   'synonyms': {'mort-terrain': ['terre'], 'Anhydrite': ['Gypse'], 'Sel': ['Halite', 'Sylvite']},

                   'splitters': [' et ', ' avec ', ' de ', ' cont(?:ient|enant) ', '\\. '],

                   'parts_of_speech': {'noun': ['lithology'], 'adjective': ['colour', 'grainsize', 'modifier'], 'subordinate': ['quantity']},

                   'abbreviations': {'Argilo':'Argile', 'Sablo':'sable'},
                     }

# pollutants lexicon
LEX_POL_MEMORIS = {'pollutants': ['arsenic', 'cadmium', 'chrome', 'chrome vi', 'cuivre', 'mercure', 'plomb', 'nickel', 'zinc', 'cyanure (libre)', 'cyanure (totaux)', 'cyanure (ape)', 'cyanure complex', 'thiocyanate', 'benzène', 'toluène', 'éthylbenzène', 'orthoxylène', 'para- et métaxylène', 'xylènes', 'styrène', 'btex totaux', 'phénol', 'indice phénol', 'naphtalène', 'acénaphtylène', 'acénaphtène', 'fluorène', 'phénanthrène', 'anthracène', 'fluoranthène', 'pyrène', 'benzo(a)anthracène', 'chrysène', 'benzo(b)fluoranthène', 'benzo(k)fluoranthène', 'benzo(a)pyrène', 'dibenzo(ah)anthracène', 'benzo(ghi)pérylène', 'indéno(1,2,3-cd)pyrène', 'hap totaux (16) - epa', '1,1-dichloroéthane', '1,2-dichloroéthane', '1,1-dichloroéthène', 'cis-1,2-dichloroéthène', 'trans 1,2-dichloroéthylène', 'dichlorométhane', 'totaux (cis,trans) 1,2-dichloroéthènes', '1,2-dichloropropane', 'tétrachloroéthylène', 'tétrachlorométhane', '1,1,1-trichloroéthane', '1,1,2-trichloroéthane', 'trichloroéthylène', 'chloroforme', 'chlorure de vinyle', 'eox (****)', 'fraction aromat. >c6-c7', 'fraction aromat. >c7-c8', 'fraction aromat. >c8-c10', 'fraction aliphat. c5-c6', 'fraction aliphat. >c6-c8', 'fraction aliphat. >c8-c10', 'fraction c5 - c8', 'fraction c8 - c10', 'fraction c10-c12', 'fraction c12-c16', 'fraction c16 - c21', 'fraction c21 - c35', 'fraction c35 - c40', 'hydrocarbures totaux c10-c35', 'hydrocarbures totaux c10-c40', 'mtbe', 'pcb 28', 'pcb 52', 'pcb 101', 'pcb 118', 'pcb 138', 'pcb 153', 'pcb 180', 'pcb totaux (7)', 'chlorures', 'soufre total', 'sulfites', 'sulfate', 'chrome total', 'cobalt', 'benzene', 'toluene', 'ethylbenzene', 'xylene sum', 'styrene', 'phenol', 'naphtalene', 'acenaphtylene', 'acenaphtene', 'fluorene', 'phenanthrene', 'anthracene', 'fluoranthene', 'pyrene', 'benzo(a)anthracene', 'chrysene', 'benzo(b)fluoranthene', 'benzo(k)fluoranthene', 'benzo(a)pyrene', 'dibenzo(ah)anthracene', 'benzo(ghi)perylene', 'indeno(1.2.3-cd)pyrene', '1.1-dichloroethane', '1.2-dichloroethane', 'cis 1.2 dichloroethene', 'trans 1.2 dichloroethene', 'dichloromethane', '1.2 dichloroethene sum', '1.2-dichloropropane', 'tetrachloroethene', 'tetrachloromethane', '1.1.1-trichloroethane', '1.1.2-trichloroethane', 'trichloroethene', 'trichloromethane (chloroforme)', 'chlorure de vinyle (chloroethene)', 'cyanures libres', 'methyl-tert-butyl-ether', 'fraction 5-8', 'fraction ec 8-10', 'fraction ec 10-12', 'fraction ec 12-16', 'fraction ec 16-21', 'fraction ec 21-35'],
                      # 'levels': ['<VR', '<VS', '<VI', '>VI', 'Inconnu'],
                      'levels': ['VR', 'VS', 'VI', 'VI_', 'Inconnu'],
                      'units': ['mg/l', 'µg/l', 'mg/kg MS'],
                      'abbreviations': {'As': 'arsenic', 'Cd': 'cadmium', 'Cr': 'chrome', 'Cr_VI': 'chrome vi', 'Cu': 'cuivre', 'Hg': 'mercure', 'Pb': 'plomb', 'Ni': 'nickel', 'Zn': 'zinc', 'CN_libre': 'cyanure (libre)', 'CN_tot': 'cyanure (totaux)', 'CN_APE': 'cyanure (ape)', 'CN_cplx': 'cyanure complex', 'thioCN': 'thiocyanate', 'Bnz': 'benzène', 'Toln': 'toluène', 'EthylBnz': 'éthylbenzène', 'O-Xyl': 'orthoxylène', 'P-M-Xyl': 'para- et métaxylène', 'Xyl': 'xylène', 'Styr': 'styrène', 'BTEX_tot': 'btex totaux', 'Phenol': 'phénol', 'Idc_Phenol': 'indice phénol', 'Naphta': 'naphtalène', 'Acenaphtyl': 'acénaphtylène', 'Acenaphtn': 'acénaphtène', 'Fluorene': 'fluorène', 'Phenanthr': 'phénanthrène', 'Anthrc': 'anthracène', 'Flranth': 'fluoranthène', 'Pyr': 'pyrène', 'Bnz(a)anthrc': 'benzo(a)anthracène', 'Chrys': 'chrysène', 'Bnz(b)flranth': 'benzo(b)fluoranthène', 'Bnz(k)flranth': 'benzo(k)fluoranthène', 'Bnz(a)pyr': 'benzo(a)pyrène', 'Dibnz(ah)anthrc': 'dibenzo(ah)anthracène', 'Bnz(ghi)peryl': 'benzo(ghi)pérylène', 'Indeno(1,2,3-cd)pyr': 'indéno(1,2,3-cd)pyrène', 'HAP_tot_EPA': 'hap totaux (16) - epa', '1,1-DCE': '1,1-dichloroéthane', '1,2-DCE': '1,2-dichloroéthane', '1,1-DCEn': '1,1-dichloroéthène', 'Cis-1,2-DCEn': 'cis-1,2-dichloroéthène', 'Trans 1,2-DCEyl': 'trans 1,2-dichloroéthylène', 'DCM': 'dichlorométhane', '(cis,trans) 1,2-DCE_tot': 'totaux (cis,trans) 1,2-dichloroéthène', '1,2-DCP': '1,2-dichloropropane', 'TetraCEyn': 'tétrachloroéthylène', 'TCM': 'tétrachlorométhane', '1,1,1-TCE': '1,1,1-trichloroéthane', '1,1,2-TCE': '1,1,2-trichloroéthane', 'TCEyn': 'trichloroéthylène', 'Chloroforme': 'chloroforme', 'CVinyl': 'chlorure de vinyle', 'EOX': 'eox', 'Arom_C6C7': 'fraction aromat. >c6-c7', 'Arom_C7C8': 'fraction aromat. >c7-c8', 'Arom_C8C10': 'fraction aromat. >c8-c10', 'Aliphat_C5C6': 'fraction aliphat. c5-c6', 'Aliphat_C6C8': 'fraction aliphat. >c6-c8', 'Aliphat_C8C10': 'fraction aliphat. >c8-c10', 'Fract_C5C8': 'fraction c5-c8', 'Fract_C8C10': 'fraction c8-c10', 'Fract_C10C12': 'fraction c10-c12', 'Fract_C12C16': 'fraction c12-c16', 'Fract_C16C21': 'fraction c16-c21', 'Fract_C21C35': 'fraction c21-c35', 'Fract_C35C40': 'fraction c35-c40', 'HC_tot_C10C35': 'hydrocarbures totaux c10-c35', 'HC_tot_C10C40': 'hydrocarbures totaux c10-c40', 'MTBE': 'mtbe', 'PCB_28': 'pcb 28', 'PCB_52': 'pcb 52', 'PCB_101': 'pcb 101', 'PCB_118': 'pcb 118', 'PCB_138': 'pcb 138', 'PCB_153': 'pcb 153', 'PCB_180': 'pcb 180', 'PCB_tot': 'pcb totaux (7)', 'Cl': 'chlorures', 'S_tot': 'soufre total'}}


# industrial sites pollution Norm (soil and water)
LEX_SOIL_NORM = {'unit': 'mg/kg MS',
                  'pollutants': {'arsenic': {'VR': 12, 'VS': 50, 'VI': 300}, 'cadmium': {'VR': 0.2, 'VS': 15, 'VI': 50}, 'chrome': {'VR': 34, 'VS': 165, 'VI': 700}, 'chrome vi': {'VR': 2.5, 'VS': 13, 'VI': 130}, 'cuivre': {'VR': 14, 'VS': 120, 'VI': 500}, 'mercure': {'VR': 0.05, 'VS': 5, 'VI': 50}, 'plomb': {'VR': 25, 'VS': 385, 'VI': 1360}, 'nickel': {'VR': 24, 'VS': 210, 'VI': 500}, 'zinc': {'VR': 67, 'VS': 320, 'VI': 1300}, 'cyanure (libre)': {'VR': 0.05, 'VS': 1, 'VI': 5}, 'benzène': {'VR': 0.1, 'VS': 0.2, 'VI': 0.8}, 'toluène': {'VR': 0.2, 'VS': 12, 'VI': 120}, 'éthylbenzène': {'VR': 0.2, 'VS': 17, 'VI': 116}, 'xylène': {'VR': 0.2, 'VS': 3, 'VI': 25}, 'styrène': {'VR': 0.2, 'VS': 2, 'VI': 10}, 'phénol': {'VR': 0.1, 'VS': 1.4, 'VI': 13}, 'indice phénol': {'VR': np.nan, 'VS': np.nan, 'VI': 2}, 'naphtalène': {'VR': 0.1, 'VS': 2.5, 'VI': 25}, 'acénaphtylène': {'VR': 0.01, 'VS': 43, 'VI': 410}, 'acénaphtène': {'VR': 0.01, 'VS': 6, 'VI': 56}, 'fluorène': {'VR': 0.01, 'VS': 16, 'VI': 163}, 'phénp.nanthrène': {'VR': 0.1, 'VS': 16, 'VI': 164}, 'anthracène': {'VR': 0.01, 'VS': 1.3, 'VI': 13.3}, 'fluoranthène': {'VR': 0.01, 'VS': 47, 'VI': 475}, 'pyrène': {'VR': 0.01, 'VS': 6.4, 'VI': 64}, 'benzo(a)anthracène': {'VR': 0.01, 'VS': 1.5, 'VI': 15}, 'chrysène': {'VR': 0.01, 'VS': 6, 'VI': 60}, 'benzo(b)fluoranthène': {'VR': 0.01, 'VS': 1.3, 'VI': 13}, 'benzo(k)fluoranthène': {'VR': 0.01, 'VS': 4.7, 'VI': 47}, 'benzo(a)pyrène': {'VR': 0.01, 'VS': 1.3, 'VI': 13}, 'dibenzo(ah)anthracène': {'VR': 0.01, 'VS': 1.4, 'VI': 14}, 'benzo(ghi)pérylène': {'VR': 0.01, 'VS': 5, 'VI': 46}, 'indéno(1,2,3-cd)pyrène': {'VR': 0.01, 'VS': 1.5, 'VI': 15}, '1,2-dichloroéthane': {'VR': 0.05, 'VS': 0.3, 'VI': 1.4}, 'dichlorométhane': {'VR': 0.05, 'VS': 0.2, 'VI': 0.8}, 'totaux (cis,trans) 1,2-dichloroéthène': {'VR': 0.05, 'VS': 0.6, 'VI': 2.5}, 'tétrachloroéthylène': {'VR': 0.05, 'VS': 1.7, 'VI': 11}, 'tétrachlorométhane': {'VR': 0.05, 'VS': 0.1, 'VI': 0.2}, '1,1,1-trichloroéthane': {'VR': 0.05, 'VS': 6, 'VI': 58}, '1,1,2-trichloroéthane': {'VR': 0.05, 'VS': 0.2, 'VI': 0.8}, 'trichloroéthylène': {'VR': 0.05, 'VS': 2, 'VI': 9}, 'chloroforme': {'VR': 0.05, 'VS': 3, 'VI': 12}, 'chlorure de vinyle': {'VR': 0.05, 'VS': 0.1, 'VI': 0.4}, 'eox': {'VR': np.nan, 'VS': np.nan, 'VI': 3}, 'fraction c5-c8': {'VR': 2, 'VS': 9, 'VI': 20}, 'fraction c8-c10': {'VR': 2, 'VS': 80, 'VI': 320}, 'fraction c10-c12': {'VR': 2.5, 'VS': 130, 'VI': 160}, 'fraction c12-c16': {'VR': 15, 'VS': 130, 'VI': 520}, 'fraction c16-c21': {'VR': 15, 'VS': 1250, 'VI': 2500}, 'fraction c21-c35': {'VR': 15, 'VS': 1250, 'VI': 2500}, 'mtbe': {'VR': 0.05, 'VS': 2, 'VI': 8}}}

LEX_WATER_NORM = {'unit': 'µg/l',
                   'pollutants': {'arsenic': {'VR': 1, 'VS': 10, 'VI': 40}, 'cadmium': {'VR': 0.25, 'VS': 5, 'VI': 20}, 'chrome': {'VR': 2.5, 'VS': 50, 'VI': 100}, 'chrome vi': {'VR': 2.5, 'VS': 9, 'VI': 90}, 'cuivre': {'VR': 15, 'VS': 100, 'VI': 200}, 'mercure': {'VR': 0.1, 'VS': 1, 'VI': 4}, 'plomb': {'VR': 2.5, 'VS': 10, 'VI': 40}, 'nickel': {'VR': 10, 'VS': 20, 'VI': 80}, 'zinc': {'VR': 90, 'VS': 200, 'VI': 400}, 'cyanure (libre)': {'VR': 2, 'VS': 70, 'VI': 140}, 'benzène': {'VR': 0.25, 'VS': 10, 'VI': 40}, 'toluène': {'VR': 2, 'VS': 700, 'VI': 5850}, 'éthylbenzène': {'VR': 2, 'VS': 300, 'VI': 1520}, 'xylène': {'VR': 4, 'VS': 500, 'VI': 2175}, 'styrène': {'VR': 2, 'VS': 20, 'VI': 110}, 'phénol': {'VR': 0.2, 'VS': 120, 'VI': 1115}, 'indice phénol': {'VR': np.nan, 'VS': np.nan, 'VI': 5}, 'naphtalène': {'VR': 0.05, 'VS': 60, 'VI': 410}, 'acénaphtylène': {'VR': 0.05, 'VS': 70, 'VI': 660}, 'acénaphtène': {'VR': 0.05, 'VS': 180, 'VI': 1800}, 'fluorène': {'VR': 0.05, 'VS': 120, 'VI': 1200}, 'phénp.nanthrène': {'VR': 0.05, 'VS': 120, 'VI': 240}, 'anthracène': {'VR': 0.05, 'VS': 75, 'VI': 150}, 'fluoranthène': {'VR': 0.05, 'VS': 4, 'VI': 60}, 'pyrène': {'VR': 0.05, 'VS': 90, 'VI': 900}, 'benzo(a)anthracène': {'VR': 0.05, 'VS': 0.7, 'VI': 7}, 'chrysène': {'VR': 0.05, 'VS': 1.5, 'VI': 3}, 'benzo(b)fluoranthène': {'VR': 0.05, 'VS': 1.5, 'VI': 69}, 'benzo(k)fluoranthène': {'VR': 0.05, 'VS': 0.8, 'VI': 1.6}, 'benzo(a)pyrène': {'VR': 0.05, 'VS': 0.7, 'VI': 1.4}, 'dibenzo(ah)anthracène': {'VR': 0.05, 'VS': 0.7, 'VI': 7}, 'benzo(ghi)pérylène': {'VR': 0.05, 'VS': 0.3, 'VI': 0.5}, 'indéno(1,2,3-cd)pyrène': {'VR': 0.05, 'VS': 0.22, 'VI': 0.44}, '1,2-dichloroéthane': {'VR': 2, 'VS': 30, 'VI': 125}, 'totaux (cis,trans) 1,2-dichloroéthène': {'VR': 2, 'VS': 50, 'VI': 200}, 'dichlorométhane': {'VR': 1, 'VS': 20, 'VI': 90}, 'tétrachloroéthylène ': {'VR': 1, 'VS': 40, 'VI': 170}, 'tétrachlorométhane': {'VR': 1, 'VS': 2, 'VI': 8}, '1,1,1-trichloroéthane': {'VR': 2, 'VS': 500, 'VI': 8450}, '1,1,2-trichloroéthane': {'VR': 2, 'VS': 12, 'VI': 50}, 'trichloroéthylène': {'VR': 1, 'VS': 70, 'VI': 290}, 'chloroforme': {'VR': 1, 'VS': 200, 'VI': 815}, 'chlorure de vinyle': {'VR': 1, 'VS': 5, 'VI': 20}, 'fraction c5-c8': {'VR': 30, 'VS': 60, 'VI': 120}, 'fraction c8-c10': {'VR': 30, 'VS': 200, 'VI': 400}, 'fraction c10-c12': {'VR': 40, 'VS': 200, 'VI': 400}, 'fraction c12-c16': {'VR': 5, 'VS': 200, 'VI': 400}, 'fraction c16-c21': {'VR': 15, 'VS': 300, 'VI': 600}, 'fraction c21-c35': {'VR': 15, 'VS': 300, 'VI': 600}, 'mtbe': {'VR': 2, 'VS': 300, 'VI': 1235}}}


# ======================= LEGENDES ============================
LEG_CONTAMINATION_LEV = """colour,width,component {:}
#9CB39C, None, VR,
#00FF00, None, VS,
#FFA500, None, VI,
#FF0000, None, VI_,
#FFFFFF, None, Inconnu
"""

LEG_LITHO_MEMORIS = """colour,width, hatch, component lithology
#FFFFE9, None, None, Matériau(?:x)? meuble(?:s)?,
#FFF497, None, '....', Alluvion,
#B54500, None, None, Boue,
#D3B798, None, 'v', Remblai,
#a5c7c9, None, 't', B[é|e]ton,
#8da3c9, None, 't', Scorie,
#FFCC99, None, None, Tourbe,
#FFEAA7, None, None, Gypse,
#00151A, None, None, Houille,
#798732, None, '-.', Limon,
#FFCB23, None, '..', Sable,
#ADB7CC, None, 'oo, Gravier,
#ACE4C8, None, None, Silt,
#D5E6CC, None, '---', Argile,
#92DCB7, None, None, Bentonite,
#BBFFDD, None, '--', Schiste,
#95FFCA, None, None, Argilite,
#D6FE9A, None, None, Siltite,
#E1F0D8, None, None, Tuffeau,
#69CF9C, None, None, Silex,
#B7D9CC, None, None, Conglomérat,
#019CCD, None, None, Carbonate,
#149EFF, None, '=', Calcaire,
#FDAAFF, None, None, Dolomite,
#FDAFFE, None, None, Dolomie,
#DEEFFE, None, None, Craie,
#AAC2C8, None, None, Chert,
#000000, None, None, Charbon,
#7BA1A8, None, None, Marne,
#FFFFFF, None, None, Inconnu
#FFFFFF, None, None, Not_exist
"""


# ======================= COULEURS ============================
COLOURS = {
    'abricot': '#E67E30',
    'acajou': '#88421D',
    'aigue-marine': '#79F8F8',
    'aile de corbeau': '#000000',
    'albâtre': '#FEFEFE',
    'alezan': '#A76726',
    'amarante': '#91283B',
    'ambre': '#F0C300',
    'améthyste': '#884DA7',
    'argent': '#CECECE',
    'asperge': '#7BA05B',
    'aubergine': '#370028',
    'auburn': '#9D3E0C',
    'aurore': '#FFCB60',
    'azur': '#1E7FCB',
    'azur brume': '#F0FFFF',
    'azur clair': '#74D0F1',
    'azurin': '#A9EAFE',
    'basané': '#8B6C42',
    'beige': '#C8AD7F',
    'beige clair': '#F5F5DC',
    'beigeasse': '#AFA778',
    'beurre': '#F0E36B',
    'beurre frais': '#FFF48D',
    'bis': '#F1E2BE',
    'bisque': '#FFE4C4',
    'bistre': '#856D4D',
    'bitume': '#4E3D28',
    'blanc': '#FFFFFF',
    'blanc cassé': '#FEFEE2',
    'blanc crème': '#FDF1B8',
    'blanc céruse': '#FEFEFE',
    "blanc d'espagne": '#FEFDF0',
    "blanc d'argent": '#FEFEFE',
    "blanc d'ivoire": '#FFFFF4',
    'blanc de saturne': '#FEFEFE',
    'blanc de troyes': '#FEFDF0',
    'blanc de zinc': '#F6FEFE',
    'blanc de lait': '#FBFCFA',
    'blanc de lin': '#FAF0E6',
    'blanc de platine': '#FAF0C5',
    'blanc de plomb': '#FEFEFE',
    'blanc lunaire': '#F4FEFE',
    'blanc neige': '#FEFEFE',
    'blanc opalin': '#F2FFFF',
    'blanc écru': '#FEFEE0',
    'blanc-bleu': '#FEFEFE',
    'blet': '#5B3C11',
    'bleu': '#0000FF',
    'bleu acier': '#3A8EBA',
    'bleu ardoise': '#686F8C',
    'bleu barbeau': '#5472AE',
    'bleu bleuet': '#5472AE',
    'bleu bondi': '#0095B6',
    'bleu charrette': '#8EA2C6',
    'bleu charron': '#8EA2C6',
    'bleu ciel': '#77B5FE',
    'bleu cobalt': '#22427C',
    'bleu céleste': '#26C4EC',
    'bleu céruléen': '#357AB7',
    'bleu de berlin': '#24445C',
    'bleu de france': '#318CE7',
    'bleu de prusse': '#24445C',
    'bleu de minuit': '#003366',
    'bleu denim': '#1560BD',
    'bleu des mers du sud': '#00CCCB',
    'bleu dragée': '#DFF2FF',
    'bleu guède': '#56739A',
    'bleu horizon': '#7F8FA6',
    'bleu majorelle': '#6050DC',
    'bleu marine': '#03224C',
    'bleu maya': '#73C2FB',
    'bleu minéral': '#24445C',
    'bleu nuit': '#0F056B',
    'bleu outremer': '#2B009A',
    'bleu paon': '#067790',
    'bleu persan': '#6600FF',
    'bleu pétrole': '#1D4851',
    'bleu roi': '#318CE7',
    'bleu saphir': '#0131B4',
    'bleu sarcelle': '#008E8E',
    'bleu smalt': '#003399',
    'bleu tiffany': '#0ABAB5',
    'bleu turquin': '#425B8A',
    'bleu égyptien': '#1034A6',
    'bleu électrique': '#2C75FF',
    'blond': '#E2BC74',
    'blé': '#E8D630',
    'bordeaux': '#6D071A',
    "boutton d'or": '#FCDC12',
    'brique': '#842E1B',
    'bronze': '#614E1A',
    'brou de noix': '#3F2204',
    'brun': '#5B3C11',
    'bulle': '#EDD38C',
    'bureau': '#6B5731',
    'byzantin': '#BD33A4',
    'byzantium': '#702963',
    "caca d'oie": '#CDCD0D',
    'cacao': '#614B3A',
    'cachou': '#2F1B0C',
    'café': '#462E01',
    'café au lait': '#785E2F',
    'canard': '#048B9A',
    'cannelle': '#7E5835',
    'caramel': '#7E3300',
    'carotte': '#F4661B',
    'cassis': '#3A020D',
    'cerise': '#DE3163',
    'chair': '#FEC3AC',
    'chamois': '#D0C07A',
    'champagne': '#FBF2B7',
    'chaudron': '#85530F',
    'chocolat': '#5A3A22',
    'chrome': '#FFFF05',
    'châtaigne': '#806D5A',
    'châtain': '#8B6C42',
    'citron': '#F7FF3C',
    'citrouille': '#DF6D14',
    'colombin': '#6A455D',
    "coquille d'oeuf": '#FDE9E0',
    'corail': '#E73E01',
    'cuisse de nymphe': '#FEE7F0',
    'cuivre': '#B36700',
    'cyan': '#2BFAFA',
    'cæruléum': '#26C4EC',
    'céladon': '#83A697',
    'cérulé': '#74D0F1',
    'dorian': '#0B1616',
    'ebène': '#000000',
    'ecarlate': '#ED0000',
    'etain oxydé': '#BABABA',
    'etain pur': '#EDEDED',
    'fauve': '#AD4F09',
    'feuille-morte': '#99512B',
    'flave': '#E6E697',
    'fleur de soufre': '#FFFF6B',
    'fraise': '#BF3030',
    'fraise écrasée': '#A42424',
    'framboise': '#C72C48',
    'fumée': '#BBD2E1',
    'fushia': '#FD3F92',
    'givré': '#80D0D0',
    'glauque': '#649B88',
    'glycine': '#C9A0DC',
    'gomme-gutte': '#EF9B0F',
    'grenadine': '#E9383F',
    'grenat': '#6E0B14',
    'gris': '#606060',
    'gris fer': '#848484',
    'gris perle': '#C7D0CC',
    'gris acier': '#AFAFAF',
    'gris anthracite': '#303030',
    'gris de payne': '#677179',
    'gris de lin': '#D2CAEC',
    'gris de maure': '#685E43',
    'gris souris': '#9E9E9E',
    'gris tourterelle': '#BBACAC',
    'grège': '#BBAE98',
    'hooker': '#1B4F08',
    'héliotrope': '#DF73FF',
    'incarnadin': '#FE96A0',
    'incarnat': '#FF6F7D',
    'indigo': '#2E006C',
    'indigo du web': '#4B0082',
    'jade': '#87E990',
    'jaune': '#FFFF00',
    'jaune auréolin': '#EFD242',
    'jaune banane': '#D1B606',
    'jaune canari': '#E7F00D',
    'jaune chartreuse': '#DFFF00',
    "jaune d'or": '#EFD807',
    'jaune de naples': '#FFF0BC',
    'jaune de cobalt': '#FDEE00',
    'jaune impérial': '#FFE436',
    'jaune mimosa': '#FEF86C',
    'jaune moutarde': '#C7CF00',
    'jaune nankin': '#F7E269',
    'jaune olive': '#808000',
    'jaune paille': '#FEE347',
    'jaune poussin': '#F7E35F',
    'kaki': '#94812B',
    'klein': '#21177D',
    'lapis-lazuli': '#26619C',
    'lavallière': '#8F5922',
    'lavande': '#9683EC',
    'lie de vin': '#AC1E44',
    'lilas': '#B666D2',
    'magenta': '#FF00FF',
    'magenta foncé': '#800080',
    'magenta fushia': '#DB0073',
    'mandarine': '#FEA347',
    'marron': '#582900',
    'mars': '#EED153',
    'mastic': '#B3B191',
    'mauve': '#D473D4',
    'maïs': '#FFDE75',
    'melon': '#DE9816',
    'menthe': '#16B84E',
    "menthe à l'eau": '#54F98D',
    'miel': '#DAB30A',
    'mordoré': '#87591A',
    'nacarat': '#FC5D5D',
    'noir': '#000000',
    'noir animal': '#000000',
    'noir charbon': '#000000',
    "noir d'aniline": '#120D16',
    "noir d'encre": '#000000',
    "noir d'ivoire": '#000000',
    'noir de carbone': '#130E0A',
    'noir de fumée': '#130E0A',
    'noir de jais': '#000000',
    'noiraud': '#2F1E0E',
    'noisette': '#955628',
    'ocre jaune': '#DFAF2C',
    'ocre rouge': '#DD985C',
    'or': '#FFD700',
    'orange': '#ED7F10',
    'orange brûlée': '#CC5500',
    'orangé': '#FAA401',
    'orchidée': '#DA70D6',
    'orpiment': '#FCD21C',
    'parme': '#CFA0E9',
    'passe-velours': '#91283B',
    'pastel': '#56739A',
    'pervenche': '#CCCCFF',
    'pinchard': '#CCCCCC',
    'plomb': '#798081',
    'poil de chameau': '#B67823',
    'pourpre': '#9E0E40',
    'prune': '#811453',
    'puce': '#4E1609',
    'pêche': '#FDBFB7',
    'queue de vache': '#A89874',
    'rose': '#FD6C9E',
    'rose mountbatten': '#997A8D',
    'rose balais': '#C4698F',
    'rose bonbon': '#F9429E',
    'rose dragée': '#FEBFD2',
    'rose thé': '#FF866A',
    'rose vif': '#FF007F',
    'rouge': '#FF0000',
    'rouge alizarine': '#D90115',
    'rouge anglais': '#F7230C',
    'rouge bismarck': '#A5260A',
    'rouge bourgogne': '#6B0D0D',
    'rouge capucine': '#FF5E4D',
    'rouge cardinal': '#B82010',
    'rouge carmin': '#960018',
    'rouge cinabre': '#FD4626',
    'rouge coquelicot': '#C60800',
    'rouge cramoisi': '#DC143C',
    "rouge d'andrinople": '#A91101',
    "rouge d'aniline": '#EB0000',
    'rouge de falun': '#801818',
    'rouge de mars': '#F7230C',
    'rouge feu': '#FF4901',
    'rouge garance': '#EE1010',
    'rouge groseille': '#CF0A1D',
    'rouge ponceau': '#C60800',
    'rouge rubis': '#E0115F',
    'rouge sang': '#850606',
    'rouge tomate': '#DE2916',
    'rouge tomette': '#AE4A34',
    'rouge turc': '#A91101',
    'rouge vermillon': '#FD4626',
    'rouge écrevisse': '#BC2001',
    'rouge-violet': '#C71585',
    'rouille': '#985717',
    'roux': '#AD4F09',
    'réglisse': '#2D241E',
    'safran': '#F3D617',
    'sang de boeuf': '#730800',
    'saumon': '#F88E55',
    'senois': '#8D4024',
    'sinople': '#149414',
    'soufre': '#FFFF6B',
    'sépia': '#AE8964',
    'tabac': '#9F551E',
    'tangerine': '#FF7F00',
    'tanné': '#A75502',
    'taupe': '#463F32',
    'terracotta': '#CC4E5C',
    "terre d'ombre": '#926D27',
    'terre de sienne': '#8E5434',
    'topaze': '#FAEA73',
    'tourdille': '#C1BFB1',
    'turquoise': '#25FDE9',
    'vanille': '#E1CE9A',
    'ventre de biche': '#E9C9B1',
    'vermeil': '#FF0921',
    'vert': '#00FF00',
    'vert absinthe': '#7FDD4C',
    'vert amande': '#82C46C',
    'vert anglais': '#18391E',
    'vert anis': '#9FE855',
    'vert avocat': '#568203',
    'vert bouteille': '#096A09',
    'vert chartreuse': '#C2F732',
    'vert citron': '#00FF00',
    "vert d'eau": '#B0F2B6',
    'vert de chrome': '#18391E',
    'vert de gris': '#95A595',
    'vert de vessie': '#22780F',
    'vert empire': '#00561B',
    'vert gazon': '#3A9D23',
    'vert impérial': '#00561B',
    'vert kaki': '#798933',
    'vert lichen': '#85C17E',
    'vert lime': '#9EFD38',
    'vert malachite': '#1FA055',
    'vert militaire': '#596643',
    'vert mousse': '#679F5A',
    'vert mélèse': '#386F48',
    'vert olive': '#708D23',
    'vert opaline': '#97DFC6',
    'vert perroquet': '#3AF24B',
    'vert pin': '#01796F',
    'vert pistache': '#BEF574',
    'vert poireau': '#4CA66B',
    'vert pomme': '#34C924',
    'vert prairie': '#57D53B',
    'vert prasin': '#4CA66B',
    'vert printemps': '#00FE7E',
    'vert sapin': '#095228',
    'vert sauge': '#689D71',
    'vert smaragdin': '#01D758',
    'vert tilleul': '#A5D152',
    'vert viride': '#40826D',
    'vert véronèse': '#586F2D',
    'vert émeraude': '#01D758',
    'vert épinard': '#175732',
    'violet': '#660099',
    "violet d'évêque": '#723E64',
    'violine': '#A10684',
    'vénitien': '#E7A854',
    'zizolin': '#6C0277',
    'orange gris': '#C28100',
    'verdâtre': '#334D00',
    'brun beige': '#DEB671',
    'noir verdâtre': '#003322',
    'verdâtre brun': '#404D00'}
