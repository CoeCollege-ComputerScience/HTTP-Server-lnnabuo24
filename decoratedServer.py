import random
import OOServer

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


@s.newCommand("/secret")
def shhh(cl):
    homePage = html.replace("**Content**", "<h1> Simple Server </h1> <div></div> <p> you found my secret kitten page, now everyone knows i like fluffy kittens..." + "</p> <img src=kitten.png>")
    s.respondHTML(homePage, cl)

@s.newCommand("/greeting")
def greeting(cl, queryString):
    name = ""
    foundName = False
    for line in queryString.split("&"):
        splitUp = line.split("=")
        if splitUp[0] == "name" and len(splitUp) > 1:
            name = splitUp[1]
            foundName = True
            break

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

s.run()
