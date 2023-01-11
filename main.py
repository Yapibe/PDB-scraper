import csv
import requests
import re
from Bio.PDB.PDBParser import PDBParser
import os


def get_user_input():
    """
    input protein name and proteopedia site url
    :return: protein name and url
    """
    input_protein = input("Enter protein name: ")
    if input_protein == "":
        return -1, -1
    proteopedia_url = input("Enter Proteopedia site url: ")
    return str(input_protein), str(proteopedia_url)


def extract_IDs_Proteopedia(html_text):
    """
    extract IDs from html text of proteopedia site
    :param html_text: text of html file
    :return: list of IDs
    """
    # try two different pattern matches
    # pattern 1
    pattern = r'title=\\"([a-zA-Z0-9]{4})\\">'
    matches = re.finditer(str(pattern), str(html_text))
    # if matches not empty, return list of ids
    list_of_proteopedia_ids = [match.group(1).upper() for match in matches]
    if list_of_proteopedia_ids:
        # return without duplicates
        return list(set(list_of_proteopedia_ids))
    # pattern 2
    else:
        pattern = r'<a href=".*?" title="([a-zA-Z0-9]{4})">\1</a>'
        matches = re.finditer(str(pattern), str(html_text))
        list_of_proteopedia_ids = [match.group(1).upper() for match in matches]
        return list(set(list_of_proteopedia_ids))


def extract_IDs_from_PDB(response_text):
    """
    extract IDs from response of PDB search
    :param response_text: response text of PDB search
    :return: list of IDs
    """
    # for every "identifier: " in the response, extract the id
    pattern = r'"identifier" : "([a-zA-Z0-9]{4})",'
    matches = re.finditer(str(pattern), str(response_text))
    list_of_PDB_ids = [match.group(1).upper() for match in matches]
    return list(list_of_PDB_ids)


def PDB_search(protein):
    """
    search PDB using protein name for IDs
    :param protein: protein name to search for
    :return: list of IDs
    """
    # search PDB for protein name
    PDB_search_url = 'https://search.rcsb.org/rcsbsearch/v2/query?json='
    query = '{"query":{"type":"group","nodes":[{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_uniprot_protein.name.value","operator":"contains_phrase","negation":false,' \
            '"value":"protein_name"}},{"type":"terminal","service":"text","parameters":{"attribute":"struct.title",' \
            '"operator":"contains_words","negation":false,"value":"protein_name"}}],"logical_operator":"or",' \
            '"label":"text"},"return_type":"entry","request_options":{"return_all_hits":true,"results_content_type":[' \
            '"experimental"],"sort":[{"sort_by":"score","direction":"desc"}],"scoring_strategy":"combined"}}'

    # replace protein name in query
    query = query.replace("protein_name", protein.capitalize())
    # send request
    response = requests.get(str(PDB_search_url + query))
    # extract ids from response
    list_of_ids = extract_IDs_from_PDB(str(response.text))
    return list(list_of_ids)


def find_PDB_only(PDB_IDs, Proteopedia_IDs):
    """
    find IDs that are in PDB but not in Proteopedia
    :param PDB_IDs: list of IDs from PDB
    :param Proteopedia_IDs: list of IDs from Proteopedia
    :return:
    """
    print("These IDs are in Proteopedia but not in PDB:")
    # turn lists into sets for faster search
    unique_PDB_IDs = set(PDB_IDs) - set(Proteopedia_IDs)
    unique_proteopedia_IDs = set(Proteopedia_IDs) - set(PDB_IDs)
    # print IDs that are in Proteopedia but not in PDB
    for ID in unique_proteopedia_IDs:
        print(ID)
    # print number of IDs that are in PDB but not in Proteopedia
    print("Number of IDs that are in PDB but not in Proteopedia: " + str(len(unique_PDB_IDs)))
    return unique_PDB_IDs


def validate_PDB_IDs(list_of_PDB_IDs, protein):
    """
    validate IDs from PDB search
    :param list_of_PDB_IDs: list of IDs from PDB search
    :param protein: protein name given by user
    :return: list of validated IDs
    """
    validated_ids = []
    flag = False
    # get pdb file from PDB
    for struct_id in list_of_PDB_IDs:
        pdb_file = requests.get(f"https://files.rcsb.org/download/{struct_id}.pdb")
        if pdb_file.status_code == 200:
            with open(str(f"{struct_id}.pdb"), str("wb")) as protein_file:
                protein_file.write(pdb_file.content)
                # parse pdb file
                parser = PDBParser(PERMISSIVE=1)
                structure = parser.get_structure(str(struct_id), str(f"{struct_id}.pdb"))
                # search for protein name in Header, Title, COMPND
                protein_file_title = structure.header['name']
                # find date that protein was added to PDB
                protein_file_release_date = structure.header['release_date']
                # check if protein name is in title without regard to capital letters
                if protein.lower() in protein_file_title.lower():
                    validated_ids.append((str(struct_id), str(protein_file_title), str(protein_file_release_date)))
                    # remove pdb file
                    protein_file.close()
                    os.remove(str(f"{struct_id}.pdb"))
                    continue
                protein_file_compound_dict = structure.header['compound']
                for compound_dict_key in protein_file_compound_dict:
                    # split compound molecule into list
                    protein_file_molecule_list = protein_file_compound_dict[compound_dict_key]['molecule'].split(",")
                    for word in protein_file_molecule_list:
                        if protein.lower() in word.lower():
                            validated_ids.append((str(struct_id), list(protein_file_molecule_list),
                                                  str(protein_file_release_date)))
                            flag = True
                            break
                    if flag:
                        break
                    if 'synonym' in protein_file_compound_dict[compound_dict_key]:
                        # check if dict has key 'synonym'
                        # split synonyms into words
                        protein_file_synonyms = protein_file_compound_dict[compound_dict_key]['synonym'].split(",")
                        for syn in protein_file_synonyms:
                            if protein.lower() in syn.lower():
                                valid_ids.append((str(struct_id), list(protein_file_synonyms),
                                                  str(protein_file_release_date)))
                                break
                flag = False
                # remove pdb file
                protein_file.close()
                os.remove(str(f"{struct_id}.pdb"))
                continue
        else:
            print(f"ID {struct_id} is not valid")
    return list(validated_ids)


if __name__ == "__main__":
    while True:
        # get user input
        protein_name_from_user, proteopedia_url_from_user = get_user_input()
        # if user enters '', exit program
        if protein_name_from_user == -1:
            break
        # get html from url
        proteopedia_html = requests.get(str(proteopedia_url_from_user)).text
        # extract ids from Proteopedia site
        proteopedia_IDS = extract_IDs_Proteopedia(str(proteopedia_html))
        print(f'{protein_name_from_user} IDs on Proteopedia: ' + f"{len(proteopedia_IDS)}")
        # get html from PDB
        PDB_IDs = PDB_search(str(protein_name_from_user))
        print(f'{protein_name_from_user} IDs on PDB: ' + f"{len(PDB_IDs)}")
        PDB_only = find_PDB_only(list(PDB_IDs), list(proteopedia_IDS))
        if PDB_only:
            valid_ids = validate_PDB_IDs(list(PDB_only), str(protein_name_from_user))
            print(f'New valid {protein_name_from_user} IDs on PDB: ' + f"{len(valid_ids)}")
            print(valid_ids)
            # create csv file with columns ID, Title, date
            with open(f"{protein_name_from_user}_ID's.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Release Date"])
                writer.writerows(valid_ids)
            # close file
            f.close()
        else:
            print("No new IDs on PDB")
