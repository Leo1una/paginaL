import os
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import JsonResponse
import io
import base64
import qrcode
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.files.storage import default_storage
from PIL import Image, ImageDraw
import qrcode
from qrcode.image.svg import SvgPathImage
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import ipaddress
import csv
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
import openpyxl
from openpyxl.styles import Font, Alignment
import random, json
import string

def welcome(request):
    return render(request, "welcome.html")

def portada(request):
    return render(request, "portada.html")

def plantillas(request):
    return render(request, "plantillas.html")

def preescolar(request): return render(request, "niveles/preescolar.html")
def preescolarO(request): return render(request, "niveles/preescolar/observaciones.html")
def primaria(request): return render(request, "niveles/primaria.html")
def secundaria(request): return render(request, "niveles/secundaria.html")
def preparatoria(request): return render(request, "niveles/preparatoria.html")

def primaria_observaciones(request):
    return render(request, "formatos/diagnostico.html")

def primaria_planeacion(request):
    return render(request, "formatos/planeacion.html")

def primaria_evaluaciones(request):
    return render(request, "formatos/evaluaciones.html")

def enviar_mensaje(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("email")
        mensaje = request.POST.get("mensaje")

        # === Correo para ti ===
        subject_admin = f"📬 Nuevo mensaje desde LRLEDEV | {nombre}"
        html_admin = render_to_string("correo_template.html", {
            "nombre": nombre,
            "correo": correo,
            "mensaje": mensaje,
        })

        email_admin = EmailMultiAlternatives(
            subject_admin,
            mensaje,
            "leonardoluna@lrledev.com",
            ["leonardoluna@lrledev.com"],
        )
        email_admin.attach_alternative(html_admin, "text/html")
        email_admin.send()

        # === Correo automático para el visitante ===
        subject_user = "Gracias por contactarte con LRLEDEV ⚙️"
        html_user = render_to_string("correo_respuesta.html", {
            "nombre": nombre,
        })

        email_user = EmailMultiAlternatives(
            subject_user,
            "Gracias por escribirnos. Te responderemos pronto.",
            "leonardoluna@lrledev.com",
            [correo],
        )
        email_user.attach_alternative(html_user, "text/html")
        email_user.send()

        return JsonResponse({"status": "ok"})

def qr(request):
    return render(request, 'qrgen/qr.html')

def qr_home(request):
    return render(request, "qrgen/qr.html")

def maestros(request):
    return render(request, "maestros.html")

def generar_qr(request):
    """Genera un código QR en PNG y SVG con opciones personalizadas."""
    if request.method == "POST":
        try:
            tipo = request.POST.get("tipo")
            puntos = request.POST.get("puntos", "square")
            color = request.POST.get("color", "#000000")
            fondo = request.POST.get("fondo", "#ffffff")
            frame = request.POST.get("frame", "none")

            # === Contenido según tipo ===
            if tipo == "link":
                data = request.POST.get("contenido", "")
            elif tipo == "texto":
                data = request.POST.get("contenido", "")
            elif tipo == "email":
                email = request.POST.get("contenido", "")
                data = f"mailto:{email}"
            elif tipo == "telefono":
                numero = request.POST.get("contenido", "")
                data = f"tel:{numero}"
            elif tipo == "whatsapp":
                numero = request.POST.get("numero")
                mensaje = request.POST.get("mensaje", "")
                data = f"https://wa.me/{numero}?text={mensaje.replace(' ', '%20')}"
            elif tipo == "wifi":
                ssid = request.POST.get("ssid")
                password = request.POST.get("password")
                data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
            else:
                return JsonResponse({"success": False, "error": "Tipo de QR no válido."})

            if not data.strip():
                return JsonResponse({"success": False, "error": "Campo vacío."})

            # === Crear QR base ===
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            matrix = qr.get_matrix()

            # === Dibujar manualmente (para cambiar forma de puntos) ===
            size = len(matrix) * 10
            img = Image.new("RGBA", (size, size), fondo)
            draw = ImageDraw.Draw(img)
            for y in range(len(matrix)):
                for x in range(len(matrix[y])):
                    if matrix[y][x]:
                        x0, y0 = x * 10, y * 10
                        x1, y1 = x0 + 10, y0 + 10
                        if puntos == "round":
                            draw.ellipse((x0, y0, x1, y1), fill=color)
                        elif puntos == "bubble":
                            draw.ellipse((x0+1, y0+1, x1-1, y1-1), outline=color, width=2)
                        else:
                            draw.rectangle((x0, y0, x1, y1), fill=color)

            # === Logo central opcional ===
            if "logo" in request.FILES:
                logo_file = request.FILES["logo"]
                logo_path = default_storage.save(logo_file.name, logo_file)
                abs_logo_path = default_storage.path(logo_path)
                logo = Image.open(abs_logo_path)
                logo.thumbnail((img.size[0] // 4, img.size[1] // 4))
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)
                os.remove(abs_logo_path)

            # === Marco opcional ===
            if frame == "circle":
                frame_img = Image.new("RGBA", (img.width + 60, img.height + 60), (255, 255, 255, 0))
                mask = Image.new("L", frame_img.size, 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0) + frame_img.size, fill=255)
                frame_img.paste(img, (30, 30), img)
                img = frame_img
            elif frame == "scan":
                draw = ImageDraw.Draw(img)
                draw.rectangle((5, 5, img.width - 5, img.height - 5), outline=(59, 130, 246), width=10)

            # === Guardar PNG ===
            png_io = io.BytesIO()
            img.save(png_io, format="PNG")
            png_bytes = png_io.getvalue()
            png_b64 = base64.b64encode(png_bytes).decode("utf-8")

            # === SVG también ===
            svg_io = io.BytesIO()
            qr_svg = qrcode.make(data, image_factory=SvgPathImage)
            qr_svg.save(svg_io)
            svg_b64 = base64.b64encode(svg_io.getvalue()).decode("utf-8")

            return JsonResponse({
                "success": True,
                "png": f"data:image/png;base64,{png_b64}",
                "svg": f"data:image/svg+xml;base64,{svg_b64}"
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

import ipaddress

def calcular_datos(ip_input, subnet_bits=0):
    data = {}
    subredes = []

    try:
        # Limpieza de entrada
        ip_input = ip_input.strip().replace(" ", "")
        if "/" not in ip_input:
            data["error"] = "Debe incluir el prefijo (por ejemplo: /24 o /64)"
            return data, subredes

        # Crear red a partir de ip_interface (más flexible)
        interfaz = ipaddress.ip_interface(ip_input)
        red = interfaz.network

        # Datos generales
        data['ip'] = str(red.network_address)
        data['prefijo'] = red.prefixlen
        data['mascara'] = str(red.netmask) if isinstance(red, ipaddress.IPv4Network) else f"/{red.prefixlen}"
        data['broadcast'] = str(red.broadcast_address) if isinstance(red, ipaddress.IPv4Network) else "N/A"
        data['total_hosts'] = (red.num_addresses - 2) if isinstance(red, ipaddress.IPv4Network) else red.num_addresses
        data['tipo'] = "Privada" if red.is_private else "Pública"
        data['clase'] = obtener_clase_ip(red)
        data['incremento'] = obtener_incremento(red)
        data['binario'] = ip_to_binary(red.network_address)
        data['error'] = None

        # Calcular rango optimizado
        if isinstance(red, ipaddress.IPv4Network):
            hosts = list(red.hosts())
            rango = f"{hosts[0]} - {hosts[-1]}" if hosts else "N/A"
        else:
            # IPv6 — no iterar todos
            first_host = red.network_address + 1
            last_host = red.network_address + (2**(128 - red.prefixlen) - 2)
            rango = f"{first_host} - {last_host}"
        data['rango'] = rango

        # Subneteo opcional
        if subnet_bits and isinstance(subnet_bits, int) and subnet_bits > 0:
            new_prefix = red.prefixlen + subnet_bits
            if new_prefix <= (32 if isinstance(red, ipaddress.IPv4Network) else 128):
                subnets = list(red.subnets(prefixlen_diff=subnet_bits))
                for i, s in enumerate(subnets, start=1):
                    if isinstance(s, ipaddress.IPv4Network):
                        hosts = s.num_addresses - 2
                        broadcast = str(s.broadcast_address)
                        mask = str(s.netmask)
                    else:
                        hosts = s.num_addresses
                        broadcast = "N/A"
                        mask = f"/{s.prefixlen}"

                    if isinstance(s, ipaddress.IPv4Network):
                        rango = f"{s.network_address + 1} - {s.broadcast_address - 1}"
                    else:
                        first_host = s.network_address + 1
                        last_host = s.network_address + (2**(128 - s.prefixlen) - 2)
                        rango = f"{first_host} - {last_host}"

                    subredes.append({
                        'num': i,
                        'network': str(s.network_address),
                        'broadcast': broadcast,
                        'rango': rango,
                        'hosts': hosts,
                        'mascara': mask,
                        'prefijo': f"/{s.prefixlen}"
                    })

                data['nuevas_subredes'] = len(subredes)
            else:
                data['error'] = "El prefijo resultante es demasiado grande."
        else:
            data['nuevas_subredes'] = 0

    except Exception as e:
        data = {'error': f'Formato de dirección IP no válido. ({str(e)})'}

    return data, subredes

def obtener_clase_ip(red):
    if isinstance(red, ipaddress.IPv6Network):
        return "IPv6"
    primer_octeto = int(str(red.network_address).split('.')[0])
    if 1 <= primer_octeto <= 126:
        return "A"
    elif 128 <= primer_octeto <= 191:
        return "B"
    elif 192 <= primer_octeto <= 223:
        return "C"
    elif 224 <= primer_octeto <= 239:
        return "D (Multicast)"
    else:
        return "E (Experimental)"

def obtener_incremento(red):
    if isinstance(red, ipaddress.IPv6Network):
        return "N/A"
    host_bits = 32 - red.prefixlen
    return 2 ** host_bits

def ip_to_binary(ip):
    if isinstance(ip, ipaddress.IPv4Address):
        return '.'.join(f"{int(octeto):08b}" for octeto in str(ip).split('.'))
    else:
        return bin(int(ip))[2:].zfill(128)

def obtener_clase(ip):
    first_octet = int(str(ip).split('.')[0])
    if first_octet < 128:
        return 'Clase A'
    elif first_octet < 192:
        return 'Clase B'
    elif first_octet < 224:
        return 'Clase C'
    elif first_octet < 240:
        return 'Clase D (Multicast)'
    else:
        return 'Clase E (Experimental)'

def calculadora(request):
    data, subredes = {}, []

    if request.method == 'POST':
        ip_input = request.POST.get('ip_input')
        subnet_bits = request.POST.get('subnet_bits') or 0
        exportar = request.POST.get('exportar')

        # Calcular datos
        data, subredes = calcular_datos(ip_input, int(subnet_bits))

        # Exportar CSV con máscara y prefijo
        if exportar == 'csv' and subredes:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="subredes.csv"'
            writer = csv.writer(response)
            writer.writerow(['#', 'Network', 'Máscara', 'Prefijo', 'Broadcast', 'Rango', 'Hosts'])
            for s in subredes:
                writer.writerow([
                    s['num'],
                    s['network'],
                    s['mascara'],
                    s['prefijo'],
                    s['broadcast'],
                    s['rango'],
                    s['hosts']
                ])
            return response

        # Exportar Excel con máscara y prefijo
        if exportar == 'excel' and subredes:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Subredes"
            ws.append(['#', 'Network', 'Máscara', 'Prefijo', 'Broadcast', 'Rango', 'Hosts'])
            for s in subredes:
                ws.append([
                    s['num'],
                    s['network'],
                    s['mascara'],
                    s['prefijo'],
                    s['broadcast'],
                    s['rango'],
                    s['hosts']
                ])
            for col in ws.columns:
                for cell in col:
                    cell.font = Font(name='Calibri', size=11)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="subredes.xlsx"'
            return response

    return render(request, 'calculadora/calculadora.html', {'data': data, 'subredes': subredes})

def ruleta(request):
    plantillas = {
        "Sí o No": ["Sí", "No"],
        "Colores": ["Rojo", "Azul", "Verde", "Amarillo", "Negro", "Blanco"],
        "Números del 1 al 10": [str(i) for i in range(1, 11)],
        "Emociones": ["Feliz", "Triste", "Enojado", "Motivado", "Cansado", "Ansioso"],
        "Nombres de ejemplo": ["Leonardo", "Nidia", "Jonathan", "Esli", "William"],
    }

    if request.method == "POST":
        opciones_texto = request.POST.get("opciones", "")
        seleccion_plantilla = request.POST.get("plantilla", "")

        if seleccion_plantilla in plantillas:
            opciones = plantillas[seleccion_plantilla]
        else:
            opciones = [x.strip() for x in opciones_texto.split(",") if x.strip()]

        resultado = random.choice(opciones) if opciones else None

        return render(request, "ruleta/ruleta.html", {
            "plantillas": plantillas,
            "resultado": resultado,
            "opciones": json.dumps(opciones)
        })

    return render(request, "ruleta/ruleta.html", {"plantillas": plantillas})

def generador(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        longitud = int(request.POST.get("longitud", 12))
        mayus = "mayus" in request.POST
        nums = "nums" in request.POST
        simbolos = "simbolos" in request.POST

        caracteres = string.ascii_lowercase
        if mayus:
            caracteres += string.ascii_uppercase
        if nums:
            caracteres += string.digits
        if simbolos:
            caracteres += "!@#$%^&*()_-+=<>?/{}[]|"

        password = "".join(random.choice(caracteres) for _ in range(longitud))
        return JsonResponse({"password": password})

    return render(request, "generador/generador.html")

def conversor(request):
    categorias = {
        "Longitud": {"Metro": 1, "Kilómetro": 1000, "Centímetro": 0.01, "Milímetro": 0.001},
        "Temperatura": {"Celsius": "C", "Fahrenheit": "F", "Kelvin": "K"},
        "Almacenamiento": {"Byte": 1, "Kilobyte": 1024, "Megabyte": 1048576, "Gigabyte": 1073741824},
    }

    resultado = None

    if request.method == "POST":
        categoria = request.POST.get("categoria")
        valor = float(request.POST.get("valor", 0))
        unidad_origen = request.POST.get("origen")
        unidad_destino = request.POST.get("destino")

        if categoria == "Longitud":
            resultado = valor * categorias[categoria][unidad_origen] / categorias[categoria][unidad_destino]

        elif categoria == "Almacenamiento":
            resultado = valor * categorias[categoria][unidad_origen] / categorias[categoria][unidad_destino]

        elif categoria == "Temperatura":
            if unidad_origen == unidad_destino:
                resultado = valor
            elif unidad_origen == "Celsius" and unidad_destino == "Fahrenheit":
                resultado = (valor * 9 / 5) + 32
            elif unidad_origen == "Fahrenheit" and unidad_destino == "Celsius":
                resultado = (valor - 32) * 5 / 9
            elif unidad_origen == "Celsius" and unidad_destino == "Kelvin":
                resultado = valor + 273.15
            elif unidad_origen == "Kelvin" and unidad_destino == "Celsius":
                resultado = valor - 273.15
            elif unidad_origen == "Fahrenheit" and unidad_destino == "Kelvin":
                resultado = (valor - 32) * 5 / 9 + 273.15
            elif unidad_origen == "Kelvin" and unidad_destino == "Fahrenheit":
                resultado = (valor - 273.15) * 9 / 5 + 32

        # ✅ Si es una solicitud AJAX, devolvemos JSON (sin recargar)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"resultado": resultado})

    # 👇 Si no es AJAX, carga normalmente la plantilla
    return render(request, "conversor/conversor.html", {
        "categorias": categorias,
        "resultado": resultado
    })