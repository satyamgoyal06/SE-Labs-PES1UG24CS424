DIGITS = "0123456789"


def mask_imei(imei):
    """
    Removes dashes and spaces, then hides all but the last four digits.

    Never raises. Returns "" when imei is not a string. When four or fewer
    characters remain, every one of them is masked, because showing "the last
    four" of such a value would reveal the whole number.
    """
    if not isinstance(imei, str):
        return ""
    imei = imei.replace('-', '').replace(' ', '')
    if len(imei) <= 4:
        return '*' * len(imei)
    return '*' * (len(imei) - 4) + imei[-4:]


def parse_parts_order(text):
    """
    Parses 'screen x1; battery x2' into a {part: quantity} dictionary.

    Never raises. Returns {} when text is not a string. Items that are empty
    or not written as 'part xQTY' (missing part, missing or non numeric
    quantity, negative or zero quantity) are skipped. Part names may contain
    the letter x, and repeated parts have their quantities added together.
    """
    order = {}
    if not isinstance(text, str):
        return order
    for item in text.split(';'):
        item = item.strip()
        # split off the trailing run of digits (the quantity)
        i = len(item)
        while i > 0 and item[i - 1] in DIGITS:
            i -= 1
        qty_text, rest = item[i:], item[:i].rstrip()
        # what is left must end with the 'x' marker, preceded by a part name
        if not qty_text or not rest or rest[-1] not in 'xX':
            continue
        part = rest[:-1].strip()
        try:
            qty = int(qty_text)
        except ValueError:      # absurdly long digit strings
            continue
        if not part or qty < 1:
            continue
        order[part] = order.get(part, 0) + qty
    return order


def parse_model(text):
    """
    Splits 'Brand Model name' into a (brand, model) tuple.

    Never raises. Returns ("", "") for non-strings and blank text, and
    (brand, "") when only one word is given. Any whitespace (spaces, tabs)
    separates the brand from the model.
    """
    if not isinstance(text, str):
        return "", ""
    parts = text.strip().split(None, 1)
    if not parts:
        return "", ""
    brand = parts[0].title()
    model = parts[1].strip() if len(parts) > 1 else ""
    return brand, model


def main():
    print("==== Running mask_imei ====")
    value = input("Enter an IMEI number (e.g. 35-209900-176148-1): ")
    print("Masked IMEI:", mask_imei(value))

    print("\n==== Running parse_parts_order ====")
    value = input("Enter parts and quantities as PART xQTY separated by ; (e.g. screen x1; battery x2): ")
    print("Parts order:", parse_parts_order(value))

    print("\n==== Running parse_model ====")
    value = input("Enter the phone brand and model (e.g. Samsung Galaxy S23): ")
    print("Brand and model:", parse_model(value))

if __name__ == "__main__":
    main()
