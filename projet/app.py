from discord.ext import commands
import discord
import random
import json
import asyncio

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot pret")
    bot.loop.create_task(revenu())
    bot.loop.create_task(dally())


def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=True, indent=4)


def read_json(file):
    try:
        with open(file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except:
        data = {}
    return data


def trouver_element_liste_dans_chaine(liste, chaine):
    for element in liste:
        if element in chaine:
            return element
    return None


txt = "Ps5-> 500€ 1\nLot de bijoux -> 1000€ 2\nTélé-> 1200€ 3\nVélos -> 800€ 4\nHabits de luxes -> 4000€ 5\nRolex -> 7000€ 6\nIphone -> 1200€ 7\nAirpods -> 250€ 8\nTrottinette électrique -> 200€ 9"
txt = txt.replace(" ", "")
txt = txt.split("\n")
objets = [x.split("->")[0] for x in txt]
prix = [x.split("€")[0] for x in txt]


def init(ctx):
    data = read_json("data.json")
    author_id = ctx.author.id
    if author_id not in data:
        data[author_id] = {}
    if "inventaire" not in data[author_id]:
        data[author_id]["inventaire"] = {}
    if "argent" not in data[author_id]["inventaire"]:
        argent = random.randint(10, 25)
        data[author_id]["inventaire"]["argent"] = argent
    if "cartel" not in data:
        data["cartel"] = {}
    if "armes" not in data[author_id]["inventaire"]:
        data[author_id]["inventaire"]["armes"] = []
    if "armes" not in data and "illegal_shop" not in data:
        shop = {}
        armes = {
            "Pompe": {
                "vies": 5,
                "proba": {"maisons": 80, "magazins": 55, "banques": 35},
            },
            "Couteau": {
                "vies": 1,
                "proba": {"maisons": 20, "magazins": 5, "banques": 1},
            },
            "Mitraillette M16": {
                "vies": 5,
                "proba": {"maisons": 70, "magazins": 70, "banques": 30},
            },
            "Pistolet Artémis 23mn": {
                "vies": 3,
                "proba": {"maisons": 60, "magazins": 40, "banques": 10},
            },
            "Dynamite": {
                "vies": 1,
                "proba": {"maisons": 1, "magazins": 1, "banques": 70},
            },
        }
        names_armes = armes.keys()
        prix = [2_300, 300, 1_200, 700, 10_000]
        for index, value in enumerate(names_armes):
            shop[value] = prix[index]
        shop["1 kg de drogue"] = 25
        shop["plantation personnelle de drogue"] = 300
        data["armes"] = armes
        data["illegal_shop"] = shop
    if "create_inc" not in data:
        inc = {"pizzeria": 10_000, "magazin": 100_000, "Banque": 500_000}
        data["create_inc"] = inc
    if "inc" not in data:
        data["inc"] = {}
    write_json(data, "data.json")
    return data


async def revenu():
    data = read_json("data.json")
    names_cartel = list(data["cartel"].keys())
    for name in names_cartel:
        cartel = data["cartel"][name]
        argent_hebdo = cartel["argent_hebdo"]
        clients = len(cartel["employé"])
        cartel["argent"] += argent_hebdo * clients
    write_json(data, "data.json")
    await asyncio.sleep(86400)


async def dally():
    try:
        data = read_json("data.json")
        inc = data["inc"]
        names_cartel = list(inc.keys())
        for name in names_cartel:
            inc2 = inc[name]
            argent_hebdo = inc["argent_hebdo"]
            clients = len(inc["employé"].keys())
            inc["argent"] += argent_hebdo * clients
        write_json(data, "data.json")
        await asyncio.sleep(86400)
    except:
        pass


@bot.command(name="start", description="Vous entrez dans la réalité")
async def start(ctx):
    data = init(ctx)
    await ctx.send(f"Vous avez fait un grand pas dans la réalité: {ctx.author.mention}")


@bot.command(
    name="receleur_sell",
    description=">receleur_sell [objet] [nombre d'objets] permet de savoir le prix total",
)
async def sell(ctx, obj: int = 0, nb_obj: int = 0):
    data = init(ctx)
    if not obj:
        return await ctx.send("il n'y a pas le numéro de l'objet")
    if not nb_obj:
        return await ctx.send(f"il n'y a aucun nombre de {objets[obj-1]}")
    author_id = ctx.author.id
    total = prix[obj - 1] * nb_obj
    if data[author_id]["inventaire"] < total:
        return await ctx.send(
            f"Vous n'avez pas assez d'argent pour acheter {objets[obj-1]}: {prix[obj-1]}*{nb_obj}={total} euros"
        )
    data[author_id]["inventaire"] -= total
    write_json(data, "data.json")
    await ctx.send(f"Vous avez acheté {objets[obj-1]}")


@bot.command(name="receleur_price", description="récupérer tous les prix")
async def price(ctx):
    await ctx.send(txt)


@bot.command(name="inventory", description="récupérer son inventaire")
async def inventory(ctx):
    user = ctx.message.author
    author_id = ctx.message.author.id
    data = init(ctx)
    for key, value in data[author_id]["inventaire"].items():
        await ctx.send(f"{key}:{value}")


@bot.command(name="create_cartel", description="créer un cartel")
async def create_cartel(ctx, nom: str, image_url: str):
    data = init(ctx)
    author_id = ctx.author.id
    argent = data[author_id]["inventaire"]["argent"]
    if argent >= 50000:
        if nom in data["cartel"]:
            return await ctx.send("il existe déjà ce nom de cartel")
        noms = data["cartel"].keys()
        image_urls = []
        for x in noms:
            image_urls.append(data["cartel"][x]["image_url"])
        if image_url in image_urls:
            return await ctx.send("l'image existe déjà dans un des cartels")
        data["cartel"][nom] = {}
        data["cartel"][nom]["image_url"] = image_url
        data["cartel"][nom]["employés"] = []
        data["cartel"][nom]["PDG"] = author_id
        data["cartel"][nom]["lvl"] = 1
        data["cartel"][nom]["argent_hebdo"] = 500
        argent -= 50000
        await ctx.send("tu as acheté ton cartel")
        embed = discord.Embed(
            title="Nouveau cartel créé",
            description=f"Nom: {nom}",
            color=discord.Color.green(),
        )
        embed.set_image(url=image_url)
        write_json(data, "data.json")
        return await ctx.send(embed=embed)
    await ctx.send("tu n'as pas assez d'argent (50 000 euros) pour acheter ton cartel")


@bot.command(name="liste_cartel", description="liste des cartels")
async def liste_cartel(ctx):
    data = init(ctx)
    for index, value in enumerate(data["cartel"].keys()):
        await ctx.send(f"cartel {index}:{value}")


@bot.command(name="join_cartel", description="rejoindre un cartel")
async def join_cartel(ctx, name):
    data = init(ctx)
    author_id = ctx.author.id
    argent = data[author_id]["inventaire"]["argent"]
    if name not in data["cartel"]:
        return await ctx.send(
            "Ce nom n'est pas dans la liste des cartels: faites cette commande pour voir la liste des cartels: '>liste_cartel'"
        )
    if argent < 10_000:
        return await ctx.send("tu n'a pas assez d'argent, il faut 10 000 euros")
    argent -= 10_000
    data["cartel"][name]["employé"].append(author_id)
    data[author_id]["cartel"] = name
    write_json(data, "data.json")
    await ctx.send(f"tu es inscrit dans le cartel: {name}")


@bot.command(name="upgrade_cartel", description="améliorer un cartel")
async def upgrade_cartel(ctx, name):
    data = init(ctx)
    author_id = ctx.author.id
    argent = data[author_id]["inventaire"]["argent"]
    data["cartel"][name]["lvl"] += 1
    if data["cartel"][name]["PDG"] != author_id:
        return await ctx.send("Tu n'es pas l'administrateur de ce cartel")
    if argent < 50_000:
        return await ctx.send("tu n'as pas assez d'argent (50 000 euros)")
    if data["cartel"][name]["lvl"] >= 5:
        data["cartel"][name]["lvl"] -= 1
        return await ctx.send(
            "je ne peux pas t'améliorer ton cartel car tu es au niveau maximum"
        )
    if data["cartel"][name]["lvl"] < 2:
        data["cartel"][name]["% de non braquage"] = 0
    data["cartel"][name]["% de non braquage"] += 5
    data["cartel"][name]["argent_hebdo"] += 100
    argent -= 50_000
    write_json(data, "data.json")
    await ctx.send(f"tu as augmenté d'un niveau ton cartel {name}")


@bot.command(
    name="liste_braquage",
    description="Affiche la liste de choix de cambriolage disponible",
)
async def liste_cambriolage(ctx):
    txt = "Cambrioler une maison -> 1500€ ( 1j d'attente) 1\nBraquer un magasin -> 7000€ (5) d'attente) 2\nCambrioler une banque-> 25 000 (7j d'attente) 3"
    await ctx.send(txt)


@bot.command(
    name="braquage", description="Braquege selon le choix de la liste de braquage"
)
async def braquage(ctx, nb):
    data = init(ctx)
    start = time.time()
    author_id = ctx.author.id
    if "cartel" in data[author_id]:
        argents = [1_500, 7_000, 25_000]
        lieux = ["maisons", "magazins", "banques"]
        times_sleep = [86400, 432000, 604800]
        proba_police = [20, 35, 50]
        armes = data[author_id]["inventaire"]["armes"]
        if not len(armes):
            return await ctx.send("tu n'as aucune armes à ta disposition")
        proba_armes_maisons = [
            value["proba"][lieux[int(nb) - 1]] for key, value in armes.items()
        ]
        proba_arme = max(proba_armes_maisons)
        index = proba_armes_maisons.index(proba_arme)
        time_sleep = times_sleep[index]
        if time_sleep > (start - data[author_id]["latest"]):
            return await ctx.send(
                "Vous êtes munis d'un bracelet impossible de faire des activités illégales"
            )
        data[author_id]["latest"] = start
        names_armes = list(armes.keys())
        arme = names_armes[index]
        await ctx.send(f"la meilleure armes pour ton braquages est {arme}")
        police = proba_police[int(nb) - 1]
        choices = [True, False]
        weights = [proba_arme, 100 - proba_arme]
        braquage = random.choices(choices, weights=weights, k=1)[0]
        argent = argents[int(nb) - 1]
        if braquage:
            weights = [police, 100 - police]
            police = random.choices(choices, weights=weights, k=1)[0]
            if not police:
                data[author_id]["inventaire"]["argent"] += argent
                write_json(data, "data.json")
                return await ctx.send(
                    f"Tu as réussi le braquage et tu as volé {argent} € !"
                )
            argent = argent // 2
            weights = [1 / 2, 1 / 2]
            corrompu = random.choices(choices, weights=weights, k=1)[0]
            if corrompu:
                data[author_id]["inventaire"]["argent"] += argent
                write_json(data, "data.json")
                return await ctx.send(
                    f"Tu t'es fait arrêter, mais tu as réussi à corrompre les policiers, tu as gagné {argent} euros"
                )
            index = data[author_id]["inventaire"]["armes"].index(arme)
            del data[author_id]["inventaire"]["armes"][index]
            data[author_id]["inventaire"]["argent"] -= argent
            return await ctx.send(
                f"Tu t'es fait arrêter et tu as perdu l'arme {arme} et l'argent {argent} euros volés !"
            )
        return await ctx.send("Le braquage a échoué !")
    await ctx.send("Tu n'es pas dans un cartel")


@bot.command(
    name="illegal_shop_list", description="liste des produits du magazin illégal"
)
async def illegal_shop(ctx):
    data = init(ctx)
    shop = data["illegal_shop"]
    embed = discord.Embed(
        title="Shop illégal",
        description="Voici la liste des produits du shop illégal :",
        color=discord.Color.red(),
    )
    embed.add_field(name="Produits", value="", inline=False)
    x = 1
    for key, value in shop.items():
        embed.add_field(name=f"{key}", value=f"{value} euros, n°{x}")
        x += 1
    await ctx.send(embed=embed)


@bot.command(
    name="illegal_shop_buy", description="liste des produits du magazin illégal"
)
async def illegal_shop_buy(ctx, nb):
    data = init(ctx)
    author_id = ctx.author.id
    armes = data["armes"]
    shop = data["illegal_shop"]
    names_armes = armes.keys()
    arme = names_armes[nb - 1]
    prix = shop[arme]
    argent = data[author_id]["inventaire"]["argent"]
    if argent < pris:
        return await ctx.send(f"tu n'as pas assez d'argent pour acheter {arme}")
    data[author_id]["inventaire"]["armes"].append(arme)
    argent -= prix
    await ctx.send(f"tu as acheté {arme} pour {prix}")


@bot.command(
    name="liste_inc", description="liste de propositions pour créer une entreprises"
)
async def liste_inc(ctx):
    data = init(ctx)
    incs = data["create_inc"]
    x = 1
    embed = discord.Embed(
        title="Entreprises",
        description="Voici la liste des choix des entreprises",
        color=discord.Color.red(),
    )
    for key, value in incs.items():
        value = f"{value} euros n°{x}"
        embed.add_field(name=key, value=value, inline=False)
        x += 1
    await ctx.send(embed=embed)


@bot.command(name="create_inc", description="créer une entreprises")
async def create_inc(ctx, nb, *, nom):
    data = init(ctx)
    revenus = [200, 500, 5_000]
    incs = data["create_inc"]
    author_id = ctx.author.id
    names_inc = incs.keys()
    index = nb - 1
    name = names_inc[index]
    prix = incs[name]
    argent = data[author_id]["inventaire"]["argent"]
    if argent < prix:
        return await ctx.send("Tu n'as pas assez d'argent pour acheter ton entreprise")
    if nom in data["inc"]:
        return await ctx.send("Ce nom d'entreprise exite déjà")
    data["inc"][nom] = {}
    data["inc"][nom]["PDG"] = author_id
    data["inc"][nom]["argent_hebdo"] = revenus[index]
    argent -= prix
    await ctx.send(f"tu as acheté l'entreprise {name}")


@bot.command(name="list_shop", description="liste du shop légal")
async def shop(ctx):
    txt = "1€ = baguette (1)\n200€ = salle de muscu (2)\n500€ = paire de Balenciaga (3)\n3.5k€ = Moto\n12k€ = Clio\n95k€ = Appartemment\n135k€ = Porchse 911 GT Carerra S\n200k€ = Bateau de plaisance\n300k€ = Villa\n500k€ = Yot\n1M€ = La Joconde"
    txt = txt.split("\n")
    prix = [x.split("€ = ")[0] for x in txt]
    objets = [
        x.split("€ = ")[1] if len(x.split("€ = ")) > 1 else "Invalid Entry" for x in txt
    ]
    embed = discord.Embed(
        title="Shop",
        description="Voici la liste des choix des produits du shop avec le prix en euros",
        color=discord.Color.red(),
    )
    ranges = range(1, len(prix) + 1)
    for x in ranges:
        index = x - 1
        value = f"{prix[index]} n°{x}"
        embed.add_field(name=objets[index], value=value, inline=False)
    await ctx.send(embed=embed)


@bot.command(
    name="help", description="Affiche la liste de toutes les commades disponibles"
)
async def help(ctx):
    all_commands = bot.commands
    commandes = [command.name for command in all_commands]
    descriptions = [bot.get_command(name).description for name in commandes]
    cmds = {}
    diff = ["receleur", "inc", "cartel", "braquage", "illegal"]
    for index, value in enumerate(commandes):
        element = trouver_element_liste_dans_chaine(diff, value)
        if element:
            if element not in cmds:
                cmds[element] = {}
            cmds[element][value] = descriptions[index]
        else:
            if "other" not in cmds:
                cmds["other"] = {}
            cmds["other"][value] = descriptions[index]

    cmds = dict(sorted(cmds.items()))
    other = cmds.pop("other")
    cmds["other"] = other
    paginated_cmds = []
    current_page = []
    for key, value in cmds.items():
        embed = discord.Embed(title=key, color=discord.Color.green())
        cmds_names = list(value.keys())
        descriptions = [value[x] for x in cmds_names]
        for i in range(len(cmds_names)):
            embed.add_field(name=cmds_names[i], value=descriptions[i], inline=False)
        paginated_cmds.append(embed)

    x = 0
    while x != len(paginated_cmds):
        message = await ctx.send(embed=paginated_cmds[x])
        if x > 0:
            await message.add_reaction("⬅️")
        if x < len(paginated_cmds) - 1:
            await message.add_reaction("➡️")

        def check(reaction, user):
            return (
                user == ctx.author
                and reaction.message.id == message.id
                and reaction.emoji in ["⬅️", "➡️"]
            )

        while True:
            try:
                reaction, user = await bot.wait_for(
                    "reaction_add", timeout=None, check=check
                )
                count = reaction.count
                if count >= 2:
                    index = ["⬅️", "➡️"].index(reaction.emoji)
                    if index == 0:
                        bouton = "previous"
                    else:
                        bouton = "next"
                    break
            except asyncio.TimeoutError:
                break
        if bouton == "next":
            x += 1
        else:
            x -= 1
        bouton = ""
        await message.delete()


bot.run("MTEzMzM5NjA5ODA2MTQzOTE0Nw.GpXTn9.08GkPn_0th931tH5AI7ZGyC8Royv00j9oCCB_k")
