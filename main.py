# import os
# import requests
# import re
# import pandas as pd

# from Bio.PDB.MMCIF2Dict import MMCIF2Dict


# def check_valid_name(protein_name):
#     # check that protein name is not empty
#     if protein_name == "":
#         print("Please enter a protein name")
#         return 0
#     # check that protein name is not a number
#     elif protein_name.isdigit():
#         print("Please enter a valid protein name")
#         return 0
#     # check that protein name is not a special character
#     elif not protein_name.isalpha():
#         print("Please enter a valid protein name")
#         return 0
#         # check that protein name is not a space
#     elif protein_name.isspace():
#         print("Please enter a valid protein name")
#         return 0
#         # check that protein name exists in PDB
#     elif not Query(protein_name).search():
#         print(" Protein not found in PDB")
#         return 0
#     # if all checks pass, return protein name
#     else:
#         return 1
#
#
c
#
#
# def common_percent(list1, list2):
#     common = len(set(list1).intersection(list2))
#     total = len(set(list1).union(list2))
#     return common / total * 100
#
#
# def check_compound_for_name(protein_id, protein_name):
#     # get pdb file from PDB
#     pdb_file = requests.get(f"https://files.rcsb.org/download/{protein_id}.pdb")
#     # save pdb file
#     with open(f"{protein_id}.pdb", "wb") as f:
#         f.write(pdb_file.content)
#     # parse pdb file
#     parser = PDBParser(PERMISSIVE=1)
#     structure = parser.get_structure(protein_id, f"{protein_id}.pdb")
#     # get compound name from pdb file
#     compound = structure.header["compound"]
#     # compound is a dictionary of dictionaries
#     # loop through the keys of the compound dictionary
#     for key in compound:
#         try:
#             # get the compound name
#             compound_molecule = compound[key]["molecule"].split(",")
#             # if any element in the list is contains "PROTEIN_NAME" then return true
#             if any(protein_name in element for element in compound_molecule):
#                 # remove pdb file
#                 os.remove(f"{protein_id}.pdb")
#                 return 1
#             # try if any element in the list contains "PROTEIN_NAME" then return true
#             # check for each subdictionary in compound to see if it contains key "synonym"
#             elif "synonym" in compound[key]:
#                 # get the synonyms
#                 compound_synonym = compound[key]["synonym"].split(",")
#                 # if any element in the list is contains "PROTEIN_NAME" then return true
#                 if any(protein_name in element for element in compound_synonym):
#                     # remove pdb file
#                     os.remove(f"{protein_id}.pdb")
#                     return 1
#         except KeyError:
#             continue
#     # if no compound name is found, return false
#     # remove pdb file
#     os.remove(f"{protein_id}.pdb")
#     return 0
#
#

#     # make list of tuple of id and if it contains the protein name
#     pdb_list = [(pdb_id, check_compound_for_name(pdb_id, protein)) for pdb_id in PDB_list]
#     # make list of ids that dont contain the protein name
#     pdb_list = [pdb_id for pdb_id, contains_name in pdb_list if contains_name == 0]
#     print("Number of PDB IDs that do not contain the protein name: ", len(pdb_list))
#     print("Number of Proteopedia IDs that do not contain the protein name: ", len(proteo_list))
