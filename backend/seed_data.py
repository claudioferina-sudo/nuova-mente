"""Contenuti storici scriptati e revisionabili: fonti, missioni, pool M3."""

SOURCES = [
    {
        "source_id": "S01",
        "title": "Il Trattato di Versailles",
        "year": "1919",
        "tag": "strutturale",
        "body": "Firmato il 28 giugno 1919, impone alla Germania la responsabilita' della guerra (art. 231), riparazioni economiche, riduzione dell'esercito a 100.000 uomini, smilitarizzazione della Renania e perdite territoriali (Alsazia-Lorena, corridoio di Danzica). In Germania viene percepito come Diktat e alimenta il mito della 'pugnalata alle spalle'.",
    },
    {
        "source_id": "S02",
        "title": "La crisi del 1929 e la Grande Depressione",
        "year": "1929-1933",
        "tag": "strutturale",
        "body": "Il crollo di Wall Street interrompe i prestiti statunitensi che sostenevano l'economia di Weimar. In Germania la disoccupazione passa da 1,3 milioni (1929) a oltre 6 milioni (1932). Il collasso economico erode il consenso ai partiti democratici e spinge elettorato e ceti medi verso le forze antisistema.",
    },
    {
        "source_id": "S03",
        "title": "Ascesa del nazismo al potere",
        "year": "1930-1933",
        "tag": "politico",
        "body": "Il NSDAP passa dal 2,6% (1928) al 37,3% (luglio 1932). Il 30 gennaio 1933 Hitler e' nominato cancelliere da Hindenburg. Con l'incendio del Reichstag e la legge dei pieni poteri (marzo 1933) la Germania diventa una dittatura a partito unico.",
    },
    {
        "source_id": "S04",
        "title": "Riarmo tedesco e servizio militare obbligatorio",
        "year": "1935",
        "tag": "politico",
        "body": "Nel marzo 1935 Hitler denuncia le clausole militari di Versailles, reintroduce la coscrizione e annuncia la Luftwaffe. Nel giugno 1935 l'accordo navale anglo-tedesco legittima di fatto la violazione del trattato: primo segnale di cedimento delle potenze occidentali.",
    },
    {
        "source_id": "S05",
        "title": "Rimilitarizzazione della Renania",
        "year": "7 marzo 1936",
        "tag": "politico",
        "body": "Le truppe tedesche entrano nella zona smilitarizzata della Renania violando Versailles e Locarno. Francia e Gran Bretagna non reagiscono militarmente. L'impunita' rafforza la convinzione di Hitler che le democrazie non useranno la forza.",
    },
    {
        "source_id": "S06",
        "title": "Anschluss dell'Austria",
        "year": "12-13 marzo 1938",
        "tag": "politico",
        "body": "La Germania annette l'Austria dopo le pressioni su Schuschnigg. Nessuna sanzione internazionale. L'Italia, dopo l'avvicinamento dell'Asse (1936) e la guerra d'Etiopia, non si oppone come aveva fatto nel 1934.",
    },
    {
        "source_id": "S07",
        "title": "Conferenza di Monaco e appeasement",
        "year": "29-30 settembre 1938",
        "tag": "politico",
        "body": "Chamberlain, Daladier, Hitler e Mussolini concedono al Reich i Sudeti cecoslovacchi senza la presenza di Praga. Chamberlain parla di 'pace per il nostro tempo'. Nel marzo 1939 la Germania occupa Boemia e Moravia: l'appeasement e' fallito.",
    },
    {
        "source_id": "S08",
        "title": "Patto Molotov-Ribbentrop",
        "year": "23 agosto 1939",
        "tag": "immediata",
        "body": "Patto di non aggressione fra Germania e URSS firmato a Mosca il 23 agosto 1939, con protocollo segreto che divide la Polonia e assegna a Mosca Paesi baltici e Bessarabia. Neutralizza il rischio di guerra su due fronti e apre la strada all'invasione della Polonia una settimana dopo.",
    },
    {
        "source_id": "S09",
        "title": "Crisi di Danzica e invasione della Polonia",
        "year": "1 settembre 1939",
        "tag": "immediata",
        "body": "Dopo le richieste su Danzica e il corridoio, e la messinscena di Gleiwitz, la Wehrmacht invade la Polonia il 1 settembre 1939 senza dichiarazione di guerra. Il 3 settembre Gran Bretagna e Francia dichiarano guerra alla Germania.",
    },
    {
        "source_id": "S10",
        "title": "Crisi della Societa' delle Nazioni",
        "year": "1931-1937",
        "tag": "strutturale",
        "body": "L'invasione giapponese della Manciuria (1931) e l'aggressione italiana all'Etiopia (1935-36) mostrano l'incapacita' della Societa' delle Nazioni di applicare la sicurezza collettiva. Le sanzioni contro l'Italia sono parziali e inefficaci; Germania, Giappone e Italia escono dall'organizzazione.",
    },
    {
        "source_id": "S11",
        "title": "Guerra civile spagnola",
        "year": "1936-1939",
        "tag": "politico",
        "body": "L'intervento di Germania e Italia a fianco di Franco e il non intervento franco-britannico fanno della Spagna un laboratorio militare e diplomatico dell'Asse, consolidando l'alleanza Roma-Berlino e la sfiducia sovietica verso le democrazie.",
    },
    {
        "source_id": "S12",
        "title": "Patto d'Acciaio Italia-Germania",
        "year": "22 maggio 1939",
        "tag": "immediata",
        "body": "Alleanza militare offensiva fra Italia e Germania. L'Italia, non pronta militarmente, otterra' nel 1939 lo status di 'non belligeranza'. Il patto segna il passaggio dall'Asse politico a un vincolo di guerra.",
    },
]

