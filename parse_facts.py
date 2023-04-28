import re

# import necessary tables
from tablesAll import fact_table, matched_table, sub_strings_table
from utils import to_csv, write_fail

# defining a filing object with the 
# attribute entity
class Filing:
    def __init__(self, entity):
        self.entity = entity

def process(facts):
    facts, facts_mapped, filing = parse_model(facts)
    check_matched_table(filing.entity) 
    reset_matched_table()
    to_csv(facts_mapped=facts_mapped, facts=facts)

def parse_model(xbrl_facts):
    k = 0
    # create a new Filing object with null properties
    filing = Filing(None)
    # create empty arrays
    facts = []
    facts_mapped = []
    # traverse the xbrlfacts
    for fact in enumerate(xbrl_facts):
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

    
    return facts, facts_mapped, filing

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

        if(filing.entity == None and key == "entity"):
            filing.entity = value
        # update values of table and object
        #update_filing_and_tables(key, value, filing)
        # check if match is found, mapped is true if so
        mapped = update_fact_with_translation(key, value, fact_info, mapped)
    # append fact_info to facts 
    facts.append(fact_info)      
    # append fact_info to facts if mapped
    if(mapped):
        facts_mapped.append(fact_info)

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

# checks the matched_table to see if any necessary concepts have not been mapped
def check_matched_table(entity):
    # Iterate over the key-value pairs in the dictionary
    for key, value in matched_table.items():
        # Check if the value is False
        if value == False:
            write_fail(key, entity)
            

# resets matched_table 
def reset_matched_table():
    for key in matched_table:
        matched_table[key] = False

# standardize the names
# load value into fact_info and return true if mapped
def update_fact_with_translation(key, value, fact_info, mapped):
    if(key == "name"):
        for substring in sub_strings_table:
            # check if value contains substring
            if(substring in value):
                # sub_string table gives the corresponding table
                # for specific substring
                corresponding_table = sub_strings_table[substring]
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