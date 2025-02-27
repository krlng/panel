"""
Renders objects representing equations including LaTeX strings and
SymPy objects.
"""
from __future__ import annotations

import sys

from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, Mapping, Type,
)

import param  # type: ignore

from pyviz_comms import Comm, JupyterComm  # type: ignore

from ..util import lazy_load
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model


def is_sympy_expr(obj: Any) -> bool:
    """Test for sympy.Expr types without usually needing to import sympy"""
    if 'sympy' in sys.modules and 'sympy' in str(type(obj).__class__):
        import sympy  # type: ignore
        if isinstance(obj, sympy.Expr):
            return True
    return False


class LaTeX(ModelPane):
    """
    The `LaTeX` pane allows rendering LaTeX equations. It uses either
    `MathJax` or `KaTeX` depending on the defined renderer.

    By default it will use the renderer loaded in the extension
    (e.g. `pn.extension('katex')`), defaulting to `KaTeX`.

    Reference: https://panel.holoviz.org/reference/panes/LaTeX.html

    :Example:

    >>> pn.extension('katex')
    >>> LaTeX(
    ...     'The LaTeX pane supports two delimiters: $LaTeX$ and \(LaTeX\)',
    ...     style={'font-size': '18pt'}, width=800
    ... )
    """

    renderer = param.ObjectSelector(default=None, allow_None=True,
                                    objects=['katex', 'mathjax'], doc="""
        The JS renderer used to render the LaTeX expression.""")

    # Priority is dependent on the data type
    priority: ClassVar[float | bool | None] = None

    _rename: ClassVar[Mapping[str, str | None]] = {
        'renderer': None, 'object': 'text'
    }

    _updates: ClassVar[bool] = True

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if is_sympy_expr(obj) or hasattr(obj, '_repr_latex_'):
            return 0.05
        elif isinstance(obj, str):
            return None
        else:
            return False

    def _get_model_type(self, root: Model, comm: Comm | None) -> Type[Model]:
        module = self.renderer
        if module is None:
            if 'panel.models.mathjax' in sys.modules and 'panel.models.katex' not in sys.modules:
                module = 'mathjax'
            else:
                module = 'katex'
        model = 'KaTeX' if module == 'katex' else 'MathJax'
        return lazy_load(f'panel.models.{module}', model, isinstance(comm, JupyterComm), root)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._get_model_type(root, comm)(**self._get_properties(doc))
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _transform_object(self, obj: Any) -> Dict[str, Any]:
        if obj is None:
            obj = ''
        elif hasattr(obj, '_repr_latex_'):
            obj = obj._repr_latex_()
        elif is_sympy_expr(obj):
            import sympy
            obj = r'$'+sympy.latex(obj)+'$'
        return dict(object=obj)
