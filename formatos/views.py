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
