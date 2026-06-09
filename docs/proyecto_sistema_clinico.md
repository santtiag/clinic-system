1   
Avance Proyecto – Sistema Clínico.   
Avance Proyecto – Sistema Clínico.   
Eliel Berrio Ramos   
Santiago Romero Solana   
Trabajo presentado como requisito del Electiva Profesional de Ingeniería del Software   
Noveno semestre   
Docente   
Laudyt María Lambraño Pérez   
Corporación Universitaria del Caribe – CECAR   
Facultad de Ciencias Básicas, Ingenierías y Arquitectura   
Ingeniería de Sistemas   
Electiva Profesional de Ingeniería del Software   
Sincelejo, Sucre   
2026   
   
2   
Avance Proyecto – Sistema Clínico.   
**Tabla de Contenido**   
Introducción ................................................................................................................................................... 2   
Descripción de la problemática ..................................................................................................................... 4   
Alcance ........................................................................................................................................................... 4   
Metodología de Desarrollo de Software ....................................................................................................... 5   
Requisitos Funcionales y No Funcionales ...................................................................................................... 6   
Requisitos Funcionales...................................................................................................................... 6   
Requisitos No Funcionales ................................................................................................................ 8   
Conclusiones ................................................................................................................................................10   
Referencias Bibliográficas ............................................................................................................................11   
   
3   
Avance Proyecto – Sistema Clínico.   
# **Introducción **  
La digitalización de procesos en el sector salud se ha convertido en un dominador para   
garantizar la eficiencia operativa y la calidad de la atención médica en las instituciones modernas.   
En este contexto, la tecnología emerge como un participante operativo importante dentro de   
cualquier organización, aportando eficiencia, digitalización y automatización en las tareas y   
responsabilidades propias de estos entornos. Particularmente, en el caso de la clínica, surge la   
necesidad absoluta de transformar digitalmente cada uno de los procesos que se llevan a cabo   
dentro de la misma, lo que conlleva a la integración de componentes pertenecientes a diversas   
áreas identificadas, entre las que se encuentran la gestión de pacientes, el agendamiento de citas,   
el manejo de historias clínicas, la facturación y los reportes médicos.    
Frente a este escenario de transformación digital, se propone el diseño y desarrollo de una   
arquitectura de microservicios que permita registrar pacientes, agendar citas médicas, procesar   
pagos electrónicos y gestionar historiales clínicos con los niveles de seguridad y trazabilidad   
requeridos en el sector salud, utilizando como fundamento metodológico los principios de   
Domain-Driven Design (DDD) para garantizar que la solución tecnológica responda fielmente a   
las complejidades del dominio clínico. Siendo así, el propósito de esta propuesta es otorgar un   
sistema software clínico que no solo aporte tecnología y digitalización a los procesos tradicionales,   
sino que todo el desarrollo esté alineado estratégicamente al dominio específico del área clínica   
que se está abordando, permitiendo acoger las necesidades de calidad asociadas al sector, entre las   
que destacan la escalabilidad para soportar picos de demanda, la seguridad en el manejo de   
información sensible, la disponibilidad continua del servicio y la mantenibilidad a largo plazo del   
sistema.   
   
4   
Avance Proyecto – Sistema Clínico.   
# **Descripción de la problemática **  
Actualmente, la clínica opera con sistemas tradicionales que, aunque permiten llevar a cabo   
las operaciones básicas de gestión administrativa y clínica, ocasionan ineficiencias operativas   
significativas que comprometen la calidad del servicio y la experiencia tanto de pacientes como   
del personal médico. Estos sistemas presentan problemas estructurales relacionados con una poca   
distribución de las responsabilidades entre los diferentes módulos funcionales, una excesiva   
independencia entre los distintos dominios de la organización que impide la comunicación fluida   
entre procesos, y una preocupante ausencia de seguridad robusta en el tratamiento de la   
información de los pacientes y sus historiales médicos.   
Por consiguiente, la ausencia de límites claros entre los distintos contextos del negocio   
médico dificulta el mantenimiento del sistema, complica la asignación de responsabilidades   
técnicas y compromete la capacidad de respuesta ante picos de demanda en la atención médica,   
obstaculizando cualquier intento de mejora continua o adaptación a nuevas regulaciones del sector   
salud. Ante este panorama de obsolescencia tecnológica y operativa, se hace evidente la necesidad   
de migrar hacia una arquitectura moderna basada en microservicios que permita comprender cuál   
es el dominio de este sistema clínico, identificando claramente los distintos contextos delimitados   
en cuestión.   
   
