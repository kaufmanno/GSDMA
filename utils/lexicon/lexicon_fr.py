"""
Definition de mots clés pour les descriptions de cuttings de forages.
:copyright: 2021  Y. N'DEPO & O. Kaufmann 
"""

from striplog import Lexicon, Legend

#==================== LEXIQUE ================================ 
LEXICON_MEMORIS = {'lithology': ['Anthracite(?:s)?', 'Porphyre(?:s)?', 'Houille(?:s)?', 'Diorite(?:s)?', 'Cargneule(?:s)?', 'Molasse(?:s)?', 'Jaspe(?:s)?', 'Gravier(?:s)?', 'Leptynite(?:s)?','Pyroxénite(?:s)?', 'Pierre coquillière(?:s)?', 'Grès(?:s)?', 'Obsidienne(?:s)?', 'Basalte(?:s)?', 'Charbon(?:s)?',   'Anhydrite(?:s)?', 'Andésite(?:s)?', 'Ardoise(?:s)?', 'Carbonatite(?:s)?', 'Dolérite(?:s)?',   'Cendres(?:s)?', 'Poudingue(?:s)?', 'Alios(?:s)?', 'Quartzite(?:s)?', 'Calcaire(?:s)?',   'Gypse(?:s)?', 'Limon(?:s)?', 'Phonolite(?:s)?', 'Arkose(?:s)?', 'Pegmatite(?:s)?',   'Bauxite(?:s)?', 'Pierre coquillère(?:s)?', 'Gneiss', 'Mort-terrain(?:s)?', 'Silcrète(?:s)?',   'Lignite(?:s)?', 'Conglomérat(?:s)?', 'Glauconie(?:s)?', 'Ponce(?:s)?', 'Péridotite(?:s)?',   'Combarbalite(?:s)?', 'Glauconite(?:s)?', 'Anatexite(?:s)?', 'Amphibolite(?:s)?',   'Greisen(?:s)?', 'Tuffeau(?:s)?', 'Granite(?:s)?', 'Gr(?:è|e|é)s', 'Brèche(?:s)?',   'Dolomie(?:s)?', 'Tuf volcanique(?:s)?', 'Halite(?:s)?', "Granite d'anatexie(?:s)?",   'Ignimbrite(?:s)?', 'Bentonite(?:s)?', 'Monzonite(?:s)?', 'Rhyolite(?:s)?', 'Monazite(?:s)?',   'Silex', 'Gabbro(?:s)?', 'Argile(?:s)?', 'Syénite(?:s)?', 'Kimberlite(?:s)?', 'Cendre(?:s)?',   'Cinérite(?:s)?', 'Tourbe(?:s)?', 'Aplite(?:s)?', 'Grè(?:s)?', 'Marne(?:s)?', 'Dacite(?:s)?',   'Micaschiste(?:s)?', 'Molasse (?:s)?', 'Tillite(?:s)?', 'Schiste(?:s)?', 'Granodiorite(?:s)?',   'Phtanite(?:s)?', 'Tuf(?:s)?', 'Sable(?:s)?', 'Trachyte(?:s)?','Remblai(?:s)?', 'Alluvion(?:s)?','Boue(?:s)?', 'Marbre(?:s)?',   'Ophite(?:s)?', 'Éclogite(?:s)?', 'Cipolin(?:s)?', 'Kersantite(?:s)?', 'Lapillis(?:s)?',   'Diatomite(?:s)?', 'Craie(?:s)?', 'Radiolarite(?:s)?'],
              
           'state': ['altéré(?:e|es)?', 'sain(?:s|e|es)?', 'hétérogène(?:s)?', 'homogène(?:s)?'],
              
           'shape': ['lentille(?:s)?', 'biseau(x)?', 'strie(?:s)?', 'veine(?:s)?', 'filet(?:s)?', 'filon(?:s)?', 'intercalé(?:s|e|es)?', 'intercalation(?:s)?', 'interstratifié(?:s|e|es)?', 'tacheté(?:s|e|es)?', 'bande(?:s)?', 'bariolé(?:e|es)?'],
              
           'material': ['laitier', 'Scories', 'béton', 'scorie(?:s)?', 'Ballast', 'Laitier', 'Géotextile', 'Scorie', 'g[e|é]otextile(?:s)?', 'Ballasts', 'ballast(?:s)?', 'Béton'],
              
           'modifier': ['Sableu(?:x|se|ses)?', 'shisteu(?:x|se)', 'caillouteu(?:x|se)', 'Charboneu(?:x|se|ses)?', 'Schisteu(?:x|se|ses)?', 'sableu(?:x|se)', 'argileu(?:x|se)', 'graveleu(?:x|se)', 'pierreu(?:x|se)', 'Argileu(?:x|se|ses)?', 'silteu(?:x|se)', 'Cendreu(?:x|se|ses)?', 'Charbonneu(?:x|se|ses)?', 'Tourbeu(?:x|se|ses)?', 'Limoneu(?:x|se|ses)?', 'bitumineu(?:x|se)', 'saturé(?:e|es)?', 'Gréseu(?:x|se|ses)?', 'boueu(?:x|se)'],
              
           'grainsize': ['(?:pluri(?:-)?)?(?:d[e|é]ci|centi|milli)?m[e|é]trique(?:s)?', 'vf(?:-)?', 'f(?:-)?',  '\\d+ mm(?:-)?', 'c(?:-)?', 'vc', 'très fin(?:e à)?', 'fin(?:e|s|es à)?','moyen(?:ne à)?',  'grossi(?:er|ers|ère|ères à)?', 'très grossi(?:er|ère)', 't fin(?:e|s|es à)?', 'moy(?: à)?',  'moy.(?: à)?', 't grossier(?:s)?', 'granules?', 'cailloux?', 'galets?', 'blocs rocheux?'],
              
           'quantity': ['beaucoup', 'peu', 'moins', 'plusieurs', 'fragment(?:s)?', 'impurité(?:es)', 'abondant(?:e|es)', 'mineur','quelques', 'rare', 'flocon(?:s)?', 'trace(?:s)', '[-.\\d]+%', '[-.\\d]+pc', '[-.\\d]+pourcent'],

           'Pollutant': ['naphtalène', 'HAP', 'huile(?:s)?'],

           'synonyms': {'mort-terrain': ['terre'], 'Anhydrite': ['Gypse'], 'Sel': ['Halite', 'Sylvite']},

           'splitters': [' avec ', ' de ', ' cont(?:ient|enant) ', '\\. '],

           'parts_of_speech': {'noun': ['lithology'], 'adjective': ['colour', 'grainsize', 'modifier'], 'subordinate': ['quantity']},

           'abbreviations': {'Argilo':'Argile', 'Sablo':'sable'},

          'colour' : ['Bleu(?:e|es|âtre|âtres)?', 'Blanc(?:he|hes|hâtre|hâtres)?', 'Gris(?:e|es|âtre|âtres)?', 'Jaun(?:e|es|âtre|âtres)?', 'Marron', 'Noir(?:e|es|âtre|âtres)?', 'Ros(?:e|es|âtre|âtres)?', 'Roug(?:e|es|âtre|âtres)?', 'Ver(?:t|te|tes|dâtre|dâtres)?', 'Violet(?:te|tes)?', 'Orange', 'Jaune-gris', 'Blanc-gris', 'Brun-jaune', 'Gris-noir', 'Rouge-orange', 'Noir-brun', 'Jaune-vert', 'Vert-ocre', 'Verdâtre-brun', 'Grise-verdâtre', 'Noir-rouge', 'beige', 'Jaune-kaki', 'Brun-gris', 'Jaune-ocre', 'Vert-de-gris', 'Gris-rouge', 'Aigue-marine', 'Azur', 'Azur clair', 'Azurin', 'Bleu acier', 'Bleu ardoise', 'Bleu barbeau', 'Bleu bleuet', 'Bleu bondi', 'Bleu céleste', 'Bleu céruléen', 'Bleu charrette', 'Bleu charron', 'Bleu ciel', 'Bleu cobalt', 'Bleu de Berlin', 'Bleu de France', 'Bleu de minuit', 'Bleu de Prusse', 'Bleu denim', 'Bleu des mers du sud', 'Bleu dragée', 'Bleu égyptien', 'Bleu électrique', 'Bleu guède', 'Bleu horizon', 'Bleu majorelle', 'Bleu marine', 'Bleu maya', 'Bleu minéral', 'Bleu nuit', 'Bleu outremer', 'Bleu paon', 'Bleu persan', 'Bleu pétrole', 'Bleu roi', 'Bleu saphir', 'Bleu sarcelle', 'Bleu smalt', 'Bleu tiffany', 'Bleu turquin', 'Cæruléum', 'Canard', 'Cérulé', 'Cyan', 'Fumée', 'Givré', 'Indigo', 'Indigo du web', 'Klein', 'Lapis-lazuli', 'Lavande', 'Pastel', 'Pervenche', 'Turquoise', 'Blanc', 'Albâtre', 'Azur brume', 'Beige clair', 'Blanc cassé', 'Blanc céruse', 'Blanc crème', "Blanc d'argent", 'Blanc de lait', 'Blanc de lin', 'Blanc de platine', 'Blanc de plomb', 'Blanc de Saturne', 'Blanc de Troyes', 'Blanc de Zinc', "Blanc d'Espagne", "Blanc d'ivoire", 'Blanc écru', 'Blanc lunaire', 'Blanc neige', 'Blanc opalin', 'Blanc-bleu', "Coquille d'oeuf", 'Cuisse de nymphe', 'Brun', 'Acajou', 'Alezan', 'Ambre', 'Auburn', 'Basané', 'Beige', 'Beigeasse', 'Bistre', 'Bitume', 'Blet', 'Brique', 'Bronze', 'Brou de noix', 'Bureau', 'Cacao', 'Cachou', 'Café', 'Café au lait', 'Cannelle', 'Caramel', 'Châtaigne', 'Châtain', 'Chaudron', 'Chocolat', 'Citrouille', 'Fauve', 'Feuille-morte', 'Grège', 'Gris de maure', 'Lavallière', 'Marron', 'Mordoré', 'Noisette', 'Orange brûlée', 'Puce', 'Rouge bismarck', 'Rouge tomette', 'Rouille', 'Sang de boeuf', 'Senois', 'Sépia', 'Tabac', 'Terre de Sienne', "Terre d'ombre", 'Vanille', 'Gris', 'Ardoise', 'Argent', 'Bis', 'Céladon', 'Etain oxydé', 'Etain pur', 'Gris acier', 'Gris anthracite', 'Gris de Payne', 'Gris fer', 'Gris Fer', 'Gris Perle', 'Gris souris', 'Gris tourterelle', 'Mastic', 'Pinchard', 'Plomb', 'Rose Mountbatten', 'Taupe', 'Tourdille', 'Jaune', 'Aurore', 'Beurre', 'Beurre frais', 'Blé', 'Blond', "Boutton d'or", 'Bulle', "Caca d'oie", 'Chamois', 'Champagne', 'Chrome', 'Citron', 'Flave', 'Fleur de soufre', 'Gomme-gutte', 'Jaune auréolin', 'Jaune banane', 'Jaune canari', 'Jaune chartreuse', 'Jaune de cobalt', 'Jaune de Naples', "Jaune d'or", 'Jaune impérial', 'Jaune mimosa', 'Jaune moutarde', 'Jaune nankin', 'Jaune olive', 'Jaune paille', 'Jaune poussin', 'Maïs', 'Mars', 'Miel', 'Ocre jaune', 'Ocre rouge', 'Or', 'Orpiment', 'Poil de chameau', 'Queue de vache', 'Safran', 'Soufre', 'Topaze', 'Vénitien', 'Noir', 'Aile de corbeau', 'Cassis', 'Dorian', 'Ebène', 'Noir animal', 'Noir charbon', "Noir d'aniline", 'Noir de carbone', 'Noir de fumée', 'Noir de jais', "Noir d'encre", "Noir d'ivoire", 'Noiraud', 'Réglisse', 'Orange', 'Abricot', 'Bisque', 'Carotte', 'Corail', 'Cuivre', 'Mandarine', 'Melon', 'Orangé', 'Roux', 'Saumon', 'Tangerine', 'Tanné', 'Ventre de biche', 'Rose', 'Cerise', 'Chair', 'Framboise', 'Fushia', 'Héliotrope', 'Incarnadin', 'Magenta', 'Magenta foncé', 'Magenta fushia', 'Mauve', 'Pêche', 'Rose balais', 'Rose bonbon', 'Rose dragée', 'Rose thé', 'Rose vif', 'Rouge', 'Amarante', 'Bordeaux', 'Ecarlate', 'Fraise', 'Fraise écrasée', 'Grenadine', 'Grenat', 'Incarnat', 'Nacarat', 'Passe-velours', 'Pourpre', 'Prune', 'Rouge alizarine', 'Rouge anglais', 'Rouge bourgogne', 'Rouge capucine', 'Rouge cardinal', 'Rouge carmin', 'Rouge cinabre', 'Rouge coquelicot', 'Rouge cramoisi', "Rouge d'Andrinople", "Rouge d'aniline", 'Rouge de falun', 'Rouge de mars', 'Rouge écrevisse', 'Rouge feu', 'Rouge garance', 'Rouge groseille', 'Rouge ponceau', 'Rouge rubis', 'Rouge sang', 'Rouge tomate', 'Rouge turc', 'Rouge vermillon', 'Rouge-violet', 'Terracotta', 'Vermeil', 'Zizolin', 'Vert', 'Asperge', 'Glauque', 'Hooker', 'Jade', 'Kaki', 'Menthe', "Menthe à l'eau", 'Sinople', 'Vert absinthe', 'Vert amande', 'Vert anglais', 'Vert anis', 'Vert avocat', 'Vert bouteille', 'Vert chartreuse', 'Vert citron', 'Vert de chrome', 'Vert de gris', 'Vert de vessie', "Vert d'eau", 'Vert émeraude', 'Vert empire', 'Vert épinard', 'Vert gazon', 'Vert impérial', 'Vert kaki', 'Vert lichen', 'Vert lime', 'Vert malachite', 'Vert mélèse', 'Vert militaire', 'Vert mousse', 'Vert olive', 'Vert opaline', 'Vert perroquet', 'Vert pin', 'Vert pistache', 'Vert poireau', 'Vert pomme', 'Vert prairie', 'Vert prasin', 'Vert printemps', 'Vert sapin', 'Vert sauge', 'Vert smaragdin', 'Vert tilleul', 'Vert véronèse', 'Vert viride', 'Violet', 'Améthyste', 'Aubergine', 'Byzantin', 'Byzantium', 'Colombin', 'Glycine', 'Gris de lin', 'Lie de vin', 'Lilas', 'Orchidée', 'Parme', "Violet d'évêque", 'Violine', 'rouge', 'orange gris', 'verdâtre', 'gris', 'brun', 'blanc', 'noire', 'brique', 'sable beige', 'brun beige', 'noir verdâtre', 'jaune', 'noir', 'verdâtre brun']
           }

