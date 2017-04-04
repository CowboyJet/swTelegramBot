import requests

class Swarfarm:
    """A simple example class"""
    i = 12345
    uri = "https://swarfarm.com"
    chartsurl = uri+"/data/log/charts"

    def getSummonInfo(self, scrolltype):
        scrollmap = {
            "Unknown scroll": 0,
            "Social summon" : 1,
            "Mystical scroll" : 2,
            "Crystals" : 3,
            "Fire scroll" : 4,
            "Water scroll" : 5,
            "Wind scroll" : 6,
            "LightDark Scroll" : 7,
            "Legendary scroll" : 8,
            "Summon stones" : 9,
            "LightDark pieces": 10,
            "Legendary pieces": 11,
            "Transcendance scroll" : 12
        }
        try:
            params = {
                "summon_method": scrollmap[scrolltype],
                "chart_type":"grade"
            }
            grade = requests.get(self.chartsurl+"/summon", params=params).json()
            total = 0.0
            for serie in grade["series"][0]["data"]:

                total += serie["y"]

            message = "Summon rates voor %s:\n" % scrolltype
            for serie in grade["series"][0]["data"]:
                ster = str(serie["name"][0]) + " ster"
                procent = round((float(serie["y"]) / total) * 100, 2)
                message += "{0}: {1}%\n".format(ster, str(procent))

            return message
        except KeyError:
            return """Voer een valide summon methode in:
            Unknown scroll
            Social summon
            Mystical scroll
            Crystals
            Fire scroll
            Water scroll
            Wind scroll
            LightDark Scroll
            Legendary scroll
            Summon stones
            LightDark pieces
            Legendary pieces
            Transcendance scroll
            """


if __name__ == "__main__":
    swarfarm = Swarfarm()
    print swarfarm.getSummonInfo("Water scroll")