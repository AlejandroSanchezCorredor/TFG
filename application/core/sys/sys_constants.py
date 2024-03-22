from enum import Enum

# Weight / Mass
class WeightUnit:
    def __init__(self, name, code, symbol, equivalence):
        self.name = name
        self.code = code
        self.symbol = symbol
        self.equivalence = equivalence


# SOURCE: http://www.interenerstat.org/images/mass.jpg
class WeightCollection(Enum):
    KG = WeightUnit(name='kilograme', code='kg', symbol='kg', equivalence=1)
    MT = WeightUnit(name='metric tonne', code='mt', symbol='mt', equivalence=1000)
    LT = WeightUnit(name='long ton', code='lt', symbol='lt', equivalence=1016)
    ST = WeightUnit(name='short ton', code='st', symbol='st', equivalence=907.2)
    LB = WeightUnit(name='pound', code='lb', symbol='lb', equivalence=0.454)


MASS_UNIT_DEFAULT = WeightCollection.KG

def normalize_weight(mass_quantity, mass_unit, mass_conversion=MASS_UNIT_DEFAULT.value.code):
    _mass_value = None
    
    try:
        _mass_source = WeightCollection[mass_unit.upper()].value
        _mass_conversion = WeightCollection[mass_conversion.upper()].value
        _mass_value = mass_quantity * (_mass_source.equivalence / _mass_conversion.equivalence)
    except Exception as e:
        print(f"[EXCEPTION] {e}")

    return _mass_value, _mass_conversion.code
