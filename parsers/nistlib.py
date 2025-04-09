import requests
from bs4 import BeautifulSoup
import warnings


def get_isothermal_data_for_ID(T, PLow, PHigh, PInc, ID):
    payload = {
        "T": T,
        "PLow": PLow,
        "PHigh": PHigh,
        "PInc": PInc,
        "Digits": 5,
        "ID": 'C'+str(ID),
        "Action": "Load",
        "Type": "IsoTherm",
        "TUnit": "K",
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
    if table is None:
        warnings.warn("Error while parsing: possibly range error")
        return None
    tr = table.find_all("tr")
    if len(tr) == 0:
        return None
    title_row = []
    result = {}
    for th in tr[0].find_all("th"):
        title=th.text.split('(')[0].strip()
        title_row.append(title)
        result[title] = []
    for tr_current in tr[1:]:
        counter = 0
        for td in tr_current.find_all("td"):
            value = float(td.text) if not td.text.isalpha() else td.text
            result[title_row[counter]].append(value)
            counter += 1
    return result


def get_critical_values_for_ID(ID):
    payload = {
        "ID": "C" + str(ID),
        "Units": "SI",
        "Mask": "4\#Thermo-Phase",
    }
    r = requests.get("https://webbook.nist.gov/cgi/cbook.cgi", params=payload)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find("table")
    tr_list = table.find_all("tr")
    result = {}
    name = soup.find("h1", {"id": "Top"})
    if name:
        result["name"] = name.text.strip()
    for tr in tr_list:
        td_list = tr.find_all("td")
        if len(td_list) == 0:
            continue
        if td_list[0].text.strip() == "Pc" and "Pc" not in result.keys():
            result["Pc"] = float(td_list[1].text.strip().split("±")[0])
        if td_list[0].text.strip() == "Tc" and "Tc" not in result.keys():
            result["Tc"] = float(td_list[1].text.strip().split("±")[0])

    payload = {
        "T": result["Tc"],
        "PLow": result["Pc"] ,
        "PHigh": result["Pc"] ,
        "PInc": 1,
        "Digits": 5,
        "ID": 'C'+str(ID),
        "Action": "Load",
        "Type": "IsoTherm",
        "TUnit": "K",
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
    final_properties = soup.find("table", attrs={"aria-labelledby": "AdditionalFluidProperties"})
    for row in final_properties.find_all("tr"):
        if row.find("th").text.strip() == "Critical temperature (Tc)":
            result["Tc"] = float(row.find("td").text.strip().split()[0])
        elif row.find("th").text.strip() == "Critical pressure (Pc)":
            result["Pc"] = float(row.find("td").text.strip().split()[0])
        elif row.find("th").text.strip() == "Acentric factor":
            result["omega"] = float(row.find("td").text.strip())

    return result


if __name__ == "__main__":
    ids_to_fill = [7732185, 630080, 124389, 7727379, 7446095, 74828]
    # get_isothermal_data_for_ID(140, 1, 6, 1, ids_to_fill[1])
    print(get_critical_values_for_ID(124389))
    # print(get_critical_values_for_ID(ids_to_fill[0]))
    # for i in ids_to_fill:
    # print(f"results for {i}: {get_critical_values_for_ID(i)}")