lexicon_memoris = Lexicon(LEXICON_MEMORIS)

LEXICON_FR = {
    'lithology': ['Anthracite(?:s)?', 'Porphyre(?:s)?', 'Houille(?:s)?', 'Diorite(?:s)?', 'Cargneule(?:s)?', 'Molasse(?:s)?', 'Jaspe(?:s)?', 'Gravier(?:s)?', 'Leptynite(?:s)?', 'Pyroxénite(?:s)?', 'Pierre coquillière(?:s)?', 'Grès(?:s)?', 'Obsidienne(?:s)?', 'Basalte(?:s)?', 'Charbon(?:s)?', 'Anhydrite(?:s)?', 'Andésite(?:s)?', 'Ardoise(?:s)?', 'Carbonatite(?:s)?', 'Dolérite(?:s)?', 'Cendres(?:s)?', 'Poudingue(?:s)?', 'Alios(?:s)?', 'Quartzite(?:s)?', 'Calcaire(?:s)?', 'Gypse(?:s)?', 'Limon(?:s)?', 'Phonolite(?:s)?', 'Arkose(?:s)?', 'Pegmatite(?:s)?', 'Bauxite(?:s)?', 'Pierre coquillère(?:s)?', 'Gneiss', 'Mort-terrain(?:s)?', 'Silcrète(?:s)?', 'Lignite(?:s)?', 'Conglomérat(?:s)?', 'Glauconie(?:s)?', 'Ponce(?:s)?', 'Péridotite(?:s)?', 'Combarbalite(?:s)?', 'Glauconite(?:s)?', 'Anatexite(?:s)?', 'Amphibolite(?:s)?', 'Greisen(?:s)?', 'Tuffeau(?:s)?', 'Granite(?:s)?', 'Gr(?:è|e|é)s', 'Brèche(?:s)?', 'Dolomie(?:s)?', 'Tuf volcanique(?:s)?', 'Halite(?:s)?', "Granite d'anatexie(?:s)?", 'Ignimbrite(?:s)?', 'Bentonite(?:s)?', 'Monzonite(?:s)?', 'Rhyolite(?:s)?', 'Monazite(?:s)?', 'Silex', 'Gabbro(?:s)?', 'Argile(?:s)?', 'Syénite(?:s)?', 'Kimberlite(?:s)?', 'Cendre(?:s)?', 'Cinérite(?:s)?', 'Tourbe(?:s)?', 'Aplite(?:s)?', 'Grè(?:s)?', 'Marne(?:s)?', 'Dacite(?:s)?', 'Micaschiste(?:s)?', 'Molasse (?:s)?', 'Tillite(?:s)?', 'Schiste(?:s)?', 'Granodiorite(?:s)?', 'Phtanite(?:s)?', 'Tuf(?:s)?', 'Sable(?:s)?', 'Trachyte(?:s)?', 'Remblai(?:s)?', 'Alluvion(?:s)?', 'Boue(?:s)?', 'Marbre(?:s)?', 'Ophite(?:s)?', 'Éclogite(?:s)?', 'Cipolin(?:s)?', 'Kersantite(?:s)?', 'Lapillis(?:s)?', 'Diatomite(?:s)?', 'Craie(?:s)?', 'Radiolarite(?:s)?'],

    'state': ['altéré(?:e|es)?', 'sain(?:s|e|es)?', 'hétérogène(?:s)?', 'homogène(?:s)?'],

    'shape': ['lentille(?:s)?', 'biseau(x)?', 'strie(?:s)?', 'veine(?:s)?', 'filet(?:s)?', 'filon(?:s)?',
              'intercalé(?:s|e|es)?', 'intercalation(?:s)?', 'interstratifié(?:s|e|es)?', 'tacheté(?:s|e|es)?',
              'bande(?:s)?', 'bariolé(?:e|es)?'],

    'material': ['laitier', 'Scories', 'béton', 'scorie(?:s)?', 'Ballast', 'Laitier', 'Géotextile', 'Scorie',
                 'g[e|é]otextile(?:s)?', 'Ballasts', 'ballast(?:s)?', 'Béton'],

    'modifier': ['Sableu(?:x|se|ses)?', 'shisteu(?:x|se)', 'caillouteu(?:x|se)', 'Charboneu(?:x|se|ses)?',
                 'Schisteu(?:x|se|ses)?', 'sableu(?:x|se)', 'argileu(?:x|se)', 'graveleu(?:x|se)', 'pierreu(?:x|se)',
                 'Argileu(?:x|se|ses)?', 'silteu(?:x|se)', 'Cendreu(?:x|se|ses)?', 'Charbonneu(?:x|se|ses)?',
                 'Tourbeu(?:x|se|ses)?', 'Limoneu(?:x|se|ses)?', 'bitumineu(?:x|se)', 'saturé(?:e|es)?',
                 'Gréseu(?:x|se|ses)?', 'boueu(?:x|se)'],

    'grainsize': ['(?:pluri(?:-)?)?(?:d[e|é]ci|centi|milli)?m[e|é]trique(?:s)?', 'vf(?:-)?', 'f(?:-)?', '\\d+ mm(?:-)?',
                  'c(?:-)?', 'vc', 'très fin(?:e à)?', 'fin(?:e|s|es à)?', 'moyen(?:ne à)?',
                  'grossi(?:er|ers|ère|ères à)?', 'très grossi(?:er|ère)', 't fin(?:e|s|es à)?', 'moy(?: à)?',
                  'moy.(?: à)?', 't grossier(?:s)?', 'granules?', 'cailloux?', 'galets?', 'blocs rocheux?'],

    'quantity': ['beaucoup', 'peu', 'moins', 'plusieurs', 'fragment(?:s)?', 'impurité(?:es)', 'abondant(?:e|es)',
                 'mineur', 'quelques', 'rare', 'flocon(?:s)?', 'trace(?:s)', '[-.\\d]+%', '[-.\\d]+pc',
                 '[-.\\d]+pourcent'],

    'Pollutant': ['naphtalène', 'HAP', 'huile(?:s)?'],

    'synonyms': {'mort-terrain': ['terre'], 'Anhydrite': ['Gypse'], 'Sel': ['Halite', 'Sylvite']},

    'splitters': [' avec ', ' de ', ' cont(?:ient|enant) ', '\\. '],

    'parts_of_speech': {'noun': ['lithology'], 'adjective': ['colour', 'grainsize', 'modifier'],
                        'subordinate': ['quantity']},

    'abbreviations': {'Argilo': 'Argile', 'Sablo': 'sable'},

    'colour': ['Bleu(?:e|es|âtre|âtres)?', 'Blanc(?:he|hes|hâtre|hâtres)?', 'Gris(?:e|es|âtre|âtres)?',
               'Jaun(?:e|es|âtre|âtres)?', 'Marron', 'Noir(?:e|es|âtre|âtres)?', 'Ros(?:e|es|âtre|âtres)?',
               'Roug(?:e|es|âtre|âtres)?', 'Ver(?:t|te|tes|dâtre|dâtres)?', 'Violet(?:te|tes)?', 'Orange', 'Jaune-gris',
               'Blanc-gris', 'Brun-jaune', 'Gris-noir', 'Rouge-orange', 'Noir-brun', 'Jaune-vert', 'Vert-ocre',
               'Verdâtre-brun', 'Grise-verdâtre', 'Noir-rouge', 'beige', 'Jaune-kaki', 'Brun-gris', 'Jaune-ocre',
               'Vert-de-gris', 'Gris-rouge', 'Aigue-marine', 'Azur', 'Azur clair', 'Azurin', 'Bleu acier',
               'Bleu ardoise', 'Bleu barbeau', 'Bleu bleuet', 'Bleu bondi', 'Bleu céleste', 'Bleu céruléen',
               'Bleu charrette', 'Bleu charron', 'Bleu ciel', 'Bleu cobalt', 'Bleu de Berlin', 'Bleu de France',
               'Bleu de minuit', 'Bleu de Prusse', 'Bleu denim', 'Bleu des mers du sud', 'Bleu dragée', 'Bleu égyptien',
               'Bleu électrique', 'Bleu guède', 'Bleu horizon', 'Bleu majorelle', 'Bleu marine', 'Bleu maya',
               'Bleu minéral', 'Bleu nuit', 'Bleu outremer', 'Bleu paon', 'Bleu persan', 'Bleu pétrole', 'Bleu roi',
               'Bleu saphir', 'Bleu sarcelle', 'Bleu smalt', 'Bleu tiffany', 'Bleu turquin', 'Cæruléum', 'Canard',
               'Cérulé', 'Cyan', 'Fumée', 'Givré', 'Indigo', 'Indigo du web', 'Klein', 'Lapis-lazuli', 'Lavande',
               'Pastel', 'Pervenche', 'Turquoise', 'Blanc', 'Albâtre', 'Azur brume', 'Beige clair',
               'Blanc cassé', 'Blanc céruse', 'Blanc crème', "Blanc d'argent", 'Blanc de lait', 'Blanc de lin',
               'Blanc de platine', 'Blanc de plomb', 'Blanc de Saturne', 'Blanc de Troyes', 'Blanc de Zinc',
               "Blanc d'Espagne", "Blanc d'ivoire", 'Blanc écru', 'Blanc lunaire', 'Blanc neige', 'Blanc opalin',
               'Blanc-bleu', "Coquille d'oeuf", 'Cuisse de nymphe', 'Brun', 'Acajou', 'Alezan', 'Ambre', 'Auburn',
               'Basané', 'Beige', 'Beigeasse', 'Bistre', 'Bitume', 'Blet', 'Brique', 'Bronze', 'Brou de noix', 'Bureau',
               'Cacao', 'Cachou', 'Café', 'Café au lait', 'Cannelle', 'Caramel', 'Châtaigne', 'Châtain', 'Chaudron',
               'Chocolat', 'Citrouille', 'Fauve', 'Feuille-morte', 'Grège', 'Gris de maure', 'Lavallière', 'Marron',
               'Mordoré', 'Noisette', 'Orange brûlée', 'Puce', 'Rouge bismarck', 'Rouge tomette', 'Rouille',
               'Sang de boeuf', 'Senois', 'Sépia', 'Tabac', 'Terre de Sienne', "Terre d'ombre", 'Vanille', 'Gris',
               'Ardoise', 'Argent', 'Bis', 'Céladon', 'Etain oxydé', 'Etain pur', 'Gris acier', 'Gris anthracite',
               'Gris de Payne', 'Gris fer', 'Gris Fer', 'Gris Perle', 'Gris souris', 'Gris tourterelle', 'Mastic',
               'Pinchard', 'Plomb', 'Rose Mountbatten', 'Taupe', 'Tourdille', 'Jaune', 'Aurore', 'Beurre',
               'Beurre frais', 'Blé', 'Blond', "Boutton d'or", 'Bulle', "Caca d'oie", 'Chamois', 'Champagne', 'Chrome',
               'Citron', 'Flave', 'Fleur de soufre', 'Gomme-gutte', 'Jaune auréolin', 'Jaune banane', 'Jaune canari',
               'Jaune chartreuse', 'Jaune de cobalt', 'Jaune de Naples', "Jaune d'or", 'Jaune impérial', 'Jaune mimosa',
               'Jaune moutarde', 'Jaune nankin', 'Jaune olive', 'Jaune paille', 'Jaune poussin', 'Maïs', 'Mars', 'Miel',
               'Ocre jaune', 'Ocre rouge', 'Or', 'Orpiment', 'Poil de chameau', 'Queue de vache', 'Safran',
               'Soufre', 'Topaze', 'Vénitien', 'Noir', 'Aile de corbeau', 'Cassis', 'Dorian', 'Ebène', 'Noir animal',
               'Noir charbon', "Noir d'aniline", 'Noir de carbone', 'Noir de fumée', 'Noir de jais', "Noir d'encre",
               "Noir d'ivoire", 'Noiraud', 'Réglisse', 'Orange', 'Abricot', 'Bisque', 'Carotte', 'Corail', 'Cuivre',
               'Mandarine', 'Melon', 'Orangé', 'Roux', 'Saumon', 'Tangerine', 'Tanné', 'Ventre de biche', 'Rose',
               'Cerise', 'Chair', 'Framboise', 'Fushia', 'Héliotrope', 'Incarnadin', 'Magenta', 'Magenta foncé',
               'Magenta fushia', 'Mauve', 'Pêche', 'Rose balais', 'Rose bonbon', 'Rose dragée', 'Rose thé', 'Rose vif',
               'Rouge', 'Amarante', 'Bordeaux', 'Ecarlate', 'Fraise', 'Fraise écrasée', 'Grenadine', 'Grenat',
               'Incarnat', 'Nacarat', 'Passe-velours', 'Pourpre', 'Prune', 'Rouge alizarine', 'Rouge anglais',
               'Rouge bourgogne', 'Rouge capucine', 'Rouge cardinal', 'Rouge carmin', 'Rouge cinabre',
               'Rouge coquelicot', 'Rouge cramoisi', "Rouge d'Andrinople", "Rouge d'aniline", 'Rouge de falun',
               'Rouge de mars', 'Rouge écrevisse', 'Rouge feu', 'Rouge garance', 'Rouge groseille', 'Rouge ponceau',
               'Rouge rubis', 'Rouge sang', 'Rouge tomate', 'Rouge turc', 'Rouge vermillon', 'Rouge-violet',
               'Terracotta', 'Vermeil', 'Zizolin', 'Vert', 'Asperge', 'Glauque', 'Hooker', 'Jade', 'Kaki', 'Menthe',
               "Menthe à l'eau", 'Sinople', 'Vert absinthe', 'Vert amande', 'Vert anglais', 'Vert anis', 'Vert avocat',
               'Vert bouteille', 'Vert chartreuse', 'Vert citron', 'Vert de chrome', 'Vert de gris', 'Vert de vessie',
               "Vert d'eau", 'Vert émeraude', 'Vert empire', 'Vert épinard', 'Vert gazon', 'Vert impérial', 'Vert kaki',
               'Vert lichen', 'Vert lime', 'Vert malachite', 'Vert mélèse', 'Vert militaire', 'Vert mousse',
               'Vert olive', 'Vert opaline', 'Vert perroquet', 'Vert pin', 'Vert pistache', 'Vert poireau',
               'Vert pomme', 'Vert prairie', 'Vert prasin', 'Vert printemps', 'Vert sapin', 'Vert sauge',
               'Vert smaragdin', 'Vert tilleul', 'Vert véronèse', 'Vert viride', 'Violet', 'Améthyste', 'Aubergine',
               'Byzantin', 'Byzantium', 'Colombin', 'Glycine', 'Gris de lin', 'Lie de vin', 'Lilas', 'Orchidée',
               'Parme', "Violet d'évêque", 'Violine', 'rouge', 'orange gris', 'verdâtre', 'gris', 'brun', 'blanc',
               'noire', 'brique', 'sable beige', 'brun beige', 'noir verdâtre', 'jaune', 'noir', 'verdâtre brun']
}
lexicon_fr = Lexicon(LEXICON_FR)

