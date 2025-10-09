const { jsPDF } = window.jspdf;

// Estado
let listaCampos = [];
let listaAlumnos = [];
let datosExcel = []; // 🔹 almacena la info completa del Excel
let logosBase64 = [];
let firmaBase64 = null;

let pdfCompleto = null;
let primeraHoja = true;
let plantillaFijaSimple = "clasico"; // se mantiene fijo para el PDF simple

// ---------- Helpers de plantilla ----------
function getBoxStyle(plantilla) {
  if (plantilla === "decorado") return "border:2px dashed #e91e63;padding:6px;";
  if (plantilla === "corporativo") return "border:2px solid #004aad;padding:6px;background:#f9f9f9;";
  return "border:1px solid #ccc;padding:6px;";
}
function getHeaderHTML(plantilla, institucion) {
  let style = "";
  if (plantilla === "decorado") style = "color:#e91e63;text-decoration:underline;";
  if (plantilla === "corporativo") style = "border-bottom:2px solid #333;padding-bottom:5px;";
  return `<h2 style="font-size:18px;font-weight:bold;${style}">${institucion || "Observaciones"}</h2>`;
}
function getLogosHTML() {
  if (logosBase64.length === 0) return "";
  if (logosBase64.length === 1) {
    return `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
              <img src="${logosBase64[0]}" style="height:50px;">
              <div style="width:50px;"></div>
            </div>`;
  }
  return `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
            <img src="${logosBase64[0]}" style="height:50px;">
            <img src="${logosBase64[1]}" style="height:50px;">
          </div>`;
}
function fechaLarga(fechaStr) {
  if (!fechaStr) return "";
  try {
    return new Date(fechaStr).toLocaleDateString("es-MX", { day:"numeric", month:"long", year:"numeric" });
  } catch { return ""; }
}

// ---------- SweetAlert mensajes ----------
const warn = (t, m) => Swal.fire(t, m, "warning");
const ok   = (t, m) => Swal.fire(t, m, "success");
const info = (t, m) => Swal.fire(t, m, "info");
const err  = (t, m) => Swal.fire(t, m, "error");

// ---------- UI: Campos personalizados ----------
function renderCampos() {
  const lista = document.getElementById("listaCampos");
  lista.innerHTML = "";
  listaCampos.forEach((c, i) => {
    lista.innerHTML += `
      <li class="flex justify-between items-center bg-gray-100 px-3 py-2 rounded">
        <span>${i + 1}. ${c}</span>
        <div class="space-x-2">
          <button onclick="moverCampo(${i}, -1)" class="px-2 py-1 bg-blue-500 text-white rounded">⬆️</button>
          <button onclick="moverCampo(${i}, 1)" class="px-2 py-1 bg-blue-500 text-white rounded">⬇️</button>
          <button onclick="eliminarCampo(${i})" class="px-2 py-1 bg-red-500 text-white rounded">❌</button>
        </div>
      </li>`;
  });
}
function renderCamposForm() {
  const form = document.getElementById("camposForm");
  if (!form) return;
  form.innerHTML = "";
  listaCampos.forEach(c => {
    const safeId = "campo_" + c.replace(/\s+/g, "_");
    form.innerHTML += `<textarea id="${safeId}" rows="3" placeholder="${c}" class="w-full border rounded-lg px-4 py-2 mb-3"></textarea>`;
  });
}
window.moverCampo = function(index, dir) {
  const ni = index + dir;
  if (ni < 0 || ni >= listaCampos.length) return;
  [listaCampos[index], listaCampos[ni]] = [listaCampos[ni], listaCampos[index]];
  renderCampos(); renderCamposForm();
}
window.eliminarCampo = function(index) {
  const nombre = listaCampos[index];
  listaCampos.splice(index, 1);
  renderCampos(); renderCamposForm();
  info("Eliminado", `Se quitó "${nombre}"`);
}

// ---------- UI: Alumnos ----------
function renderAlumnosSelect() {
  const sel = document.getElementById("alumnoSelect");
  if (!sel) return;
  sel.innerHTML = "";
  listaAlumnos.forEach(a => {
    const op = document.createElement("option");
    op.value = a; op.textContent = a;
    sel.appendChild(op);
  });
}

// ---------- Logos & firma ----------
document.getElementById("logos").addEventListener("change", e => {
  logosBase64 = [];
  Array.from(e.target.files).slice(0, 2).forEach(file => {
    const reader = new FileReader();
    reader.onload = ev => logosBase64.push(ev.target.result);
    reader.readAsDataURL(file);
  });
});
document.getElementById("firma").addEventListener("change", e => {
  const file = e.target.files[0];
  if (!file) { firmaBase64 = null; return; }
  const reader = new FileReader();
  reader.onload = ev => firmaBase64 = ev.target.result;
  reader.readAsDataURL(file);
});

