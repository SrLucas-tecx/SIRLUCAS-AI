class ContextResolver:

    def __init__(self):
        pass

    def resolve(self, data, context):

        if not isinstance(data, dict):
            return data

        topic = data.get("topic")

        if topic in [
            "lo",
            "la",
            "eso",
            "este",
            "esta",
            "él",
            "ella"
        ]:

            previous = context.topic()

            if previous:
                data["topic"] = previous

        return data
    