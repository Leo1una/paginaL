from django import template
import ipaddress

register = template.Library()

@register.filter
def to(value, arg):
    """
    Genera un rango de números desde 'value' hasta 'arg' (inclusive).
    Ejemplo: {% for i in 1|to:6 %} genera 1,2,3,4,5,6
    """
    try:
        start = int(value)
        end = int(arg)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return []


@register.filter
def wildcard(mask):
    """
    Convierte una máscara de red en wildcard mask.
    Ejemplo: 255.255.255.0 -> 0.0.0.255
    """
    try:
        parts = [255 - int(octet) for octet in mask.split('.')]
        return '.'.join(map(str, parts))
    except Exception:
        return "Error"


@register.filter
def to_binary(ip):
    """
    Convierte una dirección IP a binario.
    Ejemplo: 192.168.1.10 -> 11000000.10101000.00000001.00001010
    """
    try:
        return '.'.join(f'{int(octet):08b}' for octet in ip.split('.'))
    except Exception:
        return "Error"


@register.filter
def hosts(mask):
    """
    Calcula el número de hosts disponibles según la máscara.
    Ejemplo: 255.255.255.0 -> 254
    """
    try:
        network = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        return network.num_addresses - 2
    except Exception:
        return "Error"


@register.filter
def to_cidr(mask):
    """
    Convierte una máscara decimal a notación CIDR.
    Ejemplo: 255.255.255.0 -> /24
    """
    try:
        network = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        return f"/{network.prefixlen}"
    except Exception:
        return "Error"


@register.filter
def to_mask(prefix):
    """
    Convierte un número de prefijo (CIDR) a máscara decimal.
    Ejemplo: 24 -> 255.255.255.0
    """
    try:
        prefix = int(prefix)
        network = ipaddress.IPv4Network(f"0.0.0.0/{prefix}", strict=False)
        return str(network.netmask)
    except Exception:
        return "Error"
