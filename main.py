from pypdb import Query
import requests
import re


# search for all IDs of protein given by the user
def search_protein(protein_name):
    # todo check if protein name is valid, add error handling

    # get all IDs of protein
    if check_valid_name(protein_name) == 1:
        # search for protein name in PDB using rcsb_uniprot_protein.name.value
        protein_ids = Query(f'UniProt Molecule Name HAS EXACT PHRASE "{protein_name.capitalize()}"').search()
        capital_protein_ids = [protein_id.upper() for protein_id in protein_ids]
        return capital_protein_ids


def check_valid_name(protein_name):
    # todo check if can be made simpler
    # check that protein name is not empty
    if protein_name == "":
        print("Please enter a protein name")
        return 0
    # check that protein name is not a number
    elif protein_name.isdigit():
        print("Please enter a valid protein name")
        return 0
    # check that protein name is not a special character
    elif not protein_name.isalpha():
        print("Please enter a valid protein name")
        return 0
        # check that protein name is not a space
    elif protein_name.isspace():
        print("Please enter a valid protein name")
        return 0
        # check that protein name exists in PDB
    elif not Query(protein_name).search():
        print(" Protein not found in PDB")
        return 0
    # if all checks pass, return protein name
    else:
        return 1


def extract_ids(string):
    pattern = r'title=\\"([a-zA-Z0-9]{4})\\">'
    matches = re.finditer(pattern, string)
    ids = [match.group(1) for match in matches]
    return ids


def common_percent(list1, list2):
    common = len(set(list1).intersection(list2))
    total = len(set(list1).union(list2))
    return common / total * 100


if __name__ == "__main__":
    protein = input("Enter protein name: ")
    PDB_list = search_protein(protein)
    # print "list of PDB IDs: ", PDB_list

    print("PDB IDs: ", PDB_list)
    response = requests.get(f"https://proteopedia.org/wiki/index.php/{protein.capitalize()}_3D_structures")
    proteo_list = extract_ids(response.text)
    #make all ids uppercase
    proteo_list = [proteo_id.upper() for proteo_id in proteo_list]
    print(proteo_list)
    print("Number of Proteopedia IDs: ", len(proteo_list))
    print("Number of PDB IDs: ", len(PDB_list))
    print("Common Percent: ", common_percent(PDB_list, proteo_list))
