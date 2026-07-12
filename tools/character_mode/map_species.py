#!/usr/bin/env python3
"""Map scraped roster names to Unbound SPECIES_* constants + numeric IDs.

Adapted from the ROWE Character Mode project's map_species.py. ROWE resolves
names against its own local decomp source (guaranteed to match the compiled
ROM, since ROWE builds from that exact source). We have no such guarantee for
Unbound — instead we resolve against Skeli789/Dynamic-Pokemon-Expansion's
"Unbound" branch (cloned to tools/dpe_unbound_donor/), which is a strong lead
for Unbound's real data layer but NOT confirmed to be pinned to exactly
v2.1.1.1's compiled build. Every numeric ID produced here is PROVISIONAL until
cross-checked against the real ROM (Phase 1 routine-mapping work) — this is
flagged in the output.

Confirmed this session (tools/search_gametext.py): Unbound v2.1.1.1 has NO
Gen 9 species (every Gen 8 species tested was found in-ROM text, all 18 Gen 9
species tested were not) — matches the DPE Unbound branch's species.h, which
also stops at Gen 8 Gigantamax forms (NUM_SPECIES = 0x50E). Gen 9 characters
were dropped from characters.txt entirely per user direction.

Reads rosters_raw.json, resolves each display name to a SPECIES_* constant
and numeric ID, normalizes every species to its evolution-family base stage,
dedupes, and writes:
  - rosters_mapped.json   (character -> sorted base-stage species, both
                            SPECIES_* constant name and numeric id)
  - roster_review.csv     (for the user to audit: one row per character/species)
  - unmatched_names.txt   (names that resolved to nothing, for fixing)
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DONOR = os.path.abspath(os.path.join(HERE, "..", "dpe_unbound_donor"))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def species_ids():
    """SPECIES_X -> numeric id, from the DPE Unbound branch's include/species.h."""
    text = read(os.path.join(DONOR, "include/species.h"))
    ids = {}
    for m in re.finditer(r"#define\s+(SPECIES_\w+)\s+(0x[0-9A-Fa-f]+|\d+)", text):
        ids[m.group(1)] = int(m.group(2), 0)
    return ids


# Gen3-style bracketed/escaped control-code placeholders used in the DPE
# donor's .string dump for characters outside plain ASCII (found by
# inspection: NAME_NIDORANF -> "Nidoran[B6]", NAME_NIDORANM -> "Nidoran[B5]"
# — matches Bulbapedia's Nidoran♀/♂; NAME_FLABEBE -> "Flab\eb\e" — matches
# Bulbapedia's Flabébé). Extend if more show up in unmatched_names.txt.
BRACKET_CODES = {"[B6]": "♀", "[B5]": "♂", "\\e": "é"}


def name_to_id():
    """Display name -> numeric species id, via POSITION in
    strings/Pokemon_Name_Table.string, NOT by parsing the NAME_X label back
    into a SPECIES_X constant name.

    Discovered this session: the string table's internal NAME_X labels do
    NOT reliably match species.h's SPECIES_X constants (e.g. NAME_CRABMINBLE
    for SPECIES_CRABOMINABLE, NAME_HOOH for SPECIES_HO_OH) — the label is an
    abbreviated internal symbol, not a stable key. But the table's 0-indexed
    entry position exactly equals the numeric species id (verified: index 1
    = "Bulbasaur" = SPECIES_BULBASAUR = 0x1; index 957 = "Crabminble" =
    SPECIES_CRABOMINABLE = 0x3BD; index 770 = "Fletchindr" =
    SPECIES_FLETCHINDER = 0x302). Total entries (1294) also exactly matches
    NUM_SPECIES from species.h — strong corroboration this ordering holds
    for the whole table, not just spot-checked entries."""
    text = read(os.path.join(DONOR, "strings/Pokemon_Name_Table.string"))
    names = re.findall(r"#org @NAME_\w+\n(.+)", text)
    mapping = {}
    for idx, name in enumerate(names):
        for code, ch in BRACKET_CODES.items():
            name = name.replace(code, ch)
        if name not in mapping:  # first occurrence wins (base form before alt forms)
            mapping[name] = idx
    return mapping


def first_stage_map():
    """SPECIES_X -> base-stage SPECIES_Y, walking gEvolutionTable backwards.

    Same technique as ROWE's map_species.py, pointed at the DPE Unbound
    branch's 'Evolution Table.c' instead of a local decomp tree."""
    text = read(os.path.join(DONOR, "src/Evolution Table.c"))
    m = re.search(r"gEvolutionTable\[NUM_SPECIES\]\[EVOS_PER_MON\]\s*=\s*\{(.*?)^\};",
                  text, re.S | re.M)
    body = m.group(1)
    rows = [(r.start(), r.group(1))
            for r in re.finditer(r"\[(SPECIES_\w+)\]\s*=", body)]
    parent = {}
    for t in re.finditer(r"\{\s*EVO_\w+\s*,[^,{}]+,\s*(SPECIES_\w+)", body):
        src = None
        for pos, name in rows:
            if pos < t.start():
                src = name
            else:
                break
        if src and src != t.group(1):
            parent.setdefault(t.group(1), src)

    base = {}
    def find_base(c):
        seen = set()
        while c in parent and c not in seen:
            seen.add(c)
            c = parent[c]
        return c
    for child in list(parent):
        base[child] = find_base(child)
    return base


