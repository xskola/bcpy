# TODO TODO TODO


def get_csp_config(channels, coeffs):
    result = list()
    coeffs = [float(i) for i in coeffs.split()]
    for i in range(len(coeffs)):
        result.append(((channels[i % len(channels)]), coeffs[i]))
    return result
