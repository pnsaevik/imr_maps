
def farmloc():
    import sys

    args = sys.argv

    # Pop reload arg
    reload = "--reload" in args
    if reload:
        args = args.copy()
        del args[args.index("--reload")]

    if len(args) != 2:
        print("""
FARMLOC
   Find location (and more) for the specified farm

Usage:

farmloc [--reload] loknr

""")
        return

    try:
        loknr = int(args[1])
    except ValueError:
        print("Location number must be an integer")
        return

    try:
        from imr.maps.farms import locations, areas
        loc = locations(reload).sel(record=loknr)
        ar = areas(reload).sel(record=loknr)
    except KeyError:
        print(f"Location {loknr} not found")
        return

    def decode(e):
        ee = e.values.item()
        if isinstance(ee, bytes):
            return ee.decode('utf8')
        return ee

    loc_dict = {v: decode(loc[v]) for v in loc.variables}
    ar_dict = {v: decode(ar[v]) for v in ar.variables}
    d = dict(location=loc_dict, area=ar_dict)

    import yaml
    print(yaml.dump(d, allow_unicode=True))


def gyteomr():
    import sys
    args = sys.argv

    layers = {
        "blåkveite": "utbredelseskart:Blaakveite",
        "blålange": "utbredelseskart:Blaalange",
        "blåstål_rødnebb": "utbredelseskart:Blaastaal_Rodnebb",
        "breiflabb": "utbredelseskart:Breiflabb",
        "brisling": "utbredelseskart:Brisling",
        "brosme": "utbredelseskart:Brosme",
        "brugde": "utbredelseskart:Brugde",
        "dypvannsreke": "utbredelseskart:Dypvannsreke",
        "finnhval": "utbredelseskart:Finnhval",
        "fjesing": "utbredelseskart:Fjesing",
        "gråhai": "utbredelseskart:Graahai",
        "gressgylt": "utbredelseskart:Gressgylt",
        "grindhval": "utbredelseskart:Grindhval",
        "grønngylt_berggylt": "utbredelseskart:Groenngylt_Berggylt",
        "grønlandsel": "utbredelseskart:Gronlandsel",
        "kysttorsk": "utbredelseskart:kysttorsk",
        "håbrann": "utbredelseskart:Haabrann",
        "håkjerring": "utbredelseskart:Haakjerring",
        "haneskjell": "utbredelseskart:Haneskjell",
        "havert": "utbredelseskart:Havert",
        "havmus": "utbredelseskart:Havmus",
        "hummer": "utbredelseskart:Hummer",
        "hvalross": "utbredelseskart:Hvalross",
        "hvithval": "utbredelseskart:Hvithval",
        "hvitting": "utbredelseskart:Hvitting",
        "hyse_nea": "utbredelseskart:Hyse_Nordostarktisk",
        "isgalt": "utbredelseskart:Isgalt",
        "kamskjell": "utbredelseskart:Kamskjell",
        "klappmyss": "utbredelseskart:Klappmyss",
        "knølhval": "utbredelseskart:Knolhval",
        "kolmule": "utbredelseskart:Kolmule",
        "kongekrabbe": "utbredelseskart:Kongekrabbe",
        "kveite": "utbredelseskart:Kveite",
        "laks": "utbredelseskart:Laks",
        "lange": "utbredelseskart:Lange",
        "lodde_barentshavet": "utbredelseskart:Lodde_Barentshavet",
        "lodde_island": "utbredelseskart:Lodde_island",
        "lyr": "utbredelseskart:Lyr",
        "lysing": "utbredelseskart:Lysing",
        "makrell": "utbredelseskart:Makrell",
        "makrellstørje": "utbredelseskart:Makrellstorje",
        "mora": "utbredelseskart:Mora",
        "nvg_sild": "utbredelseskart:NVG_Sild",
        "narhval": "utbredelseskart:Narhval",
        "nebbhval": "utbredelseskart:Nebbhval",
        "nise": "utbredelseskart:Nise",
        "nordsjøhyse": "utbredelseskart:Nordsjohyse",
        "nordsjøsei": "utbredelseskart:Nordsjosei",
        "nordsjøsild": "utbredelseskart:Nordsjosild",
        "nordsjøtorsk": "utbredelseskart:Nordsjotorsk",
        "øyepål": "utbredelseskart:Oyepaal",
        "pigghå": "utbredelseskart:Pigghaa",
        "polartorsk": "utbredelseskart:Polartorsk",
        "raudåte": "utbredelseskart:Raudate",
        "ringsel": "utbredelseskart:Ringsel",
        "rødspette": "utbredelseskart:Roedspette",
        "sei_nea": "utbredelseskart:Sei_Nordostarktisk",
        "sjøkreps": "utbredelseskart:Sjokreps",
        "skjellbrosme": "utbredelseskart:Skjellbrosme",
        "skolest": "utbredelseskart:Skolest",
        "snabeluer": "utbredelseskart:Snabeluer",
        "snøkrabbe": "utbredelseskart:Snokrabbe",
        "spekkhogger": "utbredelseskart:Spekkhogger",
        "spermhval": "utbredelseskart:Spermhval",
        "springere_kvitnos": "utbredelseskart:Springere_Kvitnos",
        "springere_kvitskjeving": "utbredelseskart:Springere_Kvitskjeving",
        "steinkobbe": "utbredelseskart:Steinkobbe",
        "storkobbe": "utbredelseskart:Storkobbe",
        "stortare": "utbredelseskart:Stortare",
        "svarthå": "utbredelseskart:Svarthaa",
        "taggmakrell": "utbredelseskart:Taggmakrell",
        "taskekrabbe": "utbredelseskart:Taskekrabbe",
        "tobis": "utbredelseskart:Tobis",
        "vågehval": "utbredelseskart:Vaagehval",
        "vanliguer": "utbredelseskart:Vanliguer",
        "ål": "utbredelseskart:aal",
        "bergnebb": "utbredelseskart:bergnebb",
        "hågjel": "utbredelseskart:haagjel",
        "nordsjotorsk_2021": "utbredelseskart:nordsjotorsk_2021",
        "rognkjeks_rognkall": "utbredelseskart:rognkjeks_rognkall",
        "torsk_nea": "utbredelseskart:torsk_nea",
    }

    def print_valid_species():
        print("Valid species include: ")
        for k, v in layers.items():
            print(f'  - {k} ({v})')

    # Pop wms_code arg
    try:
        idx = [arg.startswith('--wms_codes=') for arg in args].index(True)
        wmscode_str = args.pop(idx)
    except ValueError:
        wmscode_str = '--wms_codes=10'
    codes = tuple([int(s) for s in wmscode_str.split("=")[1].split(",")])

    if len(args) != 3:
        print("GYTEOMR")
        print("   Download spawning area to geojson file\n")
        print("Usage:\n")
        print('gyteomr [--wms_codes=code1,code2,...] "species" out.geojson\n')
        print('By default, only wms code 10 ("gyteområde") is included.\n')
        print_valid_species()
        return

    species = args[1].lower()
    if species not in layers:
        layer = species
    else:
        layer = layers[species]

    try:
        from imr.maps.spawn import area
        area(layer_name=layer, outfile=args[2], wms_codes=codes)
    except ValueError:
        print(f"Unknown species: {args[1]}\n")
        print_valid_species()