# Bulbapedia name -> DPE Unbound-branch display-name divergences (10-char cap
# on species names forces truncation for anything longer). Looked up directly
# against the real strings/Pokemon_Name_Table.string content this session —
# NOT reused from ROWE's NAME_FIXES, which turned out to encode a DIFFERENT
# (and incompatible) truncation convention. E.g. ROWE's decomp truncates
# "Crabominable" -> "Crabminabl" (drop the last letter), but this DPE table
# actually has "Crabminble" (drop the 5th/8th letters, keeping "-ble" intact)
# — copying ROWE's fixes verbatim silently produced 30 unmatched species
# before this was caught and corrected via direct lookup.
# Gen 9-only names (Fuecoco, Sprigatito, Cyclizar, the Paradox mons, etc.)
# are deliberately NOT included here — Unbound has no Gen 9 species at all
# (confirmed via tools/search_gametext.py), so those must stay unmatched.
NAME_FIXES = {
    "Fletchinder": "Fletchindr",
    "Crabominable": "Crabminble",
    "Corvisquire": "Corvsquire",
    "Corviknight": "Corvknight",
    "Barraskewda": "Baraskewda",
    "Centiskorch": "Centskorch",
    "Polteageist": "Poltegeist",
    "Stonjourner": "Stonjorner",
    "Blacephalon": "Blacphalon",
}

# Known signature/ace Pokemon per character (any stage; resolved to the
# family's first stage below). Characters absent here get a random starter.
# Reused verbatim from ROWE's SIGNATURES dict for all overlapping Gen1-8
# characters (same real-world characters, same signatures).
SIGNATURES = {
 "Red":"Pikachu","Leaf":"Eevee","Blue":"Pidgeot","Lance":"Dragonite",
 "Lorelei":"Lapras","Bruno":"Machamp","Agatha":"Gengar","Koga":"Weezing",
 "Brock":"Onix","Misty":"Starmie","Lt. Surge":"Pikachu","Erika":"Vileplume",
 "Sabrina":"Alakazam","Blaine":"Arcanine","Giovanni":"Rhydon","Ash":"Pikachu",
 "Gary":"Blastoise","Ritchie":"Pikachu","Tracey":"Scyther","Jessie":"Ekans",
 "James":"Weezing",
 "Ethan":"Cyndaquil","Kris":"Totodile","Lyra":"Chikorita","Silver":"Totodile",
 "Falkner":"Hoothoot","Bugsy":"Scyther","Whitney":"Miltank","Morty":"Gengar",
 "Chuck":"Poliwrath","Jasmine":"Steelix","Pryce":"Piloswine","Clair":"Kingdra",
 "Will":"Xatu","Karen":"Umbreon","Janine":"Ariados","Archer":"Houndoom",
 "Ariana":"Arbok",
 "Brendan":"Treecko","May":"Blaziken","Wally":"Gallade","Steven":"Metagross",
 "Wallace":"Milotic","Sidney":"Absol","Phoebe":"Dusclops","Glacia":"Walrein",
 "Drake":"Salamence","Roxanne":"Nosepass","Brawly":"Hariyama","Wattson":"Manectric",
 "Flannery":"Torkoal","Norman":"Slaking","Winona":"Altaria","Tate":"Solrock",
 "Liza":"Lunatone","Juan":"Kingdra","Maxie":"Camerupt","Archie":"Sharpedo",
 "Drew":"Roserade",
 "Lucas":"Turtwig","Dawn":"Piplup","Barry":"Empoleon","Cynthia":"Garchomp",
 "Aaron":"Drapion","Bertha":"Hippowdon","Flint":"Infernape","Lucian":"Bronzong",
 "Roark":"Rampardos","Gardenia":"Roserade","Maylene":"Lucario","Crasher Wake":"Floatzel",
 "Fantina":"Mismagius","Byron":"Bastiodon","Candice":"Froslass","Volkner":"Shinx",
 "Cyrus":"Weavile","Mars":"Purugly","Jupiter":"Skuntank","Saturn":"Toxicroak",
 "Paul":"Electivire","Zoey":"Glameow","Nando":"Roserade",
 "Cheren":"Stoutland","Bianca":"Emboar","N":"Zorua","Alder":"Volcarona","Iris":"Haxorus",
 "Cilan":"Pansage","Chili":"Pansear","Cress":"Panpour","Lenora":"Watchog",
 "Burgh":"Leavanny","Elesa":"Zebstrika","Clay":"Excadrill","Skyla":"Swanna",
 "Brycen":"Beartic","Drayden":"Haxorus","Roxie":"Whirlipede","Marlon":"Jellicent",
 "Shauntal":"Chandelure","Marshal":"Conkeldurr","Grimsley":"Bisharp","Caitlin":"Gothitelle",
 "Ghetsis":"Hydreigon","Colress":"Klinklang","Trip":"Serperior",
 "Shauna":"Chespin","Diantha":"Gardevoir","Malva":"Talonflame",
 "Siebold":"Clawitzer","Wikstrom":"Aegislash","Drasna":"Noivern","Viola":"Vivillon",
 "Grant":"Tyrunt","Korrina":"Lucario","Ramos":"Gogoat","Clemont":"Heliolisk",
 "Valerie":"Sylveon","Olympia":"Meowstic","Wulfric":"Avalugg","Lysandre":"Gyarados",
 "Alain":"Charizard","Sawyer":"Sceptile",
 "Kukui":"Incineroar","Hau":"Raichu",
 "Molayne":"Dugtrio","Kahili":"Toucannon","Acerola":"Palossand",
 "Olivia":"Lycanroc","Gladion":"Type: Null",
 "Guzma":"Golisopod","Plumeria":"Salazzle","Lusamine":"Bewear","Lillie (anime)":"Vulpix",
 "Kiawe (anime)":"Turtonator","Lana (anime)":"Popplio","Mallow (anime)":"Tsareena",
 "Sophocles":"Togedemaru",
 "Leon":"Charizard","Milo":"Eldegoss","Nessa":"Drednaw","Kabu":"Centiskorch",
 "Bea":"Machamp","Allister":"Gengar","Opal":"Alcremie","Gordie":"Coalossal",
 "Melony":"Lapras","Piers":"Obstagoon","Raihan":"Duraludon","Hop":"Dubwool",
 "Bede":"Hatterene","Marnie":"Morpeko","Rose":"Copperajah","Goh":"Cinderace",
 "Chloe":"Eevee",
}

