const fs = require("fs");
const vm = require("vm");
const path = require("path");

const desktopPath = path.join(require("os").homedir(), "Desktop", "Airbus_ESOP.html");
const indexPath = path.join(__dirname, "index.html");

// 1. Verificar existencia e integridad
if (!fs.existsSync(indexPath)) {
  throw new Error("index.html no encontrado");
}
const indexHtml = fs.readFileSync(indexPath, "utf8");

if (fs.existsSync(desktopPath)) {
  const desktopHtml = fs.readFileSync(desktopPath, "utf8");
  if (desktopHtml !== indexHtml) {
    throw new Error("El archivo en el Escritorio difiere de index.html");
  }
  console.log("✅ Archivo Desktop idéntico a index.html");
}

// 2. Extraer script principal del frontend para ejecutar pruebas en entorno VM
const scripts = [...indexHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if (scripts.length === 0) {
  throw new Error("No se encontró ninguna etiqueta <script> en index.html");
}
const scriptContent = scripts[scripts.length - 1][1];

// Simulación de DOM y localStorage
const storage = {};
const mockLocalStorage = {
  getItem: (k) => (k in storage ? storage[k] : null),
  setItem: (k, v) => { storage[k] = String(v); },
  removeItem: (k) => { delete storage[k]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); }
};

// Crear elementos mock mínimos para DOM
const elements = {};
function getOrCreateElem(id) {
  if (!elements[id]) {
    elements[id] = {
      id,
      innerHTML: "",
      textContent: "",
      value: "",
      dataset: {},
      style: {},
      children: [],
      classList: {
        add: () => {},
        remove: () => {},
        contains: () => false,
        toggle: () => {}
      },
      appendChild: function(c) { this.children.push(c); },
      querySelectorAll: () => [],
      querySelector: () => null,
      addEventListener: () => {}
    };
  }
  return elements[id];
}

const context = {
  console,
  document: {
    getElementById: (id) => getOrCreateElem(id),
    querySelectorAll: () => [],
    querySelector: () => null,
    createElement: (tag) => ({
      tagName: tag,
      innerHTML: "",
      textContent: "",
      setAttribute: () => {},
      appendChild: () => {},
      classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false }
    }),
    documentElement: {
      classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false }
    },
    addEventListener: () => {}
  },
  localStorage: mockLocalStorage,
  confirm: () => true,
  alert: (msg) => console.log("   [Alerta]:", msg),
  prompt: () => "ESOP_Venta.json",
  setTimeout: () => {},
  setInterval: () => {},
  URL: { createObjectURL: () => "", revokeObjectURL: () => {} }
};
context.window = context;
context.globalThis = context;
context.location = { reload: () => {} };
context.addEventListener = () => {};

vm.createContext(context);
vm.runInContext(scriptContent, context);

// 3. Verificaciones de la lógica
console.log("\n--- TEST: ESTADO EN BLANCO INICIAL ---");
const initialLots = context.getStoredLots();
const initialSales = context.getStoredSales();
console.log("Lotes iniciales:", initialLots.length);
console.log("Ventas iniciales:", initialSales.length);

if (initialLots.length !== 0) {
  throw new Error(`Se esperaban 0 lotes iniciales, pero se obtuvieron ${initialLots.length}`);
}
if (initialSales.length !== 0) {
  throw new Error(`Se esperaban 0 ventas iniciales, pero se obtuvieron ${initialSales.length}`);
}
console.log("✅ Cartera arranca 100% en blanco.");

console.log("\n--- TEST: REGISTRO DE PAQUETE PERSONALIZADO ---");
const testLot = {
  id: "ESOP-2024",
  year: 2024,
  grant_date: "2024-05-15",
  unlock_date: "2027-05-15",
  purchased_shares: 30,
  matching_shares: 20,
  total_shares: 50,
  purchase_price: 150.26,
  total_paid: 4507.80,
  status: "LOCKED",
  notes: "Test 30+20"
};
context.saveStoredLots([testLot]);
const loadedLots = context.getStoredLots();
if (loadedLots.length !== 1 || loadedLots[0].id !== "ESOP-2024") {
  throw new Error("Fallo al guardar o recuperar el paquete personalizado");
}
console.log("✅ Paquete personalizado guardado correctamente:", loadedLots[0].id);

console.log("\n--- TEST: ELIMINACIÓN DE PAQUETE ---");
context.deleteLot("ESOP-2024");
const remainingLots = context.getStoredLots();
console.log("Lotes restantes tras eliminar:", remainingLots.length);
if (remainingLots.length !== 0) {
  throw new Error(`Fallo en deleteLot: quedan ${remainingLots.length} lotes`);
}
console.log("✅ Eliminación de paquete verificada con éxito.");

console.log("\n--- TEST: VACIAR CARTERA (resetData) ---");
// Añadir un paquete y ejecutar resetData
mockLocalStorage.setItem(context.STORAGE_KEY, JSON.stringify([testLot]));
context.resetData();
const afterResetLots = context.getStoredLots();
if (afterResetLots.length !== 0) {
  throw new Error("resetData() no dejó la cartera vacía");
}
console.log("✅ 'Vaciar Cartera' restablece a cero paquetes (sin recrear los de prueba).");

console.log("\n🎉 TODAS LAS PRUEBAS DE AUTOMATIZACIÓN PASARON CORRECTAMENTE.");
