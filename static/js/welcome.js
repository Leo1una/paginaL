// ✅ 1. Scroll automático al cargar
window.addEventListener("load", () => {
    if (window.location.pathname === "/") {
        window.location.hash = "#hero";
    }
});

// ==== AÑO Y ANIMACIONES ====
const y = new Date().getFullYear();
document.getElementById("year").textContent = y;

// ==== PARTÍCULAS DE FONDO ====
const c = document.getElementById("particles"),
    ctx = c.getContext("2d");
let p = [];

function r() {
    c.width = innerWidth;
    c.height = innerHeight;
    i();
}
window.addEventListener("resize", r);

class P {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.s = Math.random() * 2 + 1;
        this.dx = (Math.random() - 0.5) * 0.8;
        this.dy = (Math.random() - 0.5) * 0.8;
        this.z = Math.random() * 2;
    }
    u() {
        this.x += this.dx;
        this.y += this.dy;
        if (this.x < 0 || this.x > c.width) this.dx *= -1;
        if (this.y < 0 || this.y > c.height) this.dy *= -1;
    }
    d() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.s * this.z, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(59,130,246,${0.6 * this.z})`;
        ctx.fill();
    }
}

function i() {
    p = [];
    for (let n = 0; n < (c.width * c.height) / 25000; n++)
        p.push(new P(Math.random() * c.width, Math.random() * c.height));
}

function con() {
    for (let a = 0; a < p.length; a++) {
        for (let b = a; b < p.length; b++) {
            const dx = p[a].x - p[b].x,
                dy = p[a].y - p[b].y,
                d = Math.sqrt(dx * dx + dy * dy);
            if (d < 120) {
                ctx.strokeStyle = `rgba(59,130,246,${1 - d / 120})`;
                ctx.lineWidth = 0.3;
                ctx.beginPath();
                ctx.moveTo(p[a].x, p[a].y);
                ctx.lineTo(p[b].x, p[b].y);
                ctx.stroke();
            }
        }
    }
}

function a() {
    ctx.clearRect(0, 0, c.width, c.height);
    p.forEach((x) => {
        x.u();
        x.d();
    });
    con();
    requestAnimationFrame(a);
}
r();
a();

// ==== HALO ====
const halo = document.getElementById("halo").getContext("2d");
function drawHalo() {
    const g = halo.createRadialGradient(
        innerWidth / 2,
        innerHeight / 2,
        100,
        innerWidth / 2,
        innerHeight / 2,
        innerWidth / 1.2
    );
    g.addColorStop(0, "rgba(59,130,246,0.25)");
    g.addColorStop(1, "transparent");
    halo.clearRect(0, 0, innerWidth, innerHeight);
    halo.fillStyle = g;
    halo.fillRect(0, 0, innerWidth, innerHeight);
    requestAnimationFrame(drawHalo);
}
drawHalo();

// ==== RELOJ ====
function clk() {
    document.getElementById("clock").textContent =
        new Date().toLocaleTimeString();
}
setInterval(clk, 1000);
clk();

// ==== VISITAS ====
let v = localStorage.getItem("visits") || 0;
v++;
localStorage.setItem("visits", v);

// ==== TRADUCCIÓN ====
const langSel = document.getElementById("langSelect");
function applyLang(l) {
    updatePlaceholders(l);
    document.querySelectorAll(".lang").forEach((e) => {
        e.textContent = e.dataset[l];
    });
    localStorage.setItem("lang", l);

    if (l === "es") {
        roles = [
            "Ingeniero en Sistemas Computacionales",
            "Desarrollador Web",
            "Analista de Datos",
            "Creador de IA",
        ];
        document.getElementById("visits").textContent = `👁️ Visitas: ${v}`;
    } else {
        roles = [
            "Computer Systems Engineer",
            "Web Developer",
            "Data Analyst",
            "AI Creator",
        ];
        document.getElementById("visits").textContent = `👁️ Visits: ${v}`;
    }
}
langSel.value = localStorage.getItem("lang") || "es";
let roles = [];
applyLang(langSel.value);
langSel.onchange = () => applyLang(langSel.value);

// ==== ROL DINÁMICO ====
let rI = 0;
const dyn = document.getElementById("dynamicRole");
function changeRole() {
    dyn.innerHTML = "";
    const t = roles[rI];
    let i = 0;
    const ty = setInterval(() => {
        dyn.innerHTML = `<span style='color:#3B82F6;text-shadow:0 0 ${i % 10}px #60A5FA'>${t.substring(0, i++)}</span>`;
        if (i > t.length) {
            clearInterval(ty);
            setTimeout(() => {
                rI = (rI + 1) % roles.length;
                changeRole();
            }, 1500);
        }
    }, 100);
}
changeRole();

// ==== APARICIÓN SUAVE ====
const sct = document.querySelectorAll("section"),
    obs = new IntersectionObserver(
        (e) => {
            e.forEach((x) => {
                if (x.isIntersecting) x.target.classList.add("visible");
            });
        },
        { threshold: 0.1 }
    );
sct.forEach((x) => obs.observe(x));

// ==== FORMULARIO DE CONTACTO ====
document.getElementById("contactForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    const res = await fetch(e.target.action, {
        method: "POST",
        body: data,
    });
    if (res.ok) {
        Swal.fire({
            icon: "success",
            title: "¡Mensaje enviado!",
            text: "Tu mensaje fue enviado correctamente.",
            confirmButtonColor: "#3b82f6",
        });
        e.target.reset();
    } else {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudo enviar el mensaje.",
            confirmButtonColor: "#3b82f6",
        });
    }
});

// ==== PLACEHOLDERS BILINGÜES ====
function updatePlaceholders(l) {
    document.querySelectorAll(".lang-placeholder").forEach((input) => {
        input.placeholder = input.dataset[l];
    });
}

// ==== NAVBAR Y DETECCIÓN DE SECCIÓN ACTIVA ====
const links = document.querySelectorAll(".nav-link");
links.forEach((link) => {
    link.addEventListener("click", () => {
        links.forEach((l) => l.classList.remove("active"));
        link.classList.add("active");
    });
});

// ==== CAMBIO DE IDIOMA FOOTER ====
const langSelect = document.getElementById("langSelect");
const storedLang = localStorage.getItem("lang") || "es";
langSelect.value = storedLang;
applyLangFooter(storedLang); // ✅ usar el nombre correcto

langSelect.addEventListener("change", (e) => {
    const lang = e.target.value;
    localStorage.setItem("lang", lang);
    applyLangFooter(lang); // ✅ usar el nombre correcto
});

function applyLangFooter(lang) {
    // Traducción general
    document.querySelectorAll(".lang").forEach((el) => {
        if (el.dataset[lang]) el.textContent = el.dataset[lang];
    });

    // Traducción específica del footer
    const phrase = document.getElementById("footer-phrase");
    if (phrase && phrase.dataset[lang]) {
        phrase.textContent = phrase.dataset[lang];
    }
}


// ==== SCROLL PARA ACTIVAR LINKS ====
const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll(".nav-link");

window.addEventListener("scroll", () => {
    let scrollPos = window.scrollY + 150;
    sections.forEach((section) => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        const id = section.getAttribute("id");
        if (scrollPos >= top && scrollPos < top + height) {
            navLinks.forEach((link) => {
                link.classList.remove("active");
                if (link.getAttribute("href") === `#${id}`) {
                    link.classList.add("active");
                }
            });
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const navLinks = document.querySelectorAll(".navbar-nav .nav-link");
    const navbarCollapse = document.querySelector(".navbar-collapse");
    const bsCollapse = new bootstrap.Collapse(navbarCollapse, { toggle: false });

    // 🔹 Cerrar menú con animación suave al hacer clic en un enlace
    navLinks.forEach((link) => {
        link.addEventListener("click", () => {
            if (navbarCollapse.classList.contains("show")) {
                navbarCollapse.classList.remove("show");
                setTimeout(() => bsCollapse.hide(), 300); // sincroniza con la animación CSS
            }
        });
    });
});