# Signatures used as the EXACT species (not reduced to first stage):
# these characters' partner is famously the mid-stage itself.
SIGNATURES_EXACT = {"Red", "Lt. Surge", "Ash", "Ritchie"}


def main():
    with open(os.path.join(HERE, "rosters_raw.json")) as f:
        raw = json.load(f)

    name_id = name_to_id()
    ids = species_ids()
    id_to_const = {v: k for k, v in ids.items()}
    base = first_stage_map()
    unmatched = set()
    mapped = {}

    def resolve_const(name):
        """Bulbapedia display name -> SPECIES_* constant, or None."""
        sid = name_id.get(NAME_FIXES.get(name, name))
        if sid is None:
            return None
        return id_to_const.get(sid)

    for disp, info in sorted(raw.items()):
        consts = set()
        for name in info["species"]:
            const = resolve_const(name)
            if const is None:
                unmatched.add(name)
                continue
            consts.add(base.get(const, const))
        species_list = sorted(consts, key=lambda c: ids.get(c, 999999))
        entry = {"page": info["page"], "category": info["category"],
                 "gen": info.get("gen", 0),
                 "species": [{"const": c, "id": ids.get(c)} for c in species_list]}
        ace = SIGNATURES.get(disp)
        if ace:
            const = resolve_const(ace)
            if const is None:
                print("SIGNATURE UNRESOLVED: %s -> %s" % (disp, ace))
            else:
                sig_base = base.get(const, const)
                sig = const if disp in SIGNATURES_EXACT else sig_base
                if sig_base in consts:
                    entry["signature"] = {"const": sig, "id": ids.get(sig)}
                else:
                    print("SIGNATURE NOT ON ROSTER: %s -> %s (%s)" % (disp, ace, sig_base))
        mapped[disp] = entry

    with open(os.path.join(HERE, "rosters_mapped.json"), "w") as f:
        json.dump(mapped, f, indent=1, sort_keys=True)

    with open(os.path.join(HERE, "roster_review.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["character", "category", "base_species", "species_id_PROVISIONAL", "keep(Y/n)"])
        for disp, info in sorted(mapped.items()):
            for c in info["species"]:
                w.writerow([disp, info["category"], c["const"], c["id"], "Y"])

    with open(os.path.join(HERE, "unmatched_names.txt"), "w") as f:
        f.write("\n".join(sorted(unmatched)) + "\n")

    empty = [d for d, i in mapped.items() if not i["species"]]
    print("mapped %d characters; %d unmatched names; %d empty rosters%s"
          % (len(mapped), len(unmatched), len(empty),
             (": " + ", ".join(empty)) if empty else ""))
    print("\nNOTE: all species_id values are PROVISIONAL (from the DPE Unbound-branch")
    print("donor, not yet cross-checked against the real compiled ROM). Do not trust")
    print("them for binary emission until Phase 1's routine-mapping work verifies them.")


if __name__ == "__main__":
    main()
