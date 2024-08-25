import schema


class ValidationError(ValueError):
    def __init__(self, message):
        super().__init__(message)

    def humanize_error(self) -> str:
        err_msg = f"{self.args[0]}"
        if self.__cause__ and type(self.__cause__) == schema.SchemaError:
            err_msg += ": " + self.__cause__.code
        return err_msg
