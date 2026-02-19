from typing import Dict, Any
import pdfplumber
import re

def money_pattern(group_name: str|None=None) -> str:
    if group_name:
        return rf'\$\s*(?P<{group_name}>[0-9,]+(?:\.\d{2})?)'
    else:
        return r'\$\s*([0-9,]+(?:\.\d{2})?)'

def parse_money(m: re.Match|None, group: str|int) -> float:
    if m is None:
        return 0.0

    s: str|None = m.group(group)
    if s is None:
        return 0.0

    return float(s.replace(',', ''))


def parse_rent_charges(text: str) -> Dict[str, Any]:
    # make a compiled regex object for this subparser
    rent_charges_pattern  = r'Rent & Charges\s*Lease Amount.*?'
    rent_charges_pattern += rf'Rent\s*{money_pattern("base_rent")}.*?'
    rent_charges_pattern += rf'Cable Charge Back\s*{money_pattern("cable_fee")}.*?'
    rent_charges_pattern += rf'Total\s*{money_pattern("monthly_rent_total")}.*?'
    rent_charges_regex = re.compile(rent_charges_pattern, re.IGNORECASE)

    # search through the data
    m = rent_charges_regex.search(text)

    # parse the fields
    d = dict()
    d['monthly_rent_total'] = parse_money(m, 'monthly_rent_total')
    d['base_rent'] = parse_money(m, 'base_rent')
    d['cable_fee'] = parse_money(m, 'cable_fee')
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
    d['authorized_adults'] = m.group('authorized_adults')
    d['authorized_minors'] = m.group('authorized_minors')
    return d


def parse_lease(path_to_lease: str) -> Dict[str, Any]:
    # read the text from the PDF
    with pdfplumber.open(path_to_lease) as pdf:
        pages = [page.extract_text() or '' for page in pdf.pages]
        text = '\n'.join(pages)

    # normalize text by converting multiple whitespace characters into a single space
    text = re.sub(r'\s+', ' ', text)

    def find(pattern, flags=re.IGNORECASE):
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else None

    def find_money(pattern):
        val = find(pattern)
        return float(val.replace(',', '')) if val else None

    lease = dict()

    # --- Core Parties & Property ---
    lease['resident'] = find(r'RESIDENT\(S\):\s*([A-Za-z\s]+)')
    lease['unit_number'] = find(r'APT.#\s*([A-Za-z0-9]+)')
    lease['property_address'] = find(r'LOCATED AT:\s*(.*?)\s*\(“Premises”')

    # --- Dates ---
    lease['lease_signed_date'] = find(r'entered into on:\s*([0-9/]+)')
    lease['lease_start_date'] = find(r'beginning on\s*([0-9/]+)')
    lease['lease_end_date'] = find(r'ending\s*([0-9/]+)')
    lease['lease_term_months'] = int(find(r'for a period of\s*(\d+)\s*months') or 0)

    # --- Rent & Charges ---
    lease |= parse_rent_charges(text)

    lease['late_fee_percent'] = find_money(r'late rent charge equal to\s*([0-9]+)%')
    lease['returned_payment_fee'] = find_money(rf'returned fee in the amount of\s*{money_pattern()}')

    # --- Move-In Costs ---
    lease['prorated_move_in_rent'] = find_money(rf'sum of\s*({money_pattern})')
    lease['move_in_concession'] = find_money(rf'one-time concession amount:\s*({money_pattern})')
    lease['total_move_in_due'] = find_money(rf'total of all charges due at move-in is\s*({money_pattern})')

    # --- Deposits ---
    lease['security_deposit'] = find_money(rf'security deposit of\s*({money_pattern}))')
    lease['additional_deposit'] = find_money(rf'additional deposit of\s*({money_pattern})')

    # --- Occupancy ---
    lease |= parse_occupancy(text)

    # --- Pets ---
    lease['pets_allowed'] = 'Animal Addendum' in text
    lease['pet_rent'] = find_money(r'monthly pet rent.*?\$\s*([0-9,]+\.\d{2})')
    lease['pet_fee'] = find_money(r'Pet Fee.*?\$\s*([0-9,]+\.\d{2})')
    lease['pet_deposit'] = find_money(r'pet deposit.*?\$\s*([0-9,]+\.\d{2})')
    lease['pet_at_move_in'] = not bool(re.search(r'No Animal at Move in', text, re.IGNORECASE))

    # --- Parking ---
    lease['parking_addendum'] = 'Parking Addendum' in text
    lease['vehicle'] = {
        'make': find(r'Auto Information:\s*.*?\s*([A-Za-z]+)\s+[A-Za-z]+', re.IGNORECASE),
        'model': find(r'Auto Information:\s*.*?[A-Za-z]+\s+([A-Za-z]+)', re.IGNORECASE),
        'year': find(r'Auto Information:\s*.*?(\d{4})'),
        'license_plate': find(r'License No\s*([A-Z0-9]+)')
    }

    # --- Utilities ---
    lease['utilities_included_in_rent'] = False
    lease['utility_admin_fee_max'] = find_money(r'Administrative Fee.*?up to\s*\$\s*([0-9,]+\.\d{2})')
    lease['utility_late_fee'] = find_money(r'Late Fee equal to\s*\$\s*([0-9,]+\.\d{2})')

    # --- Insurance ---
    lease['renters_insurance_required'] = bool(
        re.search(r'Resident Liability Insurance Required', text, re.IGNORECASE)
    )

    # --- Termination ---
    lease['notice_required_days'] = int(find(r'give written notice.*?(\d+)\s*days') or 0)
    lease['early_termination_fee_months'] = int(
        re.search(r'Termination Fee equal to\s*two months`rent', text, re.IGNORECASE) and 2 or 0
    )

    return lease


def main() -> None:
    fname = '/mnt/c/Users/Upgrayedd/Downloads/lpm_lease.pdf'
    lease_data = parse_lease(fname)
    print(lease_data)


if __name__ == '__main__':
    main()