from app.core.action_result import ActionResult


class ResponseFormatter:

    def format(self, result):

        if result is None:
            return "No hubo respuesta."

        if not isinstance(result, ActionResult):
            return str(result)

        # Si el manager no devolvió mensaje
        if not result.message:
            return "Operación completada."

        return result.message