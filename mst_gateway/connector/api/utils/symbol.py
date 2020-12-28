

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

        if 'e-' in volume_tick:
            # Handle floats that are in scientific notation format (e.g. 1e-05)
            number, exponent = volume_tick.split('e-')
            if '.' in number:
                # Notation with a decimal point (e.g. 1.32e-05)
                decimal_places = number.split('.')[1]
                return len(decimal_places) + int(exponent)
            else:
                # Regular notation (e.g. 1e-05):
                return int(exponent)
        else:
            # Handle regular floats (e.g. 0.0001):
            return len(volume_tick.split('.')[1])
