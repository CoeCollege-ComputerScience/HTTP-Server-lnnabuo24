import random
import OOServer
import math

html = """<!DOCTYPE html>
<html>
<head> <title>Simple Server</title>
</head>
<body>
**Content**
</body>
</html>
"""

s = OOServer.Server()

# takes in a query string
# and returns a dictionary version of the many secrets it holds
def readQuery(queryString):
    data = {}

    for line in queryString.split("&"):
        splitUp = line.split("=")
        if len(splitUp) > 1:
            data[ splitUp[0] ] = splitUp[1]

    return data


@s.newCommand("/secret")
def shhh(cl, query):
    homePage = html.replace("**Content**", "<h1> Simple Server </h1> <div></div> <p> you found my secret kitten page, now everyone knows i like fluffy kittens..." + "</p> <img src=kitten.png>")
    s.respondHTML(homePage, cl)

@s.newCommand("/greeting")
def greeting(cl, queryString):
    name = ""
    foundName = False
    """
    for line in queryString.split("&"):
        splitUp = line.split("=")
        if splitUp[0] == "name" and len(splitUp) > 1:
            name = splitUp[1]
            foundName = True
            break
    """
    data = readQuery(queryString)
    if "name" in data:
        foundName = True
        name = data["name"]

    if foundName:
        homePage = html.replace("**Content**", "<p> hello there, " + name + "! </p>")
        s.respondHTML(homePage, cl)
    else:
        homePage = html.replace("**Content**", "<p> nameless? </p>")
        s.respondHTML(homePage, cl)

@s.newCommand("/dice")
def gamble(cl):
    num1 = random.randint(1, 6)
    num2 = random.randint(1, 6)

    #img1 = "<img src=kitten.png>" * num1
    #img2 = "<img src=kitten.png>" * num2
    img1 = "<img src=RedDie" + str(num1) + ".png>"
    img2 = "<img src=RedDie" + str(num2) + ".png>"

    body = "<p> you rolled: " + img1 + " and " + img2 + "</p>"
    body += "<a href=/dice> <button>reroll</button> </a>"

    homePage = html.replace("**Content**", body)
    s.respondHTML(homePage, cl)

@s.newCommand("/cubeRoot")
def cubeRoot(cl, query):
    data = readQuery(query)
    result = math.cbrt( float(data["value"]) )

    body = "<p> did you know there was a horse that could tap out cube roots with its hooves*? i have the same horse hiding in the servers and it will tell you the cube roots of numbers <p>"
    body += "<p> *i never said the horse was calculating cube roots <p>"

    if result == math.trunc(result) and result >= 0:
        result = math.trunc(result)
        # positive integer result
        body += "<p> the cube root of " + str(data["value"]) + " is..."
        body += ("tap-" * result).removesuffix("-") + "! (" + str(result) + ")"
    else:
        body += "<p> ...except " + str(data["value"]) + ", because the horse only responds with positive integers <p>"

    page = html.replace("**Content**", body)
    s.respondHTML(page, cl)

s.run()
