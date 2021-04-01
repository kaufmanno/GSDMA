"""
Definition de quelques valeurs par défault pour les descriptions de cuttings.
:copyright: 2020 O. Kaufmann & Y. N'DEPO
"""
#--------------------- JE DOIS MODIFIER CE QUI SUIT ------------------------------
# =========== LEXIQUE ===========
LEXICON = {
    'lithology': ['Glauconite', 'Cendre', 'Alios', 'Cargneule', 'Tuffeau', 'Cipolin', 'Argile', 'tillite', 'Poudingue', 'Radiolarite', 'Carbonatite', 'Tourbe', 'Arkose', 'Grès', 'Phonolite', 'Silex', 'Cinérite', 'Monzonite', 'Conglomérat', 'Quartzite', 'Anatectite', 'Pierre coquillère', 'Ophite', 'Pierre coquillière', 'Syénite', 'poudingue', 'Bentonite', 'Trachyte', 'Micaschiste', 'Marbre', "Granite d'anatexie", 'Porphyre', 'Phtanite', 'Marne', 'Cinérites', 'Tuf volcanique', 'Pegmatite', 'Molasse ', 'Lapillis', 'Halite', 'Calcaire', 'Kimberlite', 'Amphibolite', 'Diatomite', 'Leptynite', 'Lignite', 'Andésite', 'Ignimbrite', 'Rhyolite', 'Dolérite', 'Gneiss', 'Pyroxénite', 'Craie', 'Bauxite', 'Basalte', 'Gabbro', 'Aplite', 'Dolomie', 'Sable', 'Glauconie', 'Ardoise', 'Péridotite', 'Cendres', 'anhydrite', 'Brèche', 'Granite', 'Ponce', 'brèche', 'Gravier', 'Houille', 'Kersantite', 'Dacite', 'Anthracite', 'Schiste', 'Jaspe', 'Molasse', 'éclogite', 'Tuf', 'Gypse', 'Combarbalite', 'Diorite', 'Obsidienne', 'Silcrète'],
    'material':['Remblai', 'Béton', 'Laitier', 'Scories', 'Brique', 'Briquaillon', 'Caillou', 'Pierre'],
    'modifier': ['argileux','-(\w+eu(?:x|se|ses)?)'],
    'quantity': [],
    'grainsize': [],
    'colour': ['Magenta', 'mauve', 'Argent', 'Gris', 'Bleu', 'vert', 'violet', 'Blanc', 'Jaune', 'Marron', 'Orange', 'Rose', 'Rouge', 'lie-de-vin', 'Noir', 'Turquoise', 'Beige'],
    'synonyms': {},
    'splitters': [' avec ', ' de ', ' cont(?:ient|enant) ', '\. '],
    'parts_of_speech': {'noun': ['lithology'], 'adjective': ['colour', 'grainsize', 'modifier'], 'subordinate': ['quantity']}
           }

