import requests
from bs4 import BeautifulSoup


def get_data_for_ID(T, PLow, PHigh, PInc, ID):
    payload = {
        "T": T,
        "PLow": PLow,
        "PHigh": PHigh,
        "PInc": PInc,
        "Digits": ID,
        "ID": ID,
        "Action": "Load",
        "Type": "IsoTherm",
        "TUnit": "C",
        "PUnit": "MPa",
        "DUnit": "mol%2Fl",
        "HUnit": "kJ%2Fmol",
        "WUnit": "m%2Fs",
        "VisUnit": "uPa*s",
        "STUnit": "N%2Fm",
        "RefState": "DEF",
    }
    r = requests.get("https://webbook.nist.gov/cgi/fluid.cgi", params=payload)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find("table")
    tr = table.find_all("tr")
    title_row = []
    result = {}
    for th in tr[0].find_all("th"):
        title_row.append(th.text)
        result[th.text] = []
    for tr_current in tr[1:]:
        counter = 0
        for td in tr_current.find_all("td"):
            value = float(td.text) if not td.text.isalpha() else td.text
            result[title_row[counter]].append(value)
            counter += 1
    return result


if __name__ == "__main__":
    print(get_data_for_ID(T=140, PLow=1, PHigh=6, PInc=1, ID="C7732185"))
