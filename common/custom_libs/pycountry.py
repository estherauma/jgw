import pycountry

country_mapping = {
    'saudi': 'saudi arabia',
    'saudi arabia': 'saudi arabia',
    'uae': 'united arab emirates',
    'united arab emirates': 'united arab emirates',
    'uk': 'united kingdom',
    'united kingdom': 'united kingdom',
}
    
def country_name_from_aplha_code(alpha_3):
    iso_3_country_name = pycountry.countries.get(alpha_3=alpha_3)
    
    if not iso_3_country_name:
        return alpha_3
    
    return iso_3_country_name.name


def aplha_code_from_country_name(country_name):
    country_alpha3_code = pycountry.countries.get(name=country_name)
    if not country_alpha3_code:
        return country_name
    
    return country_alpha3_code.alpha_3