// ---------- Excel a lista + campos ----------
document.getElementById("excelFile").addEventListener("change", function (e) {
  const file = e.target.files[0];
  const reader = new FileReader();
  reader.onload = function (event) {
    const data = new Uint8Array(event.target.result);
    const workbook = XLSX.read(data, { type: "array" });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(sheet);

    if (rows.length === 0) { warn("Error", "El Excel está vacío"); return; }

    // Guardar lista de alumnos
    listaAlumnos = rows.map(row => row["Nombre Alumno"]);
    document.getElementById("listaTexto").value = listaAlumnos.join("\n");
    renderAlumnosSelect();

    // Guardar dataset
    datosExcel = rows;

    // Autorellenar Maestro e Institución
    if (rows[0]["Maestro"]) document.getElementById("maestro").value = rows[0]["Maestro"];
    if (rows[0]["Institucion"]) document.getElementById("institucion").value = rows[0]["Institucion"];

    // Detectar grupo común
    const grupos = [...new Set(rows.map(r => r["Grupo"]).filter(Boolean))];
    if (grupos.length === 1) {
      document.getElementById("grupo").value = grupos[0];
    } else {
      document.getElementById("grupo").value = "";
    }

    // Campos personalizados
    listaCampos = Object.keys(rows[0]).filter(c => !["Nombre Alumno", "Grupo", "Maestro", "Institucion"].includes(c));
    renderCampos(); renderCamposForm();

    ok("Excel cargado", `Se importaron ${listaAlumnos.length} alumnos con ${listaCampos.length} campos personalizados`);
  };
  reader.readAsArrayBuffer(file);
});

// ---------- Autollenar datos al seleccionar alumno ----------
document.getElementById("alumnoSelect").addEventListener("change", function () {
  const alumno = this.value;
  const alumnoData = datosExcel.find(r => r["Nombre Alumno"] === alumno);
  if (!alumnoData) return;

  // Grupo
  if (alumnoData["Grupo"]) document.getElementById("grupo").value = alumnoData["Grupo"];

  // Campos personalizados
  listaCampos.forEach(c => {
    const safeId = "campo_" + c.replace(/\s+/g, "_");
    const el = document.getElementById(safeId);
    if (el) el.value = alumnoData[c] || "";
  });
});

// ---------- PDF SIMPLE ----------
document.getElementById("btnPdfSimple").addEventListener("click", descargarPdfSimple);
async function descargarPdfSimple() {
  const maestro = document.getElementById("maestro").value.trim();
  if (!maestro) { warn("Dato faltante", "El campo Maestro es obligatorio"); return; }
  if (listaAlumnos.length === 0) { warn("Sin alumnos", "Carga la lista de alumnos"); return; }

  plantillaFijaSimple = document.getElementById("plantilla").value;
  const grupo = document.getElementById("grupo").value.trim();
  const institucion = document.getElementById("institucion").value.trim();
  const fecha = document.getElementById("fechaManual").value;

  const pdf = new jsPDF("p", "mm", "a4");
  const plantilla = document.getElementById("plantillaPDF");
  let primera = true;

  for (const alumno of listaAlumnos) {
    plantilla.innerHTML = "";

    // Encabezado
    plantilla.innerHTML += getLogosHTML();
    plantilla.innerHTML += `<div style="text-align:center;margin-bottom:12px;">${getHeaderHTML(plantillaFijaSimple, institucion)}</div>`;

    // Datos
    plantilla.innerHTML += `<p><strong>Alumno:</strong> ${alumno}</p>`;
    plantilla.innerHTML += `<p><strong>Maestro:</strong> ${maestro}</p>`;
    if (grupo) plantilla.innerHTML += `<p><strong>Grupo:</strong> ${grupo}</p>`;
    plantilla.innerHTML += `<br>`;

    // Campos vacíos
    const boxStyle = getBoxStyle(plantillaFijaSimple);
    listaCampos.forEach(c => {
      plantilla.innerHTML += `<div><strong>${c}:</strong><br><div style="${boxStyle};height:90px;"></div></div><br>`;
    });

    // Pie
    const fechaTxt = fechaLarga(fecha);
    if (fechaTxt || firmaBase64) {
      plantilla.innerHTML += `<div style="text-align:center;margin-top:40px;">${
        fechaTxt ? `<p>Fecha: ${fechaTxt}</p>` : ""
      }${firmaBase64 ? `<img src="${firmaBase64}" style="height:50px;margin-top:10px;">` : ""}</div>`;
    }

    // Captura
    plantilla.style.display = "block";
    await new Promise(r => setTimeout(r, 100));
    const canvas = await html2canvas(plantilla, { scale: 2 });
    const img = canvas.toDataURL("image/png");
    if (!primera) pdf.addPage();
    pdf.addImage(img, "PNG", 10, 10, 190, 0);
    primera = false;
    plantilla.style.display = "none";
  }
  pdf.save("Observaciones_Simple.pdf");
  ok("Descargado", "Se descargó el PDF simple");
}

