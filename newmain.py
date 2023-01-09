import requests
import re


# user interface for user to enter protein name and proteopedia site url
def get_user_input():
    protein_name = input("Enter protein name: ")
    url = input("Enter Proteopedia site url: ")
    return protein_name, url


# using BeautifulSoup to extract IdS from proteopedia site
def extract_ids_proteopedia(html):
    # try two different pattern matches
    # pattern 1
    pattern = r'title=\\"([a-zA-Z0-9]{4})\\">'
    matches = re.finditer(pattern, html)
    # if matches not emoty, return list of ids
    ids = [match.group(1) for match in matches]
    if ids:
        # return without duplicates
        return list(set(ids))
    # pattern 2
    else:
        pattern = r'<a href=".*?" title="([a-zA-Z0-9]{4})">\1</a>'
        matches = re.finditer(pattern, html)
        ids = [match.group(1) for match in matches]
        return list(set(ids))


# main function
if __name__ == "__main__":
    # get user input
    # protein_name, url = get_user_input()
    protein_name = "actin"
    actin = "https://proteopedia.org/wiki/index.php/Actin_3D_structures"
    # get html from url
    html_actin = requests.get(actin).text
    # extract ids from proteopedia site
    ids = extract_ids_proteopedia(html_actin)
    print(ids)
    abin = "https://proteopedia.org/wiki/index.php/Abrin_3D_structures"
    # get html from url
    html_abin = requests.get(abin).text
    # extract ids from proteopedia site
    ids = extract_ids_proteopedia(html_abin)
    print(ids)
    abud = "https://proteopedia.org/wiki/index.php/Opioid_receptor"
    # get html from url
    html_abud = requests.get(abud).text
    # extract ids from proteopedia site
    ids = extract_ids_proteopedia(html_abud)
    print(ids)