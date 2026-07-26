class ActionOptimizer:

    def optimize(self, actions, context):

        optimized = []

        for action in actions:

            # ----------------------------
            # DOCUMENTOS
            # ----------------------------
            if action.module == "document":

                if not action.topic:
                    action.topic = context.document()

                if action.command == "write" and not action.content:
                    continue

            # ----------------------------
            # SISTEMA
            # ----------------------------
            elif action.module == "system":

                if not action.topic:
                    action.topic = context.program()

            # ----------------------------
            # WEB
            # ----------------------------
            elif action.module == "web":

                if not action.topic:
                    action.topic = context.search()

            optimized.append(action)

        return optimized