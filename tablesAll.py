from tablesIS import revenue_table
# here tables relating to all statement types are kept

# contains the key names that are of interest
fact_table = {
    "file": str,
    "value": str,
    "name": str,
    "entity": str,
    "startDate": str,
    "endDate": str,
    "measure": str
}

# contains the most important concepts
# and if they are matched or not
matched_table = {
    "Revenue" : False
}

# contains sub_strings and its corresponding table
# where the translation can be found
sub_strings_table = {
    "Revenue" : revenue_table,
    "Net" : revenue_table,
    "Income" : revenue_table
}
