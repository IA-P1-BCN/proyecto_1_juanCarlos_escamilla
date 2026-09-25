# TaxiTech Taxímetro — Lenguaje Ubicuo

Glossary for the taximeter system (TTX-247). Canonical terms are Spanish, matching
`docs/CLIENT_SPECS.md`; package names are English (`ride`, `pricing`, `identity`,
`fleet`). Terms are grouped by the bounded context that owns them — the owner is the
only place that defines the term's model.

## Ride — carrera

**Carrera**:
El servicio de taxi: se inicia, cambia de estado y finaliza. Aggregate root del contexto ride.
_Avoid_: viaje, ride, servicio, trayecto

**Estado**:
Situación del vehículo durante la carrera: `parada` o `en_movimiento` (English aliases in code: stopped / moving).
_Avoid_: modo, fase

**Importe**:
Total en euros acumulado de una carrera, calculado por el motor de tarifas.
_Avoid_: total, precio, coste

**Taxista**:
Conductor que opera la carrera e interactúa con el sistema.
_Avoid_: conductor, usuario, driver

**Pasajero**:
Persona transportada que paga el importe al finalizar. No interactúa con el sistema.
_Avoid_: cliente, customer

## Pricing — tarifas

**Tarifa**:
Par de precios vigentes en €/segundo: parada y en movimiento. Value object whose provisioning is owned by pricing.
_Avoid_: precio, rate, tarifa horaria

**Motor de tarifas**:
Componente de pricing que calcula el importe aplicando la tarifa vigente a la actividad de la carrera.
_Avoid_: calculadora, pricing engine

## Fleet — histórico y caja

**Histórico**:
Registro de carreras finalizadas (del día), consultable por el responsable de flota.
_Avoid_: historial, log, history

**CarreraRegistro**:
Representación inmutable de una carrera cerrada (fecha, duración, importe) dentro de fleet. Modelo propio de fleet — no es el aggregate de ride.
_Avoid_: carrera histórica

**InformeCaja**:
Resumen diario de importes con el que el responsable de flota cuadra caja.
_Avoid_: reporte, factura, informe de ventas

**Responsable de flota**:
Actor que consulta el Histórico y cuadra caja. No conduce carreras.
_Avoid_: admin, manager, fleet manager

## Planificación

**Fase**:
Cada uno de los 4 entregables incrementales del proyecto: MVP, Observabilidad, Arquitectura y UX, Producción.
_Avoid_: milestone, sprint, iteración
