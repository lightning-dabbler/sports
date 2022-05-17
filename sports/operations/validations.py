import click


def command_requirement_options(*options, override_option="complete"):
    class CommandRequirement(click.Command):
        def invoke(self, ctx):
            x = [True if ctx.params[option] else False for option in options]
            if not any(x) and not ctx.params[override_option]:
                str_options = "', '".join(options)
                message = f"At least one of the following parameters must be provided: '{str_options}' !"
                raise click.ClickException(message)
            super().invoke(ctx)

    return CommandRequirement


class Validations:
    def __init__(self, **known_arguments):
        self.known_arguments = known_arguments

    def _unknown_arguments(self, arguments, category):
        known_arguments = self.known_arguments.get(category, [])
        return {"unknown_arguments": set(arguments) - set(known_arguments), "known_arguments": known_arguments}

    def options_callback(self, ctx, param, value):
        value_for_eval = value or []
        evaluated_args = self._unknown_arguments(value_for_eval, param.name)
        unknown_arguments = evaluated_args["unknown_arguments"]
        if unknown_arguments:
            known_arguments = evaluated_args["known_arguments"]
            str_options = "', '".join(unknown_arguments)
            known_options = "\n".join(known_arguments)
            message = f"Unknown Arguments for '{param.name}': '{str_options}' !\nAccepted Arguments:\n{known_options}"
            raise click.ClickException(message)
        return value
