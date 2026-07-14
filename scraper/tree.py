"""
Carga el árbol de categorías del usuario (hoja 'Árbol & Tags' + 'Tags por categoría')
y resuelve el path completo de una categoría del sitio -> handle / tags / type.

El sitio tiene hasta 4 niveles; el árbol del usuario tiene 3. Se camina el árbol
nivel por nivel (departamento › categoría › subcategoría) con matching tolerante
(exacto / prefijo / plural) y se devuelve el nodo más profundo alcanzado.
"""
import re
import html as htmllib
import unicodedata
import openpyxl

COLLECTIONS_XLSX = "/root/.claude/uploads/f4677800-7e33-5d4e-ab81-cb54e5e95596/22759230-chestershopifycolecciones_1.xlsx"
PRODUCTS_TEMPLATE = "/root/.claude/uploads/f4677800-7e33-5d4e-ab81-cb54e5e95596/bc350482-chesterproductosmatrixifytemplate_1.xlsx"


def norm(s):
    if not s:
        return ""
    s = htmllib.unescape(str(s))
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _name_eq(a, b):
    """Igualdad tolerante de nombres de categoría."""
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    # tolerar plural/singular y sufijos menores en el último token
    if a.rstrip("s") == b.rstrip("s"):
        return True
    if a.startswith(b) or b.startswith(a):
        return True
    return False


def load_tree():
    """Árbol anidado: {dept_name: {"node":.., "children": {cat_name: {"node":.., "children": {sub: {"node":..}}}}}}"""
    wb = openpyxl.load_workbook(COLLECTIONS_XLSX)
    ws = wb["Árbol & Tags"]
    wb2 = openpyxl.load_workbook(PRODUCTS_TEMPLATE)
    ws2 = wb2["Tags por categoría"]
    type_by_handle = {}
    for r in range(5, ws2.max_row + 1):
        handle = ws2.cell(r, 5).value
        typ = ws2.cell(r, 6).value
        if handle:
            type_by_handle[handle] = typ

    tree = {}
    for r in range(5, ws.max_row + 1):
        lvl, dep, cat, sub, handle, url, tags = [ws.cell(r, c).value for c in range(1, 8)]
        if not handle:
            continue
        node = {
            "handle": handle,
            "tags": tags,
            "type": type_by_handle.get(handle) or (sub or cat or dep),
            "level": lvl,
            "names": (dep, cat, sub),
        }
        dnode = tree.setdefault(dep, {"node": None, "children": {}})
        if not cat:
            dnode["node"] = node
            continue
        cnode = dnode["children"].setdefault(cat, {"node": None, "children": {}})
        if not sub:
            cnode["node"] = node
            continue
        cnode["children"][sub] = {"node": node, "children": {}}
    return tree


class TreeMatcher:
    def __init__(self):
        self.tree = load_tree()

    def _find_child(self, children, name):
        for key, val in children.items():
            if _name_eq(key, name):
                return val
        return None

    def match_path(self, path_topdown):
        """path_topdown: [departamento, categoria, subcat, subsubcat...] -> nodo más profundo."""
        parts = [p for p in path_topdown if p]
        if not parts:
            return None
        # departamento
        dnode = self._find_child(self.tree, parts[0])
        if not dnode:
            return None
        best = dnode["node"]
        cur = dnode
        for p in parts[1:]:
            nxt = self._find_child(cur["children"], p)
            if not nxt:
                break
            if nxt["node"]:
                best = nxt["node"]
            cur = nxt
        return best