# Missione 3: pool di 16 card, se ne estraggono 8 (4 remote + 4 immediate)
M3_POOL = [
    {"card_id": "C01", "text": "Il Trattato di Versailles e le sue clausole punitive (1919)", "category": "remota", "source_id": "S01"},
    {"card_id": "C02", "text": "La Grande Depressione e la disoccupazione di massa in Germania", "category": "remota", "source_id": "S02"},
    {"card_id": "C03", "text": "L'ascesa del NSDAP e la fine della Repubblica di Weimar", "category": "remota", "source_id": "S03"},
    {"card_id": "C04", "text": "Il fallimento della sicurezza collettiva della Societa' delle Nazioni", "category": "remota", "source_id": "S10"},
    {"card_id": "C05", "text": "Il riarmo tedesco e la coscrizione obbligatoria (1935)", "category": "remota", "source_id": "S04"},
    {"card_id": "C06", "text": "La rimilitarizzazione della Renania senza reazione francese (1936)", "category": "remota", "source_id": "S05"},
    {"card_id": "C07", "text": "La guerra civile spagnola come laboratorio dell'Asse (1936-39)", "category": "remota", "source_id": "S11"},
    {"card_id": "C08", "text": "Il nazionalismo economico e le politiche autarchiche degli anni Trenta", "category": "remota", "source_id": "S02"},
    {"card_id": "C09", "text": "Il patto Molotov-Ribbentrop del 23 agosto 1939", "category": "immediata", "source_id": "S08"},
    {"card_id": "C10", "text": "Le richieste tedesche su Danzica e il corridoio polacco (1939)", "category": "immediata", "source_id": "S09"},
    {"card_id": "C11", "text": "L'incidente inscenato di Gleiwitz (31 agosto 1939)", "category": "immediata", "source_id": "S09"},
    {"card_id": "C12", "text": "L'invasione della Polonia del 1 settembre 1939", "category": "immediata", "source_id": "S09"},
    {"card_id": "C13", "text": "La firma del Patto d'Acciaio (22 maggio 1939)", "category": "immediata", "source_id": "S12"},
    {"card_id": "C14", "text": "La garanzia anglo-polacca del 25 agosto 1939", "category": "immediata", "source_id": "S09"},
    {"card_id": "C15", "text": "L'occupazione di Boemia e Moravia (marzo 1939)", "category": "immediata", "source_id": "S07"},
    {"card_id": "C16", "text": "Il fallimento dei negoziati anglo-franco-sovietici (estate 1939)", "category": "immediata", "source_id": "S08"},
]

STRUCTURAL_KEYWORDS = [
    "versailles", "trattato", "riparazioni", "diktat", "crisi", "1929", "depressione",
    "disoccupazione", "economia", "economico", "societa' delle nazioni", "societa delle nazioni",
    "sicurezza collettiva", "nazionalismo", "autarchia", "weimar", "appeasement", "colonial",
]