#======================= LEGENDES ============================
POLLUTANT_MEMORIS = """colour,width,component pollutant
#00FF00, None, vr,
#FFA500, None, vs,
#FF0000, None, vi,
#888888, None, None,
"""

pollutant_memoris = Legend.from_csv(text=POLLUTANT_MEMORIS, )

LITHOLOGY_MEMORIS = """colour,width, hatch, component lithology
#FFFFE9, None, None, Matériau(?:x)? meuble(?:s)?,
#FFFFD5, None, '....', Alluvion(?:s)?,
#331100, None, None, Boue(?:s)?,
#D3B798, None, 'v', Remblai(?:s)?,
#FFCC99, None, None, Tourbe(?:s)?,
#FFEAA7, None, None, Gypse(?:s)?,
#00151A, None, None, Houille(?:s)?,
#798732, None, '-.', Limon(?:s)?,
#FFCB23, None, '..', Sable(?:s)?,
#ECB400, None, None, Gravier(?:s)?,
#ACE4C8, None, None, Silt(?:s)?,
#D5E6CC, None, '---', Argile(?:s)?,
#92DCB7, None, None, Bentonite(?:s)?,
#BBFFDD, None, '--', Schiste(?:s)?,
#95FFCA, None, None, Argilite(?:s)?,
#D6FE9A, None, None, Siltite(?:s)?,
#E1F0D8, None, None, Tuffeau(?:s)?,
#69CF9C, None, None, Silex,
#B7D9CC, None, None, Conglomérat(?:s)?,
#019CCD, None, None, Carbonate(?:s)?,
#149EF8, None, None, Calcaire(?:s)?,
#0094F8, None, None, Dolomite(?:s)?,
#0094F9, None, None, Dolomie(?:s)?,
#DEEFFE, None, None, Craie(?:s)?,
#AAC2C8, None, None, Chert(?:s)?,
#000000, None, None, Charbon(?:s)?,
#7BA1A8, None, None, Marne(?:s)?,
#FFFFFF, None, /|\, Inconnu
"""
lithology_memoris = Legend.from_csv(text=LITHOLOGY_MEMORIS)


