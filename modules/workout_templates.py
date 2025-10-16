# Template workout basati sulla scheda di Matteo Zaramella

def _detect_peso_mode(serie):
    """
    Determina automaticamente il modo peso in base alle ripetizioni.
    Se tutte le serie hanno lo stesso target di ripetizioni -> 'unico'
    Altrimenti -> 'diverso'
    """
    if not serie or len(serie) <= 1:
        return 'unico'

    # Controlla se tutte le serie sono identiche
    first = serie[0]
    if all(s == first for s in serie):
        return 'unico'
    else:
        return 'diverso'

WORKOUT_TEMPLATES = {
    'A': {
        'nome': 'WORKOUT A - Petto, Tricipiti e Gambe',
        'esercizi': [
            {'nome': 'EXTRAROTAZIONE MANUBRI', 'serie': ['15', '12', '12'], 'categoria': 'Riscaldamento', 'peso_mode': 'diverso'},
            {'nome': 'CROCI PANCA 30°', 'serie': ['10', '10', '10'], 'categoria': 'Petto e Tricipiti', 'peso_mode': 'unico'},
            {'nome': 'DISTENSIONI PANCA PIANA', 'serie': ['10', '8', '6', '4'], 'categoria': 'Petto e Tricipiti', 'peso_mode': 'diverso'},
            {'nome': 'TRICIPITI 2 MANUBRI', 'serie': ['10', '10', '10'], 'categoria': 'Petto e Tricipiti', 'peso_mode': 'unico'},
            {'nome': 'TRICIPITI BILAN PANCA 30° alla nucca', 'serie': ['10', '8', '6', '6'], 'categoria': 'Petto e Tricipiti', 'peso_mode': 'diverso'},
            {'nome': 'PAUSA + BIKE', 'serie': ["3'"], 'categoria': 'Pausa', 'skip_peso': True},
            {'nome': 'LEG EXTENSION', 'serie': ['15', '12', '10'], 'categoria': 'Gambe', 'peso_mode': 'diverso'},
            {'nome': 'AFFONDI DUE MANUBRI SINGOLI', 'serie': ['12', '10', '8', '8'], 'categoria': 'Gambe', 'peso_mode': 'diverso'},
            {'nome': 'CRUNCH', 'serie': ['30', '30', '30'], 'categoria': 'Core', 'skip_peso': True},
            {'nome': 'STRETCHING', 'serie': [], 'categoria': 'Core', 'skip_peso': True, 'skip_form': True},
        ]
    },
    'B': {
        'nome': 'WORKOUT B - Bicipiti, Dorsali e Spalle',
        'esercizi': [
            {'nome': 'EXTRAROTAZIONE MANUBRI', 'serie': ['15', '15', '15'], 'categoria': 'Riscaldamento', 'peso_mode': 'unico'},
            {'nome': 'BICIPITI MAN. ALTER. Rotaz.compl.', 'serie': ['10', '10', '10'], 'categoria': 'Bicipiti', 'peso_mode': 'unico'},
            {'nome': 'BICIPITI BILANCIERE', 'serie': ['10', '8', '6', '6'], 'categoria': 'Bicipiti', 'peso_mode': 'diverso'},
            {'nome': 'PULL OVER BILANC-PRESA INV.', 'serie': ['12', '12', '12'], 'categoria': 'Dorsali', 'peso_mode': 'unico'},
            {'nome': 'LAT MACHINE trazibar', 'serie': ['12', '10', '8', '8'], 'categoria': 'Dorsali', 'peso_mode': 'diverso'},
            {'nome': 'ALZATE FRONTALI BILANCIERE', 'serie': ['12', '12', '12'], 'categoria': 'Spalle', 'peso_mode': 'unico'},
            {'nome': 'LENTO MANUBRI CON ROTAZIONE', 'serie': ['12', '10', '8', '15'], 'categoria': 'Spalle', 'peso_mode': 'diverso'},
            {'nome': 'GINOC.ALPETTO ALLE PARALLELE', 'serie': ['30', '30', '30'], 'categoria': 'Core', 'skip_peso': True},
            {'nome': 'STRETCHING', 'serie': [], 'categoria': 'Core', 'skip_peso': True, 'skip_form': True},
        ]
    },
    'C': {
        'nome': 'WORKOUT C - Full Body',
        'esercizi': [
            {'nome': 'RUN', 'serie': ["5'"], 'categoria': 'Cardio', 'skip_peso': True},
            {'nome': 'TOP', 'serie': ["3'"], 'categoria': 'Cardio', 'skip_peso': True},
            {'nome': 'DISTENSIONI PANCA ALTA', 'serie': ['8-10', '8-10', '8-10', '8-10'], 'categoria': 'Petto e Dorso', 'peso_mode': 'unico'},
            {'nome': 'TRAZIONI (CON AIUTO)', 'serie': ['MAX', 'MAX', 'MAX', 'MAX'], 'categoria': 'Petto e Dorso', 'skip_peso': True},
            {'nome': 'PAUSA', 'serie': [], 'categoria': 'Pausa', 'skip_peso': True, 'skip_form': True},
            {'nome': 'SQUAT', 'serie': ['10-8', '10-8', '10-8', '10-8'], 'categoria': 'Gambe', 'peso_mode': 'unico'},
            {'nome': 'HYPERXTENSION', 'serie': ['20', '20', '20'], 'categoria': 'Core', 'skip_peso': True},
            {'nome': 'CRUNCH DOPPIO', 'serie': ['25', '25', '25'], 'categoria': 'Core', 'skip_peso': True},
            {'nome': 'STRETCHING', 'serie': [], 'categoria': 'Core', 'skip_peso': True, 'skip_form': True},
        ]
    }
}

def get_workout_template(workout_type):
    """Restituisce il template del workout richiesto"""
    return WORKOUT_TEMPLATES.get(workout_type.upper(), None)

def get_all_workout_types():
    """Restituisce tutti i tipi di workout disponibili"""
    return [{'type': key, 'nome': value['nome']} for key, value in WORKOUT_TEMPLATES.items()]
