import re
import csv

# import necessary tables
from tablesAll import fact_table, matched_table, sub_strings

# defining a filing obect with the 
# attributes entity, file and isdigit
class Filing:
    def __init__(self, entity, file, isdigit):
        self.entity = entity
        self.file = file
        self.isdigit = isdigit

# checks the matched_table to see if any necessary concepts have not been mapped
def check_matched_table(entity):
    # Iterate over the key-value pairs in the dictionary
    for key, value in matched_table.items():
        # Check if the value is False
        if value == False:
            # print to log that it failed mapping
            print(f"'{key}' for '{entity}' did not map, please fix")

# resets matched_table 
def reset_matched_table():
    for key in matched_table:
        matched_table[key] = False

# updates the filing object if necessary
# also checks if there is a new file, and checks 
# the matched_table of previous file by calling check_matched_table()
# and then resets it by calling reset_matched_table()
def update_filing_and_tables(key, value, filing):
    # check if value is numerical and if so set
    # isdigit to true
    if(key == "value" and value.isnumeric()):
        filing.isdigit = True
    # check if first file
    if (key == "file" and filing.file == None):
        filing.file = value
    else:
        # check if the file has changed and if so update
        # then check and reset
        if(key == "file" and value != filing.file and filing.isdigit):
            filing.file = value
            # check table and then reset
            check_matched_table(filing.entity) # check previous fact
            reset_matched_table() # reset table for the next fact
    
    # check if first file
    if(key == "entity" and filing.entity == None):
        filing.entity = value
    else: 
        # check if the entity has changed and if so update
        if(key == "entity" and value != filing.entity):
            filing.entity = value

# standardize the names
# load value into fact_info and return true if mapped
def update_fact_with_translation(key, value, fact_info, mapped):
    if(key == "name"):
        for substring in sub_strings:
            # check if value contains substring
            if(substring in value):
                # sub_string table gives the corresponding table
                # for specific substring
                corresponding_table = sub_strings[substring]
                # check if match exist in corresponding table
                if(value in corresponding_table):
                    # set value of key to translated value and original value
                    fact_info[key] = corresponding_table[value], value 
                    # set the value of key matched to True to check
                    matched_table[corresponding_table[value]] = True 
                    mapped = True
                    return mapped
    # add key and value to fact_info[]
    if(key in fact_table):
        fact_info[key] = value
    return mapped

# outputs the facts into csv, one file for mapped and one for all
def to_csv(facts_mapped, facts):
    with open('outputmappedfacts.csv', mode='w', newline='') as file:
        # Create a writer object

        writer = csv.DictWriter(file, fieldnames=['NCRname', 'name', 'entity', 'value', 'measure', 'startDate', 'endDate'])

        # Write the header row
        writer.writeheader()

        # Write the data rows
        for row in facts_mapped:
            namerow = row["name"]
            writer.writerow({"NCRname": namerow[0], "name": namerow[1], "entity": row["entity"], "value": row["value"], "measure": row["measure"], "startDate": row["startDate"], "endDate": row["endDate"]})
    
    with open('outputallfacts.csv', mode='w', newline='') as file:
        # Create a writer object

        writer = csv.DictWriter(file, fieldnames=['name','entity', 'value', 'measure', 'startDate', 'endDate'])

        # Write the header row
        writer.writeheader()

        # Write the data rows
        for row in facts:
            writer.writerow({"name": row.get("name"), "entity": row.get("entity"), "value": row.get("value"), "measure": row.get("measure"), "startDate": row.get("startDate"), "endDate": row.get("endDate")})

# parse the model by traversing it
def parse_model(xbrl_facts):
    k = 0
    # create a new Filing object with null properties
    filing = Filing(None, None, False)
    # create empty arrays
    facts = []
    facts_mapped = []
    last_index = len(xbrl_facts) - 1
    # traverse the xbrlfacts
    for i, fact in enumerate(xbrl_facts):
        k += 1
        # make the fact string for parsing
        fact = str(fact)
        # Define the pattern for splitting the data string
        pattern = r"modelInlineFact\[__\d+\]\("
        # Split the data string using the pattern
        fact = re.split(pattern, fact)
        # Remove the first element (empty string)
        fact.pop(0)
        # make into string again for further parsing
        fact = str(fact)
        parse_fact(fact=fact, filing = filing, facts = facts, facts_mapped = facts_mapped)
        # if last fact and check it
        if(i == last_index):
            check_matched_table(filing.entity) 
    print(k, "facts parsed")
    return facts, facts_mapped

# takes an attribute as input and returns a key-value pair
def get_attribute(attribute):
    # while attribute does not start with ' delete the first character
    while not (attribute.startswith("'")):
        attribute = attribute[1:]

    # While the attribute ends with certain characters, remove the last character
    while (attribute.endswith(")") or attribute.endswith(",") or attribute.endswith("))") or attribute.endswith("))), ")):
        attribute = attribute[:-1]
    
    # Remove all single quotes from the attribute
    attribute = attribute.replace("'", "")
    # split attribute to get the key value pairs
    key, value = attribute.split(", ", 1)
    return key, value

# iterate through attributes within fact
def parse_fact(fact, filing, facts, facts_mapped):
    # split to get an array of fact containing the attributes
    fact = fact.split(", (")
    # instanciate mapped to false
    mapped = False
    #initiate an empty array
    fact_info = {}
    # iterate over each attribute in fact
    # to get key-value pairs and handle them
    for attribute in fact:
        # necessary in this format
        if(attribute == ")))" or attribute == ")"):
            continue
        #check if the attribute is the end of a fact
        if(attribute.endswith("]")):
            break
        # get attribute as key-value pair
        key, value = get_attribute(attribute)
        # update values of table and object
        update_filing_and_tables(key, value, filing)
        # check if match is found, mapped is true if so
        mapped = update_fact_with_translation(key, value, fact_info, mapped)
    # append fact_info to facts 
    facts.append(fact_info)      
    # append fact_info to facts if mapped
    if(mapped):
        facts_mapped.append(fact_info)