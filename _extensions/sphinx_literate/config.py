
def setup(app):
    # Begin and end a reference to another code block
    app.add_config_value("lit_begin_ref", "{{", 'html', [str])
    app.add_config_value("lit_end_ref", "}}", 'html', [str])