5   
Avance Proyecto – Sistema Clínico.   
# **Alcance **  
El proyecto abarca el diseño e implementación de una plataforma integral de gestión clínica   
basada en microservicios, la cual integra los dominios operativos de la institución médica   
incluyendo gestión de identidad y acceso, agendamiento de citas, historias clínicas electrónicas,   
facturación con pasarelas de pago, reportes médicos y panel administrativo, organ izados mediante   
Domain-Driven Design en subdominios core, de apoyo y genéricos según su criticidad para el   
negocio. Adicionalmente, el alcance contempla la aplicación de la metodología de desarrollo   
Extreme Programming (XP) a lo largo de todo el ciclo de vida del proyecto, asegurando prácticas   
ágiles que garanticen la calidad técnica, la retroalimentación frecuente y la adaptabilidad ante   
cambios en los requerimientos. Para este primer avance documental, el alcance se reduce   
específicamente a la elaboración de la Introducción, la Descripción de la Problemática y la   
definición general del Alcance del sistema, estableciendo las bases conceptuales necesarias para   
el desarrollo posterior de la solución que cumplan los requisitos de escalabilidad, seguridad y   
disponibilidad establecidos.   
# **Metodología de Desarrollo de Software **  
Para el desarrollo de la plataforma de gestión clínica basada en microservicios, se ha   
seleccionado una metodología ágil adaptada que responda a las características específicas del   
equipo de trabajo y del proyecto. Considerando que el equipo de desarrollo está conformado   
únicamente por dos integrantes, resulta optar por un enfoque que maximice la productividad sin   
sobrecargar con ceremonias excesivas que podrían ralentizar el progreso del proyecto. Así mismo,   
se propone Extreme Programming (XP) como metodología principal, complementada con   
elementos de Kanban para la gestión visual del flujo de trabajo. XP resulta especialmente   
apropiada para equipos reducidos debido a que sus prácticas fundamentales, como la programación   
en parejas, el desarrollo guiado por pruebas (TDD), la integración continua y las iteraciones cortas,   
se adaptan perfectamente a trabajo colaborativo en equipos pequeños. Habría que decir también,   
que esta metodología permite mantener un ritmo de desarrollo sostenible, fomenta la comunicación   
   
6   
Avance Proyecto – Sistema Clínico.   
constante entre los desarrolladores y facilita la detección temprana de errores, aspectos importantes   
cuando se trabaja en un sistema que maneja información sensible como lo es una plataforma de   
gestión clínica con datos de pacientes e historiales médicos.   
Además, la selección de XP también se justifica por la naturaleza del proyecto, que requiere   
diseñar una arquitectura de microservicios aplicando principios de Domain-Driven Design para   
abordar las necesidades de escalabilidad, seguridad y disponibilidad del sistema clínico. Siendo   
así, las prácticas de XP como el desarrollo iterativo e incremental permiten abordar los seis   
bounded contexts identificados de manera progresiva, priorizando aquellos que conforman el core   
domain como la Gestión de Identidad y Acceso, el Agendamiento de Citas y la Historia Clínica,   
para luego continuar con los subdominios de apoyo y genéricos. Adicionalmente, Kanban se   
incorporará como herramienta complementaria para visualizar el estado de las tareas en un tablero   
que muestre las columnas de pendiente, en progreso, en revisión y completado, limitando el trabajo   
en progreso para evitar dispersión en múltiples frentes simultáneamente.   
7   
Avance Proyecto – Sistema Clínico.   
# **Conclusiones **  
El presente trabajo plantea desarrollar el diseño de una plataforma de gestión clínica,   
abordando la digitalización integral de los procesos médicos y administrativos de la institución.   
Mediante la aplicación de Domain-Driven Design (DDD), se identificaron y delimitaron seis   
bounded contexts —Gestión de Pacientes y Personal Médico, Agendamiento de Citas, Facturación   
y Pagos Electrónicos, Historia Clínica Electrónica, Reportes Médicos y Panel Administrativo—   
permitiendo modelar el dominio clínico de manera alineada con el negocio real y superando las   
ineficiencias de los sistemas tradicionales. La adopción de Extreme Programming adaptada a un   
equipo de dos personas facilita la gestión ágil del desarrollo, asegurando calidad técnica y   
cumplimiento de los requisitos funcionales y no funcionales priorizados. Así mismo, el sistema   
resultante satisface las necesidades de escalabilidad, seguridad, disponibilidad y mantenibilidad,   
estableciendo una base tecnológica que permite la evolución independiente de cada componente y   
garantizando el tratamiento seguro de la información médica sensible. 
