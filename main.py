import csv
import requests
import re
import Bio.PDB.MMCIF2Dict
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
    return str(input_protein), str("https://proteopedia.org/wiki/index.php/" + proteopedia_url)


def extract_IDs_Proteopedia(html_text):
    """
    extract IDs from html text of proteopedia site
    :param html_text: text of html file
    :return: set of IDs
    """
    # try two different pattern matches
    # pattern 1
    pattern = r'title=\\"([a-zA-Z0-9]{4})\\">'
    matches = re.finditer(str(pattern), str(html_text))
    # if matches not empty, return list of ids
    list_of_proteopedia_ids = [match.group(1).upper() for match in matches]
    if list_of_proteopedia_ids:
        # return without duplicates
        return set(list_of_proteopedia_ids)
    # pattern 2
    else:
        pattern = r'<a href=".*?" title="([a-zA-Z0-9]{4})">\1</a>'
        matches = re.finditer(str(pattern), str(html_text))
        list_of_proteopedia_ids = [match.group(1).upper() for match in matches]
        return set(list_of_proteopedia_ids)


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
    # return without duplicates
    return set(list_of_PDB_ids)


def title_search(protein):
    """
    search for PDB titles containing protein name
    :param protein:
    :return: list of IDs
    """
    # search PDB for protein name
    PDB_search_url = 'https://search.rcsb.org/rcsbsearch/v2/query?json='
    query = ' {' \
            '"query":{' \
            '"type":"group",' \
            '"logical_operator":"and",' \
            '"nodes":[' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":false,' \
            '"value":"protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"group",' \
            '"nodes":[' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name-binding protein"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name peptide"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"peptide from protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"putative protein_name"' \
            '                       }' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"possible protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"hypothetical protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"probable protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name-interacting"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"struct.title",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name Inhibitor"' \
            '}' \
            '}' \
            '],' \
            '"logical_operator":"or"' \
            '}' \
            '],' \
            '"label":"text"' \
            '},' \
            '"return_type":"entry",' \
            '"request_options":{' \
            '"return_all_hits": true,' \
            '"results_content_type":[' \
            '"experimental"' \
            '],' \
            '"sort":[' \
            '{' \
            '"sort_by":"score",' \
            '"direction":"desc"' \
            '}' \
            '],' \
            '"scoring_strategy":"combined"' \
            '}' \
            '}'

    # replace protein name in query
    search = query.replace("protein_name", protein.capitalize())
    # send request
    response = requests.get(str(PDB_search_url + search))
    # extract ids from response
    list_of_ids = extract_IDs_from_PDB(str(response.text))
    return list(list_of_ids)


def molecule_name_search(protein):
    """
    search for PDB molecule name containing protein name
    :param protein: protein name
    :return: list of PDB ids
    """
    # search PDB for protein name
    PDB_search_url = 'https://search.rcsb.org/rcsbsearch/v2/query?json='
    query = ' {' \
            '"query":{' \
            '"type":"group",' \
            '"logical_operator":"and",' \
            '"nodes":[' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":false,' \
            '"value":"protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"group",' \
            '"nodes":[' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name-binding protein"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name peptide"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"peptide from protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"putative protein_name"' \
            '                       }' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"possible protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"hypothetical protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"probable protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name-interacting"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name Inhibitor"' \
            '}' \
            '}' \
            '],' \
            '"logical_operator":"or"' \
            '}' \
            '],' \
            '"label":"text"' \
            '},' \
            '"return_type":"entry",' \
            '"request_options":{' \
            '"return_all_hits": true,' \
            '"results_content_type":[' \
            '"experimental"' \
            '],' \
            '"sort":[' \
            '{' \
            '"sort_by":"score",' \
            '"direction":"desc"' \
            '}' \
            '],' \
            '"scoring_strategy":"combined"' \
            '}' \
            '}'

    # replace protein name in query
    search = query.replace("protein_name", protein.capitalize())
    # send request
    response = requests.get(str(PDB_search_url + search))
    # extract ids from response
    list_of_ids = extract_IDs_from_PDB(str(response.text))
    return list(list_of_ids)


def synonym_search(protein):
    """
    search for synonyms of protein name
    :param protein: protein name
    :return: list of PDB ids
    """
    # search PDB for protein name
    PDB_search_url = 'https://search.rcsb.org/rcsbsearch/v2/query?json='
    query = ' {' \
            '"query":{' \
            '"type":"group",' \
            '"logical_operator":"and",' \
            '"nodes":[' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":false,' \
            '"value":"protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"group",' \
            '"nodes":[' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name-binding protein"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name peptide"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"peptide from protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"putative protein_name"' \
            '                       }' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"possible protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"hypothetical protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"probable protein_name"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name-interacting"' \
            '}' \
            '},' \
            '{' \
            '"type":"terminal",' \
            '"service":"text",' \
            '"parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description",' \
            '"operator":"contains_phrase",' \
            '"negation":true,' \
            '"value":"protein_name Inhibitor"' \
            '}' \
            '}' \
            '],' \
            '"logical_operator":"or"' \
            '}' \
            '],' \
            '"label":"text"' \
            '},' \
            '"return_type":"entry",' \
            '"request_options":{' \
            '"return_all_hits": true,' \
            '"results_content_type":[' \
            '"experimental"' \
            '],' \
            '"sort":[' \
            '{' \
            '"sort_by":"score",' \
            '"direction":"desc"' \
            '}' \
            '],' \
            '"scoring_strategy":"combined"' \
            '}' \
            '}'

    # replace protein name in query
    search = query.replace("protein_name", protein.capitalize())
    # send request
    response = requests.get(str(PDB_search_url + search))
    # extract ids from response
    list_of_ids = extract_IDs_from_PDB(str(response.text))
    return list(list_of_ids)


def PDB_search(protein):
    """
    search the titles, molecule name, and synonyms for protein name, return list containing IDs
    :param protein: name of protein
    :return: set of IDs
    """
    title_list = title_search(str(protein))
    # sort the list of IDs
    title_list = sorted(title_list)
    molecule_list = molecule_name_search(str(protein))
    # sort the list of IDs
    molecule_list = sorted(molecule_list)
    synonym_list = synonym_search(str(protein))
    # sort the list of IDs
    synonym_list = sorted(synonym_list)
    # combine the lists of IDs into one list
    combined_list = title_list + molecule_list + synonym_list
    return set(combined_list)


def find_PDB_only(PDB_IDs, Proteopedia_IDs):
    """
    find IDs that are in PDB but not in Proteopedia
    :param PDB_IDs: list of IDs from PDB
    :param Proteopedia_IDs: list of IDs from Proteopedia
    :return:
    """
    print("These IDs are in Proteopedia but not in PDB:")
    # find IDs that are in PDB set but not in Proteopedia set
    unique_PDB_IDs = set(PDB_IDs) - set(Proteopedia_IDs)
    unique_proteopedia_IDs = set(Proteopedia_IDs) - set(PDB_IDs)
    # print IDs that are in Proteopedia but not in PDB
    for ID in unique_proteopedia_IDs:
        print(ID)
    # print number of IDs that are in PDB but not in Proteopedia
    print("Number of IDs that are in PDB but not in Proteopedia: " + str(len(unique_PDB_IDs)))
    return unique_PDB_IDs


def get_molecule_name(set_of_PDB_IDs):
    list_of_ID_and_molecule_name = []
    for id in set_of_PDB_IDs:
        pdb_file = requests.get(f"https://files.rcsb.org/header/{id}.cif")
        if pdb_file.status_code == 200:
            with open(str(f"{id}.cif"), str("wb")) as protein_file:
                protein_file.write(pdb_file.content)
                protein_file_dict = Bio.PDB.MMCIF2Dict.MMCIF2Dict(str(f"{id}.cif"))
                if "_entity.pdbx_description" in protein_file_dict:
                    # add to list
                    list_of_ID_and_molecule_name.append((id, protein_file_dict["_entity.pdbx_description"]))
                else:
                    list_of_ID_and_molecule_name.append((id, "no molecule name"))
                os.remove(str(f"{id}.cif"))
    return list_of_ID_and_molecule_name


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
        PDB_only = find_PDB_only(set(PDB_IDs), list(proteopedia_IDS))
        print("PDB only IDs: " + str(PDB_only))
        if PDB_only:
            set_of_tuples = get_molecule_name(set(PDB_only))
            with open(f"{protein_name_from_user}_IDs.csv", "w", newline="") as f:
                writer = csv.writer(f)
                # create ID column, molecule name column, link to website column
                writer.writerow(["ID", "Molecule name", "Link to CIF file"])
                # write to each row
                for ID, molecule_name in set_of_tuples:
                    # write id without any commas
                    writer.writerow([ID, molecule_name, f"https://files.rcsb.org/header/{ID}.cif"])
            # close file
            f.close()
        else:
            print("No new IDs on PDB")

