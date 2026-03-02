from typing import Dict, Any
import pdfplumber
import re

def money_pattern(group_name: str|None=None) -> str:
    if group_name:
        return rf'\$\s*(?P<{group_name}>[0-9,]+' + r'(\.\d{2})?)'
    else:
        return r'\$\s*([0-9,]+(\.\d{2})?)'


def date_pattern(group_name: str|None=None) -> str:
    if group_name:
        return rf'(?P<{group_name}>\d+/\d+/\d+)'
    else:
        return r'(\d+/\d+/\d+)'


def parse_money(m: re.Match|None, group: str|int) -> float:
    if m is None:
        return float('nan')

    s: str|None = m.group(group)
    if s is None:
        return float('nan')

    return float(s.replace(',', ''))


def parse_str_field(m: re.Match|None, group: str|int) -> str:
    if m is None:
        return 'UNKNOWN'
    return m.group(group) or 'UNKNOWN'


def parse_terms(text: str) -> Dict[str, Any]:
    # make a compoiled regex object for this subparser
    terms_pattern  = rf'THIS LEASE AGREEMENT is entered into on: {date_pattern("signing_date")}.*?'
    terms_pattern +=  r'by the management of (?P<landlord>.*?) \(“Landlord”\) and the undersigned resident\(s\) covering:.*?'
    terms_pattern +=  r'APT.# (?P<unit_number>\d+) \(“Unit”\) LOCATED AT: (?P<address>.*?) \(“Premises”\).*?'
    terms_pattern +=  r'RESIDENT\(S\): (?P<residents>.*)\s?\s*'
    terms_pattern +=  r'1. TERM: The Unit is leased to Resident\(s\) for a period of (?P<lease_term_months>\d+) months.*?'
    terms_pattern += rf'beginning on\s*{date_pattern("lease_start_date")}.*?'
    terms_pattern += rf'and ending {date_pattern("lease_end_date")}.*?'
    terms_regex = re.compile(terms_pattern, re.IGNORECASE)

    # search through the data
    m = terms_regex.search(text)

    # parse the fields
    d = dict()
    d['residents']         = parse_str_field(m, 'residents').strip('. ')
    d['landlord']          = parse_str_field(m, 'landlord')
    d['unit_number']       = parse_str_field(m, 'unit_number')
    d['address']           = parse_str_field(m, 'address')
    d['lease_term_months'] = int(m.group('lease_term_months')) or float('nan')
    d['lease_signed_date'] = parse_str_field(m, 'signing_date')
    d['lease_start_date']  = parse_str_field(m, 'lease_start_date')
    d['lease_end_date']    = parse_str_field(m, 'lease_end_date')
    return d


def parse_rent_charges(text: str) -> Dict[str, Any]:
    # make a compiled regex object for this subparser
    rent_charges_pattern  = r'Rent & Charges\s*Lease Amount.*?'
    rent_charges_pattern += rf'Rent\s*{money_pattern("base_rent")}.*?'
    rent_charges_pattern += rf'Cable Charge Back\s*{money_pattern("cable_fee")}.*?'
    rent_charges_pattern += rf'Total\s*{money_pattern("monthly_rent_total")}.*?'
    rent_charges_pattern += rf'The total of all charges due at move-in is\s*{money_pattern("move_in_charges")}.*?'
    rent_charges_pattern +=  r'Resident agrees to pay a late rent charge equal to (?P<late_charge_frac>\d+)%.*?'
    rent_charges_pattern += rf'Any returned payment for any reason whatsoever shall be subject to a returned fee in the amount of\s*{money_pattern("returned_payment_charge")} as additional rent.*?'
    rent_charges_pattern += rf'A security deposit of\s*{money_pattern("security_deposit")}.*?'
    rent_charges_pattern += rf'and an additional deposit of\s*{money_pattern("additional_deposit")}.*?'
    rent_charges_regex = re.compile(rent_charges_pattern, re.IGNORECASE)

    # search through the data
    m = rent_charges_regex.search(text)

    # parse the fields
    d = dict()
    d['monthly_rent_total']      = parse_money(m, 'monthly_rent_total')
    d['base_rent']               = parse_money(m, 'base_rent')
    d['cable_fee']               = parse_money(m, 'cable_fee')
    d['move_in_charges']         = parse_money(m, 'move_in_charges')
    d['late_charge_frac']        = float(m.group('late_charge_frac')) / 100 if m else float('nan')
    d['late_charge_cost']        = d['late_charge_frac'] * d['monthly_rent_total']
    d['returned_payment_charge'] = parse_money(m, 'returned_payment_charge')
    return d


def parse_occupancy(text: str) -> Dict[str, Any]:
    # make a compiled regex object for this subparser
    occupancy_pattern  = r'The apartment is leased to the resident for occupancy solely by (?P<num_authorized_adults>\d+) adults \(age \d+ and over\)'
    occupancy_pattern += r' and (?P<num_authorized_minors>\d+) minors or non-lessee occupants, consisting of \(full name of each occupant\)\s+'
    occupancy_pattern += r'Adults: (?P<authorized_adults>.*?)'
    occupancy_pattern += r'Minors/Non-Lessee Occupants:\s*(?P<authorized_minors>.*?)\s+and Resident\(s\)'
    occupancy_regex = re.compile(occupancy_pattern, re.IGNORECASE)

    # search through the data
    m = occupancy_regex.search(text)
    
    # parse the fields
    d = dict()
    d['num_authorized_adults'] = int(m.group('num_authorized_adults') or 0)
    d['num_authorized_minors'] = int(m.group('num_authorized_minors') or 0)
    d['authorized_adults'] = m.group('authorized_adults').strip()
    d['authorized_minors'] = m.group('authorized_minors').strip()
    return d


def parse_animal_addendum(text: str) -> Dict[str, Any]:
    # make a compiled regex object for this subparser
    animal_addendum_pattern  =  r'Animal Addendum.*?'
    animal_addendum_pattern += rf'monthly pet rent in the amount of\s*{money_pattern('pet_rent')}.*?'
    animal_addendum_pattern += rf'Resident agrees to pay a NON-REFUNDABLE "Pet Fee" in the amount of\s*{money_pattern('pet_fee')}.*?'
    animal_addendum_pattern += rf'Resident agrees to pay a pet deposit in the amount of\s*{money_pattern('pet_deposit')}.*?'
    animal_addendum_regex = re.compile(animal_addendum_pattern, re.IGNORECASE)

    # search through the data
    m = animal_addendum_regex.search(text)

    # parse the fields
    d = dict()
    d['pets_allowed'] = 'Animal Addendum' in text
    d['pet_rent']     = parse_money(m, 'pet_rent')
    d['pet_fee']      = parse_money(m, 'pet_fee')
    d['pet_deposit']  = parse_money(m, 'pet_deposit')
    return d


def parse_lease(path_to_lease: str) -> Dict[str, Any]:
    # read the text from the PDF
    with pdfplumber.open(path_to_lease) as pdf:
        pages = [page.extract_text() or '' for page in pdf.pages]
        text = '\n'.join(pages)

    # normalize text by converting multiple whitespace characters into a single space
    text = re.sub(r'\s+', ' ', text)

    # parse the text into a dictionary
    lease = dict()
    lease |= parse_terms(text)
    lease |= parse_rent_charges(text)
    lease |= parse_occupancy(text)
    lease |= parse_animal_addendum(text)

    return lease


def main() -> None:
    fname = '/mnt/c/Users/Upgrayedd/Downloads/lpm_lease.pdf'
    lease_data = parse_lease(fname)
    print(lease_data)


if __name__ == '__main__':
    main()