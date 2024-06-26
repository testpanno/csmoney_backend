from enum import Enum

class ESkinType(Enum):

    # Main types
    KNIVES = "Knives"
    GLOVES = "Gloves"
    PISTOLS = "Pistols"
    SMGS = "SMGs"
    ASSAULT_RIFLES = "Assault Rifles"
    SNIPER_RIFLES = "Sniper Rifles"
    SHOTGUNS = "Shotguns"
    MACHINE_GUNS = "Machine guns"
    KEYS = "Keys"

    # Other types
    STICKER = "Sticker"
    CASE = "Case"
    GRAFFITI = "Graffity"
    MUSIC_KIT = "Music Kit"
    PIN = "Pin"
    AGENTS = "Agents"
    PATCH = "Patch"
    ZEUS = "Zeus"

class ESkinExterior(Enum):
    FACTORY_NEW = 'Factory New'
    MINIMAL_WEAR = 'Minimal Wear'
    FIELD_TESTED = 'Field-Tested'
    WELL_WORN = 'Well-Worn'
    BATTLE_SCARRED = 'Battle-Scarred'

class ESkinRarity(Enum):
    BASE_GRADE = "Base Grade"
    CONSUMER_GRADE = "Consumer Grade"
    INDUSTRIAL_GRADE = "Industrial Grade"
    MIL_SPEC_GRADE = "Mil-Spec Grade"
    RESTRICTED = "Restricted"
    CLASSIFIED = "Classified"
    COVERT = "Covert"

class ESkinPhase(Enum):
    PHASE_1 = "Phase 1"
    PHASE_2 = "Phase 2"
    PHASE_3 = "Phase 3"
    PHASE_4 = "Phase 4"
    EMERALD = "Emerald"
    SAPPHIRE = "Sapphire"
    RUBY = "Ruby"
    BLACK_PEARL = "Black Pearl"