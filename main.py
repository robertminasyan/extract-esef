from model import read_and_save_filings
from processfacts import parse_model, to_csv

xbrl_facts = read_and_save_filings()
# collect facts and mapped facts
facts, facts_mapped = parse_model(xbrl_facts = xbrl_facts)
# write to csv files
to_csv(facts_mapped=facts_mapped, facts=facts)

