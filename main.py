import os
from model import read_and_save_filings
# main file to run program
# run by executing file

while True:
    testing_or_training = int(input("Enter 1 for training or 2 for testing: "))

    if testing_or_training == 1:
        PATH_ARCHIVES = os.path.join(".", "archives_training")
        break
    elif testing_or_training == 2:
        PATH_ARCHIVES = os.path.join(".", "archives_testing")
        break
    else:
        print("Invalid input. Please try again")
read_and_save_filings(PATH_ARCHIVES)

