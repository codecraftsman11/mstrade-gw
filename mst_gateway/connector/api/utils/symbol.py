

def calculate_volume_precision(volume_tick):
    """
    Determines the number of decimal places allowed in symbol's volume
    based on its volume_tick value.

    """
    if not volume_tick:
        return None
    if volume_tick.is_integer():
        return 0
    else:
        volume_tick = str(volume_tick)

        # Handle floats that are in scientific notation format (e.g. 1e-05):
        if 'e-' in volume_tick:
            number, exponent = volume_tick.split('e-')
            # Notation with a decimal point (e.g. 1.32e-05):
            if '.' in number:
                decimal_places = number.split('.')[1]
                return len(decimal_places) + int(exponent)
            # Regular notation (e.g. 1e-05):
            else:
                return int(exponent)
        # Handle regular floats (e.g. 0.0001):
        else:
            return len(volume_tick.split('.')[1])