VALID_CAUSE_KEYWORDS = STRUCTURAL_KEYWORDS + [
    "nazismo", "hitler", "nsdap", "dittatura", "riarmo", "renania", "anschluss", "austria",
    "monaco", "sudeti", "molotov", "ribbentrop", "danzica", "corridoio", "polonia",
    "patto d'acciaio", "patto d acciaio", "spagna", "franco", "gleiwitz", "espansionismo",
    "spazio vitale", "lebensraum", "revisionismo", "militarismo", "giappone", "manciuria",
]

MISSIONS = [
    {
        "mission_num": 1,
        "title": "Rilevazione dell'iper-semplificazione",
        "subtitle": "L'AI riduce tutto a una causa sola",
        "max_points": 20,
        "kind": "guided_text",
        "ai_output": "La Seconda Guerra Mondiale scoppio' perche' Hitler era un uomo malvagio che voleva conquistare il mondo. Non ci sono altre spiegazioni: senza di lui, l'Europa del 1939 sarebbe rimasta in pace.",
        "student_action": "Riscrivi il prompt in modo storicamente corretto ed elenca almeno TRE cause distinte del conflitto, di cui almeno una di tipo strutturale (economica, giuridica o istituzionale).",
        "unlock_trigger": "Almeno 3 cause distinte valide, di cui almeno 1 strutturale.",
        "hint": "Guarda le schede S01 (Versailles), S02 (crisi del 1929) e S10 (Societa' delle Nazioni): sono cause che esistevano prima di qualsiasi decisione personale.",
        "rubric": "Valuta se lo studente riconosce la fallacia dell'iper-semplificazione monocausale, elenca cause distinte e non ridondanti, e individua almeno una causa strutturale (economica, giuridica, istituzionale) distinguendola dalle scelte individuali.",
    },
    {
        "mission_num": 2,
        "title": "Fact-checking dell'allucinazione",
        "subtitle": "Una data e' sbagliata. Trovala e documentala",
        "max_points": 20,
        "kind": "factcheck",
        "ai_output": "Nel 1938 la Germania annette l'Austria con l'Anschluss. Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia, per dividere l'Europa orientale. Il 1 settembre 1939 la Wehrmacht invade la Polonia e il 3 settembre Francia e Gran Bretagna dichiarano guerra alla Germania.",
        "student_action": "Scegli l'affermazione falsa, evidenzia nel testo il segmento inesatto e cita la scheda del dossier che lo smentisce.",
        "unlock_trigger": "Item corretto E segmento evidenziato corretto E source_id citato.",
        "hint": "Il patto di non aggressione fra Berlino e Mosca precede l'invasione della Polonia, non la segue. Controlla la scheda S08.",
        "options": [
            {"option_id": "O1", "text": "Nel 1938 la Germania annette l'Austria con l'Anschluss.", "correct": False},
            {"option_id": "O2", "text": "Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia.", "correct": True},
            {"option_id": "O3", "text": "Il 1 settembre 1939 la Wehrmacht invade la Polonia.", "correct": False},
            {"option_id": "O4", "text": "Il 3 settembre 1939 Francia e Gran Bretagna dichiarano guerra alla Germania.", "correct": False},
        ],
        "false_segment": "Il patto Molotov-Ribbentrop viene firmato nel 1941, dopo l'invasione della Polonia",
        "expected_source_id": "S08",
        "rubric": "",
    },
    {
        "mission_num": 3,
        "title": "Cause remote contro cause immediate",
        "subtitle": "L'AI mette tutto sullo stesso piano",
        "max_points": 20,
        "kind": "dragdrop",
        "ai_output": "Elenco delle cause della guerra: Versailles, la crisi del 1929, il patto Molotov-Ribbentrop, Danzica, l'ascesa del nazismo, Gleiwitz. Sono tutte cause equivalenti e sullo stesso piano.",
        "student_action": "Classifica ogni card come CAUSA REMOTA (di lungo periodo, strutturale) o CAUSA IMMEDIATA (scintilla del 1939).",
        "unlock_trigger": "Almeno 6 card su 8 classificate correttamente.",
        "hint": "Chiediti: questo fatto agiva gia' da anni creando le condizioni, o e' un evento del 1938-39 che ha innescato il conflitto?",
        "rubric": "",
    },
    {
        "mission_num": 4,
        "title": "Confutazione dialettica",
        "subtitle": "Una tesi parziale, apparentemente ragionevole",
        "max_points": 20,
        "kind": "free_text",
        "ai_output": "La guerra fu causata unicamente dalla durezza del Trattato di Versailles: la Germania fu umiliata e non aveva altra scelta che reagire con le armi. Ogni altro fattore e' irrilevante.",
        "student_action": "Confuta la tesi: riconosci cosa contiene di vero, mostra cosa omette portando almeno DUE evidenze dal dossier (cita i source_id) e rendi esplicito il nesso logico fra le evidenze e la tua conclusione.",
        "unlock_trigger": "Tesi riconosciuta + almeno 2 evidenze dal dossier + nesso logico esplicito.",
        "hint": "Versailles e' una condizione, non una necessita': confronta S02 (crisi economica), S03 (scelte politiche interne) e S05/S07 (mancata reazione delle democrazie).",
        "rubric": "Valuta se lo studente: (a) riformula correttamente la tesi avversaria riconoscendone la parte fondata; (b) porta almeno due evidenze distinte tratte dal dossier con riferimento alle schede; (c) esplicita il nesso logico fra evidenze e conclusione, distinguendo condizione da causa necessaria.",
    },
    {
        "mission_num": 5,
        "title": "Verdetto finale ed Escape",
        "subtitle": "Redigi il rapporto che chiude il dossier",
        "max_points": 20,
        "kind": "report",
        "ai_output": "DOSSIER 1939 - CONCLUSIONE AUTOMATICA: causa unica individuata, responsabile unico individuato, caso chiuso. Confidenza: 99,8%.",
        "student_action": "Compila le quattro sezioni del rapporto e seleziona almeno TRE fonti del dossier a supporto.",
        "unlock_trigger": "4 sezioni compilate + almeno 3 fonti citate + nessuna contraddizione con M1-M4.",
        "hint": "Ogni sezione deve stare in piedi da sola: nella ricostruzione distingui i piani causali come hai fatto in M3.",
        "sections": [
            {"key": "contesto", "label": "Contesto storico", "placeholder": "Quali condizioni di lungo periodo pesavano sull'Europa fra le due guerre?"},
            {"key": "errori_ai", "label": "Errori dell'AI rilevati", "placeholder": "Quali errori hai smontato nelle missioni 1-4? (iper-semplificazione, allucinazione, appiattimento dei piani causali, tesi parziale)"},
            {"key": "ricostruzione", "label": "Ricostruzione corretta", "placeholder": "Distingui cause remote e cause immediate e collegale."},
            {"key": "verdetto", "label": "Verdetto argomentato", "placeholder": "Qual e' la tua conclusione e su quali fonti si regge?"},
        ],
        "rubric": "Valuta la coerenza interna del rapporto: distinzione fra piani causali, uso critico e incrociato di almeno tre fonti, assenza di affermazioni contraddittorie rispetto alle missioni precedenti, chiarezza del verdetto.",
    },
]

ROOM = {
    "room_id": "dossier-1939",
    "title": "Dossier 1939",
    "collection": "Seconda Guerra Mondiale",
    "tagline": "Un'AI ha chiuso il caso in 4 secondi. Ha sbagliato quasi tutto.",
    "briefing": "Il 1 settembre 1939 la Wehrmacht entra in Polonia. Ottantacinque anni dopo, un sistema di intelligenza artificiale ha prodotto un dossier che spiega quella guerra con una causa sola e una data sbagliata. Il tuo compito non e' rispondere a delle domande: e' smontare cinque output difettosi, uno alla volta, usando solo le schede del dossier. Ogni missione vale 20 punti. I punti diventano ore di PBL.",
    "missions_count": 5,
    "duration_min": 50,
}

CLASSES = [
    {"class_code": "5AIT", "pin": "1939", "name": "5A Informatica", "teacher": "Prof. Ferrari", "leaderboard_enabled": True},
    {"class_code": "4BSS", "pin": "1939", "name": "4B Servizi Socio-Sanitari", "teacher": "Prof. Ferrari", "leaderboard_enabled": False},
]

TEACHER_PIN = "1918"
