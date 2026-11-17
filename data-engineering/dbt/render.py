"""Render dbt-style Jinja without dbt or a database.

Plain Jinja2 plus small stand-ins for the dbt functions that macros use most
(return, var, ref, source, exceptions.raise_compiler_error, execute, log), so
you can see what a macro or model produces. Chapter 9 of README.md explains
when this is handy; the real `dbt compile` is always the final word.

    from render import Renderer
    r = Renderer("toy_rides/macros", vars={"experiment_rules": [...]})
    print(r.call("experiment_group_case", "driver_id"))
    print(r.render_file("toy_rides/models/marts/driver_day.sql"))
"""
import re
from pathlib import Path

import jinja2

_MACRO_DEF = re.compile(r"(\{%-?\s*macro\s+)(\w+)")


class _Return(Exception):
    """dbt's return(): stop the macro and hand `value` to the caller."""

    def __init__(self, value):
        super().__init__(value)
        self.value = value


class CompilerError(Exception):
    """What exceptions.raise_compiler_error raises in dbt (it aborts the run)."""


def _raise_compiler_error(message):
    raise CompilerError(message)


def _return(value):
    raise _Return(value)


def environment():
    """The Jinja environment dbt uses for SQL: the `do` statement on, no auto-escaping."""
    return jinja2.Environment(extensions=["jinja2.ext.do"], undefined=jinja2.StrictUndefined)


def render(template, **context):
    """Render one plain-Jinja string (no dbt functions)."""
    return environment().from_string(template).render(**context)


class Renderer:
    """Load every macro under `macro_dir` and render templates that call them.

    dbt makes every macro of a project callable from everywhere, including from
    another macro in the same file, and lets a macro hand back a Python value with
    return(). Plain Jinja does neither, so each `{% macro name(` is renamed to
    `m__name` and `name` becomes a wrapper that calls it and catches return().
    """

    def __init__(self, macro_dir, vars=None, is_incremental=False):
        self._vars = dict(vars or {})
        self._modules = []
        self.context = {
            "return": _return,
            "var": self._var,
            "ref": lambda name: name,
            "source": lambda source, table: f"{source}.{table}",
            "this": "this",
            "is_incremental": lambda: is_incremental,
            "execute": True,
            "log": lambda msg, info=False: "",
            "exceptions": type("Exceptions", (), {"raise_compiler_error": staticmethod(_raise_compiler_error)}),
        }
        env = environment()
        for path in sorted(Path(macro_dir).rglob("*.sql")):
            source = path.read_text()
            for name in _MACRO_DEF.findall(source):
                self.context[name[1]] = self._wrapper(name[1])
            template = env.from_string(_MACRO_DEF.sub(r"\1m__\2", source))
            self._modules.append(template.make_module(self.context))

    def _var(self, name, default=None):
        if name in self._vars:
            return self._vars[name]
        if default is None:
            raise CompilerError(f"Required var '{name}' not found")
        return default

    def _wrapper(self, name):
        def call(*args, **kwargs):
            for module in self._modules:
                macro = getattr(module, "m__" + name, None)
                if macro is not None:
                    try:
                        return macro(*args, **kwargs)
                    except _Return as r:
                        return r.value
            raise CompilerError(f"macro {name} not found")
        return call

    def call(self, name, *args, **kwargs):
        """Call one macro: its return() value, or else its rendered text."""
        return self.context[name](*args, **kwargs)

    def render_file(self, path):
        """Render a model file (config() calls render as empty text)."""
        context = {**self.context, "config": lambda **kwargs: ""}
        return environment().from_string(Path(path).read_text()).render(**context)
