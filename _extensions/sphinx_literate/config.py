from dataclasses import dataclass

@dataclass
class Config:
    """
    Configuration of the sphinx_literate extension.
    All members of this class are available prefixed with "lit_" as options in
    the sphinx project's config.py.
    """

    # Begin and end a reference to another code block
    begin_ref: str = "{{"
    end_ref: str = "{{"

    @classmethod
    def from_app(cls, app):
        config = cls()
        for field in cls.__dataclass_fields__.values():
            value = getattr(app.config, "lit_" + field.name)
            setattr(config, field.name, value)

def setup(app):
    for field in Config.__dataclass_fields__.values():
        app.add_config_value("lit_" + field.name, field.default, 'html', [field.type])
