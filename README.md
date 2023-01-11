
# PDB scraper
Protein Structure Finder <br>

This program allows you to search for a protein by name and compare it with the Protein Data Bank (PDB) and Proteopedia databases.

How does it run: <br>
1. The program will prompt you to enter a protein name. This name will be used to search for the protein in both PDB and Proteopedia.

2. You will then be prompted to enter the Proteopedia URL of the page containing the 3D structures of the protein.

3. The program will print a series of messages to help you understand what it is currently doing and how accurate the search is. For example, if the protein entered is "Obscurin", the program will print:

    ```
    Obscurin IDs on Proteopedia: 32
    Obscurin IDs on PDB: 35
    These IDs are in Proteopedia but not in PDB:
    Number of IDs in PDB but not in Proteopedia: 3
    ```
    From the list of IDs that are only found in the PDB search, the program will go through each PDB file and search the TITLE and COMPOUND (Molecule first, then Synonyms) for the protein name.

4. The program will create a CSV file of the following format: (ID, sentence from file that triggered inclusion, release date).
5. Exiting the program <br>
    a. If you want to exit the program, press enter when prompted to enter a protein name. <br>
    b. If you want to search for another protein, type the name of the protein when prompted to enter a protein name. <br>
## Authors

- [@Yapibe](https://github.com/Yapibe)


