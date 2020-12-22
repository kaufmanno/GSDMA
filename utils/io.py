import re
from striplog import Striplog, Lexicon
from core.orm import BoreholeOrm, PositionOrm


def striplog_from_text(filename, lexicon=Lexicon.default()):
    """ creates a Striplog object from a las or flat text file
    
    Parameters
    ----------
    Lexicon : dict
              default = default lexicon included in striplog
              
    Returns
    -------
    strip: striplog object
    
 
    """

    if re.compile(r".+\.las").match(filename):
        print(f"File {filename:s} OK! Creation of the striplog ...")
        with open(filename, 'r') as las3:
            strip = Striplog.from_las3(las3.read(), lexicon)

    elif re.compile(r".+\.(csv|txt)").match(filename):
        print(f"File {filename:s} OK! Creation of the striplog ...")
        f = re.DOTALL | re.IGNORECASE
        regex_data = r'start.+?\n(.+?)(?:\n\n+|\n*\#|\n*$)'  # retrieve data of BH

        pattern = re.compile(regex_data, flags=f)
        with open(filename, 'r') as csv:
            text = pattern.search(csv.read()).group(1)
            text = re.sub(r'[\t]+', ';', re.sub(r'(\n+|\r\n|\r)', '\n', text.strip()))
            strip = Striplog.from_descriptions(text, dlm=';', lexicon=lexicon)

    else:
        print("Error! Please check the file extension !")
        raise

    return strip


def boreholes_from_files(borehole_dict=None):
    """Creates a list of BoreholeORM objects from flat text or las files
    
    Parameters
    ----------
    boreholes_dict: dict
                    
                    
                 
    Returns
    -------
    boreholes: list
               boreholes object
    components: dict
                dictionnary containing ID and component
    
    
    """

    int_id = 0
    bh_id = 0
    boreholes = []
    comp_id = 0
    pos_id = 0
    component_dict = {}
    components = {}

    if borehole_dict is not None:
        for bh, filename in borehole_dict.items():
            strip = striplog_from_text(filename)

            interval_number = 0
            boreholes.append(BoreholeOrm(id=bh))
            for c in strip.components:
                if c not in component_dict.keys():
                    component_dict.update({c: comp_id})
                    comp_id += 1

            d = {}
            for interval in strip:
                top = PositionOrm(id=pos_id, upper=interval.top.upper, middle=interval.top.middle,
                                  lower=interval.top.lower)
                base = PositionOrm(id=pos_id + 1, upper=interval.base.upper, middle=interval.base.middle,
                                   lower=interval.base.lower)
                d.update({int_id: {'description': interval.description, 'interval_number': interval_number, 'top': top,
                                   'base': base}})
                interval_number += 1
                int_id += 1
                pos_id += 2
            boreholes[bh_id].intervals_values = d
            bh_id += 1
        components = {v: k for k, v in component_dict.items()}

    return boreholes, components