// ---------- PDF COMPLETO ----------
document.getElementById("btnMostrarCompleto").addEventListener("click", () => {
  if (listaAlumnos.length === 0) { warn("Sin alumnos", "Carga la lista de alumnos"); return; }
  document.getElementById("formCompleto").classList.remove("hidden");
  renderAlumnosSelect(); 
  renderCamposForm();
  pdfCompleto = new jsPDF("p", "mm", "a4");
  primeraHoja = true;

  // 🔹 Forzar carga automática del primer alumno
  const sel = document.getElementById("alumnoSelect");
  if (sel.options.length > 0) {
    sel.selectedIndex = 0;
    sel.dispatchEvent(new Event("change"));
  }
});

document.getElementById("btnAgregarHoja").addEventListener("click", agregarHojaCompleta);
async function agregarHojaCompleta() {
  const maestro = document.getElementById("maestro").value.trim();
  if (!maestro) { warn("Dato faltante", "El campo Maestro es obligatorio"); return; }

  const sel = document.getElementById("alumnoSelect");
  const alumno = sel.value;
  if (!alumno) { warn("Falta alumno", "Selecciona un alumno"); return; }

  // Datos del alumno desde Excel
  const alumnoData = datosExcel.find(r => r["Nombre Alumno"] === alumno) || {};

  // Tomamos grupo desde Excel o del input
  const grupo = alumnoData["Grupo"] || document.getElementById("grupo").value.trim();
  const institucion = document.getElementById("institucion").value.trim();
  const fecha = document.getElementById("fechaManual").value;

  const plantilla = document.getElementById("plantillaPDF");
  plantilla.innerHTML = "";

  // 🔹 Plantilla actual (ya no se congela)
  const plantillaActual = document.getElementById("plantilla").value;

  // Encabezado
  plantilla.innerHTML += getLogosHTML();
  plantilla.innerHTML += `<div style="text-align:center;margin-bottom:12px;">${getHeaderHTML(plantillaActual, institucion)}</div>`;

  // Datos básicos
  plantilla.innerHTML += `<p><strong>Alumno:</strong> ${alumno}</p>`;
  plantilla.innerHTML += `<p><strong>Maestro:</strong> ${maestro}</p>`;
  if (grupo) plantilla.innerHTML += `<p><strong>Grupo:</strong> ${grupo}</p>`;
  plantilla.innerHTML += `<br>`;

  // Campos personalizados con valores del Excel
  const boxStyle = getBoxStyle(plantillaActual);
  listaCampos.forEach(c => {
    const valor = alumnoData[c] || "";
    plantilla.innerHTML += `<div><strong>${c}:</strong><br><div style="${boxStyle}">${valor}</div></div><br>`;
  });

  // Pie
  const fechaTxt = fechaLarga(fecha);
  if (fechaTxt || firmaBase64) {
    plantilla.innerHTML += `<div style="text-align:center;margin-top:40px;">${
      fechaTxt ? `<p>Fecha: ${fechaTxt}</p>` : ""
    }${firmaBase64 ? `<img src="${firmaBase64}" style="height:50px;margin-top:10px;">` : ""}</div>`;
  }

  // Captura
  plantilla.style.display = "block";
  await new Promise(r => setTimeout(r, 100));
  const canvas = await html2canvas(plantilla, { scale: 2 });
  const img = canvas.toDataURL("image/png");
  if (!primeraHoja) pdfCompleto.addPage();
  pdfCompleto.addImage(img, "PNG", 10, 10, 190, 0);
  primeraHoja = false;
  plantilla.style.display = "none";

  sel.remove(sel.selectedIndex);
  ok("Hoja agregada", `Se agregó la hoja de "${alumno}"`);
}

document.getElementById("btnGuardarCompleto").addEventListener("click", () => {
  if (!pdfCompleto) { warn("Sin contenido", "Aún no agregas hojas al PDF"); return; }
  pdfCompleto.save("Observaciones_Completo.pdf");
  ok("Descargado", "Se descargó el PDF completo");
});

// ---------- Limpiar todo ----------
document.getElementById("btnLimpiarTodo").addEventListener("click",()=>{
  Swal.fire({
    title:"¿Seguro?",
    text:"Esto borrará todos los datos ingresados",
    icon:"warning",
    showCancelButton:true,
    confirmButtonText:"Sí, limpiar",
    cancelButtonText:"Cancelar"
  }).then(res=>{
    if(res.isConfirmed){
      document.getElementById("maestro").value="";
      document.getElementById("grupo").value="";
      document.getElementById("institucion").value="";
      document.getElementById("fechaManual").value="";
      listaAlumnos=[];
      document.getElementById("listaTexto").value="";
      renderAlumnosSelect();
      listaCampos=[];
      renderCampos();
      renderCamposForm();
      document.getElementById("formCompleto").classList.add("hidden");
      datosExcel=[];
      document.getElementById("excelFile").value = ""; // 🔹 reset para volver a cargar
      Swal.fire("✅ Listo","Se limpió todo","success");
    }
  });
});

// ---------- Actualizar vista previa al cambiar plantilla ----------
document.getElementById("plantilla").addEventListener("change", () => {
  renderCamposForm();
  const sel = document.getElementById("alumnoSelect");
  if (sel && sel.value) {
    sel.dispatchEvent(new Event("change"));
  }
});
