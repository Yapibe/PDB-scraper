import csv
import requests
import re
from Bio.PDB.PDBParser import PDBParser
import os


# user interface for user to enter protein name and proteopedia site url
def get_user_input():
    protein_name = input("Enter protein name: ")
    url = input("Enter Proteopedia site url: ")
    return protein_name, url


# using BeautifulSoup to extract IdS from proteopedia site
def extract_IDs_Proteopedia(html):
    # try two different pattern matches
    # pattern 1
    pattern = r'title=\\"([a-zA-Z0-9]{4})\\">'
    matches = re.finditer(pattern, html)
    # if matches not empty, return list of ids
    ids = [match.group(1).upper() for match in matches]
    if ids:
        # return without duplicates
        return list(set(ids))
    # pattern 2
    else:
        pattern = r'<a href=".*?" title="([a-zA-Z0-9]{4})">\1</a>'
        matches = re.finditer(pattern, html)
        ids = [match.group(1).upper() for match in matches]
        return list(set(ids))


def extract_IDs_PDB(response):
    # for every "identifier: " in the response, extract the id
    pattern = r'"identifier" : "([a-zA-Z0-9]{4})",'
    matches = re.finditer(pattern, response)
    ids = [match.group(1).upper() for match in matches]
    return ids


def PDB_search(protein_name):
    # search PDB for protein name
    url = 'https://search.rcsb.org/rcsbsearch/v2/query?json='
    query = '{"query":{"type":"group","nodes":[{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_uniprot_protein.name.value","operator":"contains_phrase","negation":false,' \
            '"value":"protein_name"}},{"type":"terminal","service":"text","parameters":{"attribute":"struct.title",' \
            '"operator":"contains_words","negation":false,"value":"protein_name"}}],"logical_operator":"or",' \
            '"label":"text"},"return_type":"entry","request_options":{"return_all_hits":true,"results_content_type":[' \
            '"experimental"],"sort":[{"sort_by":"score","direction":"desc"}],"scoring_strategy":"combined"}}'

    # replace protein name in query
    query = query.replace("protein_name", protein_name.capitalize())
    # send request
    response = requests.get(url + query)
    # extract ids from response
    ids = extract_IDs_PDB(response.text)
    return ids


def find_PDB_only(ids_PDB, ids_Proteopedia):
    # find PDB ids that are in PDB but not in proteopedia
    # compare ids
    print("IDs in Proteopedia but not in PDB:")
    for id in proteopedia_IDS:
        if id.upper() not in PDB_IDs:
            print(id)
    i = 0
    for id in PDB_IDs:
        if id not in proteopedia_IDS:
            i += 1
    print("Number of IDs in PDB but not in Proteopedia: " + str(i))
    return list(set(ids_PDB) - set(ids_Proteopedia))


def validate_PDB_IDs(list_of_IDs, protein_name):
    # iterate through list_of_IDs and validate each id
    # if id is valid, add to valid_ids list of tuples (id, word)
    valid_ids = []
    flag = False
    # get pdb file from PDB
    for id in list_of_IDs:
        pdb_file = requests.get(f"https://files.rcsb.org/download/{id}.pdb")
        if pdb_file.status_code == 200:
            with open(f"{id}.pdb", "wb") as f:
                f.write(pdb_file.content)
                # parse pdb file
                parser = PDBParser(PERMISSIVE=1)
                structure = parser.get_structure(id, f"{id}.pdb")
                # search for protein name in Header, Title, COMPND
                TITLE = structure.header['name']
                # find date that protein was added to PDB
                date = structure.header['release_date']
                # check if protein name is in title without regard to capital letters
                if protein_name.lower() in TITLE.lower():
                    valid_ids.append((id, TITLE, date))
                    # remove pdb file
                    os.remove(f"{id}.pdb")
                    continue
                COMPND = structure.header['compound']
                for key in COMPND:
                    # split compound molecule into words
                    words = COMPND[key]['molecule'].split(",")
                    for word in words:
                        if protein_name.lower() in word.lower():
                            valid_ids.append((id, words, date))
                            flag = True
                            break
                    if flag:
                        break
                    if 'synonym' in COMPND[key]:
                        # check if dict has key 'synonym'
                        # split synonyms into words
                        synonyms = COMPND[key]['synonym'].split(",")
                        for syn in synonyms:
                            if protein_name.lower() in syn.lower():
                                valid_ids.append((id, synonyms, date))
                                break
                flag = False
                # remove pdb file
                os.remove(f"{id}.pdb")
                continue
        else:
            print(f"ID {id} is not valid")
    return valid_ids


if __name__ == "__main__":
    # get user input
    protein_name, url = get_user_input()
    # get html from url
    html = requests.get(url).text
    # extract ids from Proteopedia site
    proteopedia_IDS = extract_IDs_Proteopedia(html)
    print(f'{protein_name} IDs on Proteopedia: ' + f"{len(proteopedia_IDS)}")
    # get html from PDB
    PDB_IDs = PDB_search(protein_name)
    print(f'{protein_name} IDs on PDB: ' + f"{len(PDB_IDs)}")
    PDB_only = find_PDB_only(PDB_IDs, proteopedia_IDS)
    if PDB_only:
        valid_ids = validate_PDB_IDs(PDB_only, protein_name)
        print(f' New valid {protein_name} IDs on PDB: ' + f"{len(valid_ids)}")
        print(valid_ids)
        # create csv file with columns ID, Title, date
        with open(f"{protein_name}_IDs.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Date"])
            writer.writerows(valid_ids)
    else:
        print("No new IDs on PDB")
