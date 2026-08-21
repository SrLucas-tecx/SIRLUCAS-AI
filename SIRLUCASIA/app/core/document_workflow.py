import logging

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

from app.IA.ollama_client import OllamaClient
from app.IA.prompt_manager import PromptManager


logger = logging.getLogger(__name__)


class DocumentWorkflow:
    """
    Coordina la creación y escritura de documentos
    utilizando Ollama para generar contenido.

    Flujo principal:

        create_with_ai()
            ↓
        crear documento
            ↓
        construir prompt
            ↓
        Ollama genera contenido
            ↓
        escribir contenido
    """

    def __init__(
        self,
        document_manager,
        ollama_client=None,
        prompt_manager=None,
    ):

        self.document_manager = document_manager

        self.ollama = (
            ollama_client
            or OllamaClient()
        )

        self.prompt_manager = (
            prompt_manager
            or PromptManager()
        )

        logger.info(
            "[DocumentWorkflow] Inicializado correctamente."
        )

    # ==================================================
    # ROUTER
    # ==================================================

    def execute(self, data):

        command = (
            data.get("command")
            if isinstance(data, dict)
            else None
        )

        method = (
            getattr(self, command, None)
            if command
            else None
        )

        if (
            method is None
            or not callable(method)
            or command.startswith("_")
        ):

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command=command,
                message=(
                    f"No existe la acción "
                    f"'{command}'."
                ),
                error=(
                    f"Acción '{command}' no "
                    f"implementada en DocumentWorkflow."
                )
            )

        return method(data)

    # ==================================================
    # CREAR DOCUMENTO Y GENERAR CONTENIDO CON IA
    # ==================================================

    def create_with_ai(self, data):
        """
        Crea un documento y utiliza Ollama
        para generar su contenido.

        Ejemplo:

        {
            "command": "create_with_ai",
            "topic": "ensayo_ia",
            "format": "docx",
            "instruction":
                "Escribe un ensayo sobre inteligencia artificial",
            "context": "..."
        }
        """

        name = data.get("topic")

        instruction = (
            data.get("instruction")
            or data.get("message")
            or data.get("content")
        )

        format_name = (
            data.get("format")
            or "docx"
        )

        context_text = (
            data.get("context")
            or ""
        )

        # ==============================================
        # VALIDACIONES
        # ==============================================

        if not name:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="create_with_ai",
                message=(
                    "No especificaste el nombre "
                    "del documento."
                ),
                error="Campo 'topic' vacío."
            )

        if not instruction:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="create_with_ai",
                message=(
                    "No especificaste qué debe "
                    "escribir la IA."
                ),
                error=(
                    "Se requiere 'instruction', "
                    "'message' o 'content'."
                )
            )

        # ==============================================
        # VERIFICAR OLLAMA
        # ==============================================

        if not self.ollama.is_available():

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="create_with_ai",
                message=(
                    "Ollama no está disponible."
                ),
                error=(
                    "No se pudo conectar con "
                    "el servidor de Ollama."
                )
            )

        try:

            # ==========================================
            # 1. CREAR DOCUMENTO
            # ==========================================

            create_result = (
                self.document_manager.create(
                    {
                        "topic": name,
                        "format": format_name,
                    }
                )
            )

            if not create_result.success:

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="create_with_ai",
                    message=(
                        "No pude crear el documento."
                    ),
                    error=(
                        create_result.error
                        or create_result.message
                    )
                )

            # ==========================================
            # OBTENER NOMBRE DEL ARCHIVO
            # ==========================================

            filename = name

            if (
                isinstance(
                    create_result.data,
                    dict
                )
            ):

                filename = (
                    create_result.data.get(
                        "filename"
                    )
                    or create_result.data.get(
                        "topic"
                    )
                    or name
                )

            # ==========================================
            # 2. CONSTRUIR INSTRUCCIÓN PARA LA IA
            # ==========================================

            ai_message = f"""
Genera el contenido para un documento.

TÍTULO O NOMBRE DEL DOCUMENTO:
{name}

INSTRUCCIÓN DEL USUARIO:
{instruction}

REGLAS IMPORTANTES:

- Escribe únicamente el contenido que debe ir dentro del documento.
- No digas "aquí tienes el documento".
- No expliques lo que vas a hacer.
- No inventes que el documento ya fue creado.
- No hables como asistente.
- Genera contenido claro, útil y bien estructurado.
"""

            prompt = self.prompt_manager.build(
                ai_message,
                context_text
            )

            # ==========================================
            # 3. GENERAR CONTENIDO CON OLLAMA
            # ==========================================

            generated_content = (
                self.ollama.generate(
                    prompt
                )
            )

            # ==========================================
            # VALIDAR RESPUESTA
            # ==========================================

            if not generated_content:

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="create_with_ai",
                    message=(
                        "Ollama no generó contenido."
                    ),
                    error="Respuesta vacía."
                )

            # ==========================================
            # DETECTAR ERRORES DE OLLAMA
            # ==========================================

            if generated_content.startswith("⚠️"):

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="create_with_ai",
                    message=(
                        "El documento fue creado, "
                        "pero Ollama no pudo generar "
                        "el contenido."
                    ),
                    error=generated_content
                )

            # ==========================================
            # 4. ESCRIBIR CONTENIDO
            # ==========================================

            write_result = (
                self.document_manager.write(
                    {
                        "topic": filename,
                        "content": generated_content
                    }
                )
            )

            if not write_result.success:

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="create_with_ai",
                    message=(
                        "El documento fue creado y "
                        "Ollama generó el contenido, "
                        "pero no se pudo escribir."
                    ),
                    error=(
                        write_result.error
                        or write_result.message
                    )
                )

            # ==========================================
            # RESULTADO FINAL
            # ==========================================

            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="document_workflow",
                command="create_with_ai",
                message=(
                    f"Documento '{filename}' "
                    "creado y completado correctamente."
                ),
                data={
                    "filename": filename,
                    "format": format_name,
                    "content": generated_content
                }
            )

        except Exception as e:

            logger.exception(
                "[DocumentWorkflow] Error "
                "en create_with_ai."
            )

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="create_with_ai",
                message=(
                    "Ocurrió un error durante "
                    "la creación del documento."
                ),
                error=str(e)
            )

    # ==================================================
    # ESCRIBIR CONTENIDO CON IA EN DOCUMENTO EXISTENTE
    # ==================================================

    def write_with_ai(self, data):
        """
        Genera contenido con Ollama y lo agrega
        a un documento existente.

        Ejemplo:

        {
            "command": "write_with_ai",
            "topic": "ensayo_ia",
            "instruction":
                "Agrega una conclusión."
        }
        """

        name = data.get("topic")

        instruction = (
            data.get("instruction")
            or data.get("message")
            or data.get("content")
        )

        context_text = (
            data.get("context")
            or ""
        )

        # ==============================================
        # VALIDACIONES
        # ==============================================

        if not name:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="write_with_ai",
                message=(
                    "No especificaste el documento."
                ),
                error="Campo 'topic' vacío."
            )

        if not instruction:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="write_with_ai",
                message=(
                    "No especificaste qué debe "
                    "escribir la IA."
                ),
                error="Campo 'instruction' vacío."
            )

        # ==============================================
        # VERIFICAR OLLAMA
        # ==============================================

        if not self.ollama.is_available():

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="write_with_ai",
                message=(
                    "Ollama no está disponible."
                ),
                error="No se pudo conectar con Ollama."
            )

        try:

            # ==========================================
            # LEER DOCUMENTO ACTUAL
            # ==========================================

            read_result = (
                self.document_manager.read(
                    {
                        "topic": name
                    }
                )
            )

            if not read_result.success:

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="write_with_ai",
                    message=(
                        "No pude leer el documento."
                    ),
                    error=(
                        read_result.error
                        or read_result.message
                    )
                )

            # ==========================================
            # EXTRAER CONTENIDO ACTUAL
            # ==========================================

            current_content = ""

            if isinstance(
                read_result.data,
                dict
            ):

                current_content = (
                    read_result.data.get(
                        "content",
                        ""
                    )
                )

            # ==========================================
            # LIMITAR CONTENIDO ENVIADO A OLLAMA
            # ==========================================

            max_document_chars = 6000

            if len(current_content) > max_document_chars:

                current_content = (
                    current_content[
                        -max_document_chars:
                    ]
                )

            # ==========================================
            # CREAR PROMPT
            # ==========================================

            ai_message = f"""
Estás ayudando a continuar un documento existente.

CONTENIDO ACTUAL:

{current_content}

NUEVA INSTRUCCIÓN:

{instruction}

REGLAS:

- Genera únicamente el contenido nuevo.
- No repitas todo el documento.
- Mantén coherencia con el texto existente.
- No expliques que estás modificando un documento.
- No escribas frases dirigidas al usuario.
"""

            prompt = self.prompt_manager.build(
                ai_message,
                context_text
            )

            # ==========================================
            # GENERAR CONTENIDO
            # ==========================================

            generated_content = (
                self.ollama.generate(
                    prompt
                )
            )

            if not generated_content:

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="write_with_ai",
                    message=(
                        "Ollama no generó contenido."
                    ),
                    error="Respuesta vacía."
                )

            if generated_content.startswith("⚠️"):

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="write_with_ai",
                    message=(
                        "No se pudo generar "
                        "el contenido."
                    ),
                    error=generated_content
                )

            # ==========================================
            # ESCRIBIR EN DOCUMENTO
            # ==========================================

            write_result = (
                self.document_manager.write(
                    {
                        "topic": name,
                        "content": generated_content
                    }
                )
            )

            if not write_result.success:

                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="document_workflow",
                    command="write_with_ai",
                    message=(
                        "El contenido fue generado, "
                        "pero no se pudo escribir "
                        "en el documento."
                    ),
                    error=(
                        write_result.error
                        or write_result.message
                    )
                )

            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="document_workflow",
                command="write_with_ai",
                message=(
                    f"Contenido agregado correctamente "
                    f"a '{name}'."
                ),
                data={
                    "filename": name,
                    "generated_content": (
                        generated_content
                    )
                }
            )

        except Exception as e:

            logger.exception(
                "[DocumentWorkflow] Error "
                "en write_with_ai."
            )

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="document_workflow",
                command="write_with_ai",
                message=(
                    "Ocurrió un error al generar "
                    "el contenido."
                ),
                error=str(e)
            )