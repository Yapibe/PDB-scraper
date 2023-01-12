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
    query = '{"query":{"type":"group","logical_operator":"and","nodes":[{"type":"group","nodes":[{"type":"terminal",' \
            '"service":"text","parameters":{"attribute":"struct.title","operator":"contains_phrase","negation":false,' \
            '"value":"obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":false,"value":"obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":false,' \
            '"value":"obscurin"}}],"logical_operator":"or"},{"type":"group","nodes":[{"type":"terminal",' \
            '"service":"text","parameters":{"attribute":"struct.title","operator":"contains_phrase","negation":true,' \
            '"value":"obscurin-binding protein"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"struct.title","operator":"contains_phrase","negation":true,"value":"obscurin peptide"}},' \
            '{"type":"terminal","service":"text","parameters":{"attribute":"struct.title",' \
            '"operator":"contains_phrase","negation":true,"value":"peptide from obscurin"}},{"type":"terminal",' \
            '"service":"text","parameters":{"attribute":"struct.title","operator":"contains_phrase","negation":true,' \
            '"value":"putative obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"struct.title","operator":"contains_phrase","negation":true,"value":"possible obscurin"}},' \
            '{"type":"terminal","service":"text","parameters":{"attribute":"struct.title",' \
            '"operator":"contains_phrase","negation":true,"value":"hypothetical obscurin"}},{"type":"terminal",' \
            '"service":"text","parameters":{"attribute":"struct.title","operator":"contains_phrase","negation":true,' \
            '"value":"probable obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"struct.title","operator":"contains_phrase","negation":true,' \
            '"value":"obscurin-interacting"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"struct.title","operator":"contains_phrase","negation":true,"value":"obscurin inhibitor"}},' \
            '{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"obscurin-binding protein"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"obscurin peptide"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"peptide from obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"putative obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"possible obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"hypothetical obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"probable obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"obscurin-interacting"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.rcsb_macromolecular_names_combined.name","operator":"contains_phrase",' \
            '"negation":true,"value":"obscurin inhibitor"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"obscurin-binding protein"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"obscurin peptide"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"peptide from obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"putative obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"possible obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"hypothetical obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"probable obscurin"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"obscurin-interacting"}},{"type":"terminal","service":"text","parameters":{' \
            '"attribute":"rcsb_polymer_entity.pdbx_description","operator":"contains_phrase","negation":true,' \
            '"value":"obscurin inhibitor"}}],"logical_operator":"or"}],"label":"text"},"return_type":"entry",' \
            '"request_options":{"return_all_hits":true,"results_content_type":["experimental"],' \
            '"sort":[{"sort_by":"score","direction":"desc"}],"scoring_strategy":"combined"}}'

    # replace protein name in query
    search = query.replace("obscurin", protein.capitalize())
    # send request
    response = requests.get(str(PDB_search_url + search))
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
    # get pdb file from PDB
    for struct_id in list_of_PDB_IDs:
        pdb_file = requests.get(f"https://files.rcsb.org/header/{struct_id}.cif")
        if pdb_file.status_code == 200:
            with open(str(f"{struct_id}.cif"), str("wb")) as protein_file:
                protein_file.write(pdb_file.content)
                protein_file_dict = Bio.PDB.MMCIF2Dict.MMCIF2Dict(str(f"{struct_id}.cif"))
                # check if protein name is in pdb file
                protein = protein.lower()
                # check if protein name is in title
                match = next(filter(lambda x: protein in x, protein_file_dict["_struct.title"]), None)
                if match:
                    validated_ids.append(
                        (struct_id, match, protein_file_dict["_pdbx_database_status.recvd_initial_deposition_date"]))
                    # remove file
                    os.remove(str(f"{struct_id}.cif"))
                    continue
                # check if protein name is in compound molecule
                match = next(filter(lambda x: protein in x, protein_file_dict["_entity.pdbx_description"]), None)
                if match:
                    validated_ids.append(
                        (struct_id, match, protein_file_dict["_pdbx_database_status.recvd_initial_deposition_date"]))
                    # remove file
                    os.remove(str(f"{struct_id}.cif"))
                    continue
                # check if dict has synonym key
                if "_entity_name_com.name" in protein_file_dict:
                    # check if protein name is in synonym
                    match = next(filter(lambda x: protein in x, protein_file_dict["_entity_name_com.name"]), None)
                    if match:
                        validated_ids.append((struct_id, match,
                                              protein_file_dict["_pdbx_database_status.recvd_initial_deposition_date"]))
                        # remove file
                        os.remove(str(f"{struct_id}.cif"))
                        continue
                # name not in file, remove file
                os.remove(str(f"{struct_id}.cif"))
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
        print("PDB only IDs:")
        for ID in PDB_only:
            print(ID)
        if PDB_only:
            # valid_ids = validate_PDB_IDs(list(PDB_only), str(protein_name_from_user))
            # print(f'New valid {protein_name_from_user} IDs on PDB: ' + f"{len(valid_ids)}")
            # print(valid_ids)
            # create csv file with columns ID, Title, date
            with open(f"{protein_name_from_user}_ID's.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID"])
                writer.writerows(PDB_only)
            # close file
            f.close()
        else:
            print("No new IDs on PDB")
