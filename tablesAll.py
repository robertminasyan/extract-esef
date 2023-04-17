from tablesIS import revenue_table
# here tables relating to all statement types are kept

# contains the key names that are of interest
fact_table = {
    "file": None,
    "value": None,
    "name": None,
    #"QName": None,
    "entity": None,
    "startDate": None,
    "endDate": None,
    "measure": None
    #"unitRef": None
}

# contains the most important concepts
# and if they are matched or not
matched_table = {
    "Revenue" : False
}

# contains sub_strings and its corresponding table
# where the translation can be found
sub_strings = {
    "Revenue" : revenue_table
    #"CostOfSales" : None
}
