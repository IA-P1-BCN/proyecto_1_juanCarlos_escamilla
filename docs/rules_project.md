Principios de arquitectura limpia

/sessions/kind-determined-allen/mnt/outputs/factoria-f5-deck/assets/logo-factoria-naranja.png

1   Separación de responsabilidades


Cada módulo hace una sola cosa: la lógica de negocio no se mezcla con la base de datos ni con la interfaz.


2   Capas independientes


Puedes cambiar la base de datos o el framework web sin reescribir la lógica central.


3   Bajo acoplamiento


Un cambio en una parte no obliga a tocar diez archivos más.


4   Código testable


Si las piezas están separadas, puedes probar cada una por su cuenta.


Ninguno de estos principios es nuevo — lo nuevo es que ahora también los sigue el agente que 
escribe contigo.


Ejemplo real: TaxiTech Taxímetro

/sessions/kind-determined-allen/mnt/outputs/factoria-f5-deck/assets/icon_target.png

Briefing: un taxímetro digital en Python. Calcula tarifa en tiempo real, guarda histórico, y crece en 4 fases hasta tener API y panel web.


CLI que calcula la tarifa de una carrera.


Logs, histórico en disco, tarifas configurables.


Refactor a POO, contraseña, interfaz gráfica.


1   MVP


2   Observabilidad


3   Arquitectura y UX


4   Producción


Base de datos, API REST, panel web, un solo comando.


El reto: diseñar desde la Fase 1 una estructura que aguante hasta la Fase 4 sin reescribirse entera.


Estructura de carpetas recomendada

/sessions/kind-determined-allen/mnt/outputs/factoria-f5-deck/assets/logo-factoria-naranja.png
taximetro/

├── src/

│   ├── domain/           # Carrera, Tarifa — reglas de negocio puras

│   ├── application/      # Casos de uso: iniciar, cambiar_estado, finalizar

│   ├── infrastructure/   # Persistencia (fichero → BD), logging, config

│   └── interfaces/       # cli.py · gui.py · api.py · web/

├── config/tarifas.json

├── logs/

├── tests/

└── README.md

#Qué va en cada capa y por qué

/sessions/kind-determined-allen/mnt/outputs/factoria-f5-deck/assets/logo-factoria-naranja.png
Capa

Qué contiene

Por qué se aísla

domain

Carrera, Tarifa: cálculo del importe

No depende de nada — se testea sola y no cambia entre fases

application

iniciar, cambiar_estado, finalizar, consultar

Orquesta el domain sin saber si hay CLI, GUI o API detrás

infrastructure

Guardar historial, logs, leer config

Cambiar fichero por base de datos no toca el resto del código

interfaces

cli.py, gui.py, api.py, web/

Cada fase añade una puerta de entrada nueva sobre la misma lógica

#Cómo escala fase a fase

/sessions/kind-determined-allen/mnt/outputs/factoria-f5-deck/assets/logo-factoria-naranja.png

1   Fase 1 — MVP


Solo domain + application + interfaces/cli.py. El resto de carpetas ni existen todavía.


2   Fase 2 — Observabilidad


Se añade infrastructure/ (logging, historial en fichero, config de tarifas).


3   Fase 3 — Arquitectura y UX


El domain se reorganiza en clases; se añade interfaces/gui.py y autenticación.


4   Fase 4 — Producción


infrastructure/ cambia de fichero a base de datos; se añaden interfaces/api.py y web/.


Lo importante: en ninguna fase se reescribe domain ni application — solo se añaden o sustituyen piezas alrededor.




#La base para colaborar con agentes de IA

/sessions/kind-determined-allen/mnt/outputs/factoria-f5-deck/assets/logo-factoria-naranja.png

Código desordenado


El agente no sabe dónde encaja cada cambio.


Genera parches inconsistentes con el resto.


Tú acabas revisando línea por línea.


Código limpio + PEP 8


El agente entiende la estructura y dónde añadir cada pieza.


Sus cambios siguen el mismo estilo que ya tienes.


Revisas el diseño, no el formato.


La idea final: PEP 8 y la arquitectura limpia no son "burocracia" — son lo que hace que humanos y agentes de IA trabajen sobre el mismo código sin pisarse.