LEGEND_FR = """colour,width,component lithology
#FFFFE9, None, Matériau(?:x)? meuble(?:s)?,
#FFFFD5, None, Alluvion(?:s)?,
#331100, None, Boue(?:s)?,
#F5E1BD, None, Lœss,
#F5E1BD, None, Loess,
#D6C59E, None, Cendre(?:s)? volcanique(?:s)?,
#E1E3C3, None, Colluvion(?:s)?,
#D3CA9F, None, Lahar(?:s)?,
#FFEEBF, None, Moraine(?:s)?,
#FFCC99, None, Tourbe(?:s)?,
#FFEAA7, None, Gypse(?:s)?,
#FFDB67, None, Houille(?:s)?,
#FFD345, None, Limon(?:s)?,
#FFCB23, None, Sable(?:s)?,
#ECB400, None, Gravier(?:s)?,
#CFEFDF, None, Roche(?:s)? sédimentaire(?:s)?,
#D9FDD3, None, Roche(?:s)? clastique(?:s)?,
#ACE4C8, None, Silt(?:s)?,
#D5E6CC, None, Argile(?:s)?,
#92DCB7, None, Bentonite(?:s)?,
#C0D0C0, None, Diatomite(?:s)?,
#DBFEBC, None, Molasse(?:s)?,
#BBFFDD, None, Schiste(?:s)?,
#95FFCA, None, Argilite(?:s)?,
#D6FE9A, None, Siltite(?:s)?,
#E1F0D8, None, Tuffeau(?:s)?,
#CDFFD9, None, Grès,
#CBEFCE, None, Arénite(?:s)?,
#A6FCAA, None, Orthoquartzite(?:s)?,
#7DFFE3, None, Calcarénite(?:s)?,
#B8EAC3, None, Arkose(?:s)?,
#BDDBF1, None, Wacke(?:s)?,
#69CF9C, None, Silex,
#90A565, None, Radiolarite(?:s)?,
#B7D9CC, None, Conglomérat(?:s)?,
#A7BA86, None, Brèche(?:s)? sédimentaire(?:s)?,
#BCC0C5, None, Dolomie(?:s)?,
#8DBECD, None, Olistostrome(?:s)?,
#A5AAAD, None, Carbonatite(?:s)?,
#019CCD, None, Carbonate(?:s)?,
#149EF8, None, Calcaire(?:s)?,
#0094F8, None, Dolomite(?:s)?,
#BFE3DC, None, Phosphorite(?:s)?,
#DEEFFE, None, Craie(?:s)?,
#9ACEFE, None, Évaporite(?:s)?,
#AAC2C8, None, Chert(?:s)?,
#C0AEB6, None, Alios,
#B99598, None, Radiolarite(?:s)?,
#98004C, None, Exhalite(?:s)?,
#6E4900, None, Charbon(?:s)?,
#D9C2A3, None, Marne(?:s)?,
#FFEFF3, None, Roche(?:s)? plutonique(?:s)?,
#FFC8BF, None, Aplite(?:s)?,
#FFE1E8, None, Porphyre(?:s)?,
#FDCFCF, None, Lamprophyre(?:s)?,
#FFD1DC, None, Pegmatite(?:s)?,
#FC6E7C, None, Granitoïde(?:s)?,
#FC5262, None, Granite(?:s)? alcalin(?:s)?,
#FB2338, None, Granite(?:s)?,
#F43C6C, None, Granite(?:s)? péralumineux,
#F41A87, None, Granite(?:s)? métallineux,
#DD2972, None, Granite(?:s)? subalumineux,
#E45891, None, Granite(?:s)? peralkaline(?:s)?,
#E979A6, None, Granodiorite(?:s)?,
#FF6F6B, None, Tonalite(?:s)?,
#FFB3C5, None, Trondhjemite(?:s)?,
#F8BEAE, None, Syénite(?:s)? alcaline(?:s)?,
#F9B5BB, None, Quartz syenite(?:s)?,
#FFA7BC, None, Syenite(?:s)?,
#FF6388, None, Quartz monzonite(?:s)?,
#FF275A, None, Monzonite(?:s)?,
#FFCCC5, None, Quartz monzodiorite(?:s)?,
#FFA99D, None, Monzodiorite(?:s)?,
#FF6F5B, None, Diorite(?:s)? de quartz(?:s)?,
#FF3317, None, Diorite(?:s)?,
#E81C00, None, Diabase(?:s)?,
#FF95AE, None, Gabbroïde(?:s)?,
#FF819F, None, Quartz monzogabro(?:s)?,
#FFD6D1, None, Monzogabbro(?:s)?,
#EDA7CA, None, Quartz gabbro(?:s)?,
#E993BE, None, Gabbro(?:s)?,
#FF85FB, None, Gabbronorite(?:s)?,
#E377AD, None, Norite(?:s)?,
#FFBFCE, None, Troctolite(?:s)?,
#FFA3B9, None, Anorthosite(?:s)?,
#FF6F91, None, Roche(?:s)? intrusif alcalique(?:s)?,
#FF1B51, None, Népheline(?:s)?,
#E80037, None, Roche(?:s)? intrusive ultramafique(?:s)?,
#CE0031, None, Péridotite(?:s)?,
#940023, None, Kimberlite(?:s)?,
#C1010A, None, Pyroxénite(?:s)?,
#A30109, None, Hornblendite(?:s)?,
#750107, None, Carbonatite intrusive(?:s)?,
#F9D3D3, None, Roche(?:s)? volcanique(?:s)?,
#FFE5F3, None, Roche(?:s)? volcanique(?:s)? vitreuse(?:s)?,
#FFD1EA, None, Obsidienne(?:s)?,
#FFC3F8, None, Vitrophyre(?:s)?,
#FFC3E4, None, Pierre(?:s)? ponce(?:s)?,
#FFEDBF, None, Pyroclastique(?:s)?,
#FFEFD9, None, Tuf(?:s)?,
#FFE5C3, None, Ignimbrite(?:s)?,
#FFD59D, None, Brèche(?:s)? volcanique(?:s)?,
#FFC10B, None, Coulée(?:s)? de lave(?:s)?,
#F48B00, None, Roche(?:s)? volcanique(?:s)? felsique(?:s)?,
#FEDC7E, None, Rhyolite(?:s)? alcaline(?:s)?,
#FED768, None, Rhyolite(?:s)?,
#FEC62A, None, Rhyodacite(?:s)?,
#FECDAC, None, Dacite(?:s)?,
#FEB786, None, Trachyte(?:s)? alcaline(?:s)?,
#FEA060, None, Trachyte(?:s)?,
#FE8736, None, Quartz latite(?:s)?,
#FE7518, None, Latite(?:s)?,
#EB6001, None, Roche(?:s)? volcanique(?:s)? intermédiaire(?:s)?,
#C95201, None, Trachyandesite(?:s)?,
#B14801, None, Andésite(?:s)?,
#933C01, None, Roche(?:s)? mafique(?:s)? volcanique(?:s)?,
#ECD5C6, None, Trachybasalte(?:s)?,
#DDB397, None, Basalte(?:s)?,
#D39D79, None, Tholite(?:s)?,
#C68050, None, Hawaiite(?:s)?,
#A96537, None, Basalte(?:s)? alcalin(?:s)?,
#854F2B, None, Roche(?:s)? alcalique(?:s)? volcanique(?:s)?,
#5F391F, None, Phonolite(?:s)?,
#C24100, None, Téphrite(?:s)?,
#A03500, None, Komatiite(?:s)?,
#6E2500, None, Carbonatite volcanique(?:s)?,
#E6CDFF, None, Roche(?:s)? métamorphique(?:s)?,
#EAAFFF, None, Hornfels,
#E9FFE9, None, Roche(?:s)? métasédimentaire(?:s)?,
#C9FFC9, None, Méta-argilite(?:s)?,
#A7A7FF, None, Ardoise(?:s)?,
#9FFF9F, None, Quartzite(?:s)?,
#7DFF7D, None, Méta-conglomérat(?:s)?,
#0000FF, None, Marbre(?:s)?,
#FFA7FF, None, Roche(?:s)? métavolcanique(?:s)?,
#FF8DFF, None, Roche(?:s)? métavolcanique felsique(?:s)?,
#FF57FF, None, Méta-rhyolite(?:s)?,
#FE6700, None, Kératophyre(?:s)?,
#C9557E, None, Roche(?:s)? métavolcanique(?:s)? intermédiaire(?:s)?,
#B93B68, None, Roche(?:s)? métavolcanique(?:s)? mafique(?:s)?,
#872B4C, None, Méta-basalte(?:s)?,
#FF0000, None, Spilite(?:s)?,
#008000, None, Pierre(?:s)? verte(?:s)?,
#EDEDF3, None, Phyllite(?:s)?,
#DBDBE7, None, Schiste(?:s)?,
#B1B1B1, None, Micaschiste(?:s)?,
#969696, None, Schiste(?:s)? pélitique(?:s)?,
#A2A2C0, None, Schiste(?:s)? de quartz-feldspar(?:s)?,
#B4CFE4, None, Schiste(?:s)? de silicate de calcul(?:s)?,
#B6B6CE, None, Schiste(?:s)? d'amphibole(?:s)?,
#ABFFFF, None, Granofels,
#79FFFF, None, Gneiss,
#0FFFFF, None, Gneiss felsique(?:s)?,
#00DBD6, None, Gneiss granitique(?:s)?,
#00A4A0, None, Gneiss biotite(?:s)?,
#007673, None, Gneiss mafique(?:s)?,
#33CCCC, None, Orthogneiss,
#2DB6B3, None, Paragneiss,
#AC0000, None, Migmatite(?:s)?,
#AC7F50, None, Amphibolite(?:s)?,
#84613E, None, Granulite(?:s)?,
#FF4FFF, None, Eclogite(?:s)?,
#EC00EC, None, Greisen(?:s)?,
#6600CC, None, Skarn(?:s)?,
#005C00, None, Serpentinite(?:s)?,
#C600C6, None, Roche(?:s)? tectonique(?:s)?,
#9C009C, None, Tectonite(?:s)?,
#6A006A, None, Tectonite(?:s)? mélange(?:s)?,
#2A002A, None, Brèche(?:s)? tectonique(?:s)?,
#F4FFD5, None, Cataclasite(?:s)?,
#339966, None, Phyllonite(?:s)?,
#D0CBB0, None, Mylonite(?:s)?,
#B0A778, None, Basanite(?:s)?
"""

legend_fr = Legend.from_csv(text=LEGEND_FR)

#======================= COULEURS ============================ 

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
