def apply_bootstrap_classes(form):
    """Apply Bootstrap `form-control` classes to all form fields.

    Use this in views when rendering third-party or Django auth forms so
    fields render consistently with the rest of the site.
    """
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        classes = existing.split() if existing else []
        if "form-control" not in classes:
            classes.append("form-control")
        field.widget.attrs["class"] = " ".join(classes)
    return form
