import pycountry

def country_name_from_aplha_code(alpha_3):
    iso_3_country_name = pycountry.countries.get(alpha_3=alpha_3)
    if not iso_3_country_name:
        return alpha_3
    
    return iso_3_country_name.name