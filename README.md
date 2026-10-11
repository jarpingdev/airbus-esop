# Airbus ESOP Manager & Simulator (España)

Herramienta en Python para el seguimiento patrimonial, simulación fiscal y optimización de compras y ventas de acciones en el programa **ESOP de Airbus**.

---

## 🚀 ¿Cómo ejecutar el programa?

Tienes **dos formas** de utilizar el programa, según tu preferencia:

### 1. 🌐 Versión Visual (Panel Web Interactivo - Recomendado)
Abre un dashboard gráfico moderno en tu navegador web con tarjetas, sliders en tiempo real, gráficos y botones interactivos:

```bash
cd /Users/joseantonio/Developer/airbus_esop
.venv/bin/python app.py
```
*(Se abrirá automáticamente en tu navegador en `http://localhost:5050`, y además puedes abrirlo desde cualquier tablet/móvil en tu red Wi-Fi)*

---

### 2. 💻 Versión Terminal (Consola de Comandos)
Para consultas rápidas o entornos de línea de comandos:

```bash
cd /Users/joseantonio/Developer/airbus_esop
.venv/bin/python airbus_esop.py
```

O si solo quieres ver un resumen rápido de tu cartera:

```bash
cd /Users/joseantonio/Developer/airbus_esop
.venv/bin/python airbus_esop.py --status
```

---

## 🔄 Sincronización Total en Tiempo Real
Ambas versiones (Web y Terminal) comparten la misma base de datos en:
`data/portfolio.json`

* **Cualquier lote que agregues, edites o elimines en la versión web se refleja al instante en la versión de terminal.**
* **Cualquier cambio hecho desde la consola se actualiza de inmediato en el panel web.**

---

## ☁️ Acceso y Ejecución en Servidor Remoto Ubuntu

La aplicación está completamente desplegada y configurada como servicio permanente en tu servidor Ubuntu (`82.70.77.208`):

### 1. Panel Web 24/7 en el Servidor
El servidor web corre como servicio `systemd` en segundo plano:
* **URL directa:** `http://82.70.77.208:5050` *(o vía túnel SSH: `ssh -L 5050:localhost:5050 oracle` y abrir `http://localhost:5050`)*
* **Comandos del servicio:**
  ```bash
  ssh oracle "sudo systemctl status airbus-esop"    # Ver estado
  ssh oracle "sudo systemctl restart airbus-esop"   # Reiniciar
  ssh oracle "sudo systemctl stop airbus-esop"      # Detener
  ```

### 2. Versión Terminal desde Cualquier Lugar (SSH)
Puedes consultar el estado o interactuar con el menú directamente desde cualquier terminal o móvil con SSH:
```bash
# Informe rápido en pantalla:
ssh oracle "airbus --status"

# Menú interactivo completo:
ssh -t oracle "airbus"
```

### 3. Sincronización entre Mac y Servidor
Para sincronizar cambios en `portfolio.json` entre tu Mac y el servidor:
```bash
# Subir datos del Mac al Servidor:
rsync -avz /Users/joseantonio/Developer/airbus_esop/data/ oracle:/home/ubuntu/airbus_esop/data/

# Bajar datos del Servidor al Mac:
rsync -avz oracle:/home/ubuntu/airbus_esop/data/ /Users/joseantonio/Developer/airbus_esop/data/
```

---

## 🛠️ Funcionalidades Principales

1. **📊 Estado de Cartera en Tiempo Real:**
   - Conexión directa con la cotización oficial de Airbus en Euronext París (`AIR.PA`).
   - Muestra tu lote de 2024 (15 pagadas + 12 regaladas = 27 acciones).
   - Contador de días restantes hasta el desbloqueo legal de los 3 años.
   - Cálculo automático de rentabilidad bruta y valor total.

2. **💰 Simulador de Venta y Fiscalidad IRPF (España):**
   - Simula la venta a precio de mercado o a un precio objetivo definido por ti.
   - Valida el cumplimiento del plazo de 3 años para mantener la exención fiscal del regalo de Airbus (*Art. 42.3.f de la Ley de IRPF*).
   - Aplica los tramos de la base del ahorro del IRPF (19% hasta 6.000 €, 21% entre 6.000 € y 50.000 €, etc.).
   - Muestra el **dinero neto limpio en cuenta bancaria**.

3. **🎯 Optimizador de Compra ESOP 2027:**
   - Compara los paquetes oficiales de Airbus con la cotización estimada y tu presupuesto disponible.
   - Recomienda el mejor paquete para maximizar el descuento de acciones gratuitas.
   - Calcula cuánto dinero sobrante de la venta de 2024 te queda para diversificar.

4. **📅 Exportador de Recordatorios (.ics):**
   - Genera el archivo `airbus_esop_recordatorios.ics` para Mac Calendar / Google Calendar.
   - Incluye aviso de apertura de la campaña en febrero de 2027 y la fecha exacta de desbloqueo en mayo de 2027.

5. **➕ Registro de Nuevos Lotes:**
   - Permite añadir la compra de 2027 y futuras campañas para mantener la rueda trienal funcionando de forma continuada.

6. **❓ Preguntas Frecuentes (FAQ) y Guía Estratégica:**
   - Explicación a fondo de por qué NO es recomendable acumular acciones de Airbus y por qué la venta sistemática al desbloquear protege tu patrimonio contra el riesgo de concentración.
   - Guía detallada de cada opción del menú (1 a 5).
   - Detalles fiscales para el IRPF en España y guía paso a paso de operativa en Equiniti.

---

## 👨‍💻 Sobre el Creador / About Me

> *"Automatizando lo complejo, simplificando lo cotidiano."*

¡Hola! Soy **Jose Antonio** ([@jarpingdev](https://github.com/jarpingdev)).

Apasionado por el desarrollo de software, la tecnología y el sector aeroespacial. Mi filosofía es simple: construir herramientas prácticas que solucionen problemas del día a día, sustituyendo la fricción y las hojas de cálculo aburridas por código limpio, automatizaciones y experiencias interactivas.

* ✈️ **Visión:** Conectando ingeniería, finanzas personales y tecnología en el entorno de Airbus para que cualquiera pueda tomar decisiones informadas sin perderse en el papeleo.
* 🐍 **Stack:** Python, arquitecturas web ligeras, automatización de sistemas (Linux/macOS), APIs y despliegues en la nube.
* 💡 **Dato curioso:** Si un proceso se tiene que hacer más de dos veces, prefiero crear un simulador en tiempo real con fiscalidad del IRPF integrada antes que usar un Excel.
* 📬 **Contacto:** [GitHub @jarpingdev](https://github.com/jarpingdev)
