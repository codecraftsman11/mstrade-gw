

def calculate_decimal_precision(value):
    """
    Determines the amount of decimal places in a number.
        Example: for 0.04, decimal precision is 2

    """
    if not value:
        return None
    if value.is_integer():
        return 0
    else:
        value = str(value)

        if 'e-' in value:
            # Handle floats that are in scientific notation format (e.g. 1e-05)
            number, exponent = value.split('e-')
            if '.' in number:
                # Notation with a decimal point (e.g. 1.32e-05)
                decimal_places = number.split('.')[1]
                return len(decimal_places) + int(exponent)
            else:
                # Regular notation (e.g. 1e-05):
                return int(exponent)
        else:
            # Handle regular floats (e.g. 0.0001):
            return len(value.split('.')[1])
