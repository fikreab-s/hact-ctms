"""
HACT CTMS — OpenClinica ODM metadata parser
============================================
Parses the CDISC ODM XML returned by OpenClinica's ``getMetadata`` SOAP
operation into a plain-Python structure that the importer can turn into
CTMS ``Visit`` / ``Form`` / ``Item`` / ``VisitForm`` rows.

Design goals:
- **Namespace-agnostic**: OpenClinica mixes the CDISC ODM namespace with its
  own ``OpenClinica:`` extension namespace and version numbers drift between
  releases, so we match on *local* element/attribute names only.
- **Defensive**: missing elements degrade gracefully rather than raising.
- **Pure**: no Django imports here so it is trivially unit-testable.

The output shape:
{
  "study": {"oid": "S_HACTPSBI", "name": "..."},
  "events": [
     {"oid": "SE_SCREENING", "name": "Screening", "order": 1,
      "type": "scheduled", "form_oids": ["F_..."]},
  ],
  "forms": [
     {"oid": "F_...", "name": "A1 Screening", "version": "1.0",
      "item_groups": ["IG_..."]},
  ],
  "items": [   # already flattened + ordered per form
     {"form_oid": "F_...", "group_oid": "IG_...", "oid": "I_...",
      "name": "WEIGHT", "label": "Weight (kg)", "field_type": "number",
      "required": True, "order": 4, "validation_rule": "range(0.5, 10.0)",
      "options": [{"value": "1", "label": "Male"}]},
  ],
}
"""

from xml.etree import ElementTree as ET


def _ln(tag):
    """Local name of an element tag, stripping any '{namespace}' prefix."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _attr(el, name, default=""):
    """Namespace-agnostic attribute lookup (matches on local name)."""
    # Fast path: exact (no-namespace) attribute.
    if name in el.attrib:
        return el.attrib[name]
    for k, v in el.attrib.items():
        if _ln(k) == name:
            return v
    return default


def _find_all(el, localname):
    """All descendants whose local tag name == localname."""
    return [c for c in el.iter() if _ln(c.tag) == localname]


def _children(el, localname):
    """Direct children whose local tag name == localname."""
    return [c for c in list(el) if _ln(c.tag) == localname]


def _text(el):
    return (el.text or "").strip() if el is not None else ""


# ── OpenClinica DataType / ResponseType → CTMS field_type ────────────────────

def _map_field_type(data_type, response_type, has_options, n_options):
    """Decide the CTMS field_type from OC's DataType + ResponseType.

    ResponseType (OpenClinica extension) is the most reliable signal for the
    widget; DataType is the fallback for plain fields.
    """
    rt = (response_type or "").strip().lower()
    dt = (data_type or "").strip().lower()

    # Widget explicitly declared by OpenClinica.
    if rt:
        if rt in ("radio",):
            return "radio"
        if rt in ("checkbox", "multi-select", "multi_select"):
            return "checkbox"
        if rt in ("single-select", "single_select", "select", "dropdown"):
            return "dropdown"
        if rt in ("textarea",):
            return "textarea"
        if rt in ("file", "image"):
            return "file"
        if rt in ("calculation", "group-calculation"):
            return "text"
        # "text" falls through to DataType handling below

    # Coded item without an explicit widget → pick radio for a few options,
    # dropdown for many.
    if has_options:
        return "radio" if n_options <= 5 else "dropdown"

    if dt in ("integer", "int", "float", "real", "double"):
        return "number"
    if dt in ("date", "partialdate"):
        return "date"
    if dt in ("datetime",):
        return "datetime"
    return "text"


def _parse_range_checks(item_def):
    """Turn OC <RangeCheck> elements into a 'range(min, max)' rule if possible."""
    lo = hi = None
    for rc in _children(item_def, "RangeCheck"):
        comparator = _attr(rc, "Comparator", "").upper()
        val = ""
        for cv in _children(rc, "CheckValue"):
            val = _text(cv)
            break
        if not val:
            continue
        try:
            num = float(val)
        except ValueError:
            continue
        if comparator in ("GE", "GT"):
            lo = num
        elif comparator in ("LE", "LT"):
            hi = num
    if lo is not None and hi is not None:
        return f"range({_fmt(lo)}, {_fmt(hi)})"
    return ""


def _fmt(num):
    """Render a float without a trailing .0 when it is integral."""
    return str(int(num)) if float(num).is_integer() else str(num)


def _response_type_for(item_def, form_oid):
    """Extract OpenClinica ResponseType for this item (optionally per-form).

    OC nests it under an OpenClinica extension, roughly:
      <OpenClinica:ItemDetails>
        <OpenClinica:ItemPresentInForm FormOID="F_...">
          <OpenClinica:ResponseType>radio</OpenClinica:ResponseType>  (or attr)
    We match on local names and, when a FormOID is given, prefer the entry
    for that form.
    """
    best = ""
    for pif in _find_all(item_def, "ItemPresentInForm"):
        this_form = _attr(pif, "FormOID", "")
        rt = ""
        # ResponseType may be a child element or an attribute.
        for rte in _find_all(pif, "ResponseType"):
            rt = _text(rte) or _attr(rte, "Name", "") or _attr(rte, "ResponseTypeName", "")
            if rt:
                break
        if not rt:
            rt = _attr(pif, "ResponseType", "")
        if rt:
            if form_oid and this_form == form_oid:
                return rt
            best = best or rt
    # Some OC versions put ResponseType directly under ItemDetails.
    if not best:
        for rte in _find_all(item_def, "ResponseType"):
            best = _text(rte) or _attr(rte, "Name", "")
            if best:
                break
    return best


def parse_odm_metadata(odm_xml):
    """Parse an OpenClinica getMetadata ODM string into the structure above.

    Returns None if the XML cannot be parsed or has no MetaDataVersion.
    """
    if not odm_xml:
        return None
    try:
        root = ET.fromstring(odm_xml)
    except ET.ParseError:
        return None

    # Study OID + name
    study_oid = ""
    study_name = ""
    study_el = next((e for e in root.iter() if _ln(e.tag) == "Study"), None)
    if study_el is not None:
        study_oid = _attr(study_el, "OID", "")
        for gv in _find_all(study_el, "StudyName"):
            study_name = _text(gv)
            break

    mdv = next((e for e in root.iter() if _ln(e.tag) == "MetaDataVersion"), None)
    if mdv is None:
        return None

    # ── Build lookup tables ──────────────────────────────────────────────
    # CodeLists: oid -> [{value, label}]
    code_lists = {}
    for cl in _find_all(mdv, "CodeList"):
        oid = _attr(cl, "OID")
        opts = []
        for cli in _find_all(cl, "CodeListItem"):
            coded = _attr(cli, "CodedValue")
            label = coded
            for dec in _find_all(cli, "TranslatedText"):
                label = _text(dec) or coded
                break
            opts.append({"value": coded, "label": label})
        if oid:
            code_lists[oid] = opts

    # ItemDefs by OID
    item_defs = {}
    for idef in _find_all(mdv, "ItemDef"):
        oid = _attr(idef, "OID")
        if oid:
            item_defs[oid] = idef

    # ItemGroupDefs: oid -> ordered list of (item_oid, mandatory, order)
    group_items = {}
    for gdef in _find_all(mdv, "ItemGroupDef"):
        goid = _attr(gdef, "OID")
        refs = []
        for iref in _children(gdef, "ItemRef"):
            refs.append({
                "item_oid": _attr(iref, "ItemOID"),
                "mandatory": _attr(iref, "Mandatory", "No").lower() in ("yes", "true", "1"),
                "order": _to_int(_attr(iref, "OrderNumber", "0")),
            })
        if goid:
            group_items[goid] = refs

    # FormDefs: oid -> {name, version, group_oids}
    forms = []
    form_group_map = {}
    for fdef in _find_all(mdv, "FormDef"):
        foid = _attr(fdef, "OID")
        name = _attr(fdef, "Name") or foid
        groups = [_attr(g, "ItemGroupOID") for g in _children(fdef, "ItemGroupRef")]
        form_group_map[foid] = groups
        forms.append({
            "oid": foid,
            "name": name,
            "version": _derive_version(foid),
            "item_groups": groups,
        })

    # StudyEventDefs (visits): oid -> {name, order, type, form_oids}
    events = []
    # Protocol declares ordering via StudyEventRef
    order_by_oid = {}
    protocol = next((e for e in _find_all(mdv, "Protocol")), None)
    if protocol is not None:
        for i, ser in enumerate(_children(protocol, "StudyEventRef"), start=1):
            oid = _attr(ser, "StudyEventOID")
            order_by_oid[oid] = _to_int(_attr(ser, "OrderNumber", str(i)), i)

    for i, edef in enumerate(_find_all(mdv, "StudyEventDef"), start=1):
        eoid = _attr(edef, "OID")
        events.append({
            "oid": eoid,
            "name": _attr(edef, "Name") or eoid,
            "order": order_by_oid.get(eoid, i),
            "type": _attr(edef, "Type", "").lower(),
            "repeating": _attr(edef, "Repeating", "No").lower() in ("yes", "true", "1"),
            "form_oids": [_attr(fr, "FormOID") for fr in _children(edef, "FormRef")],
        })
    events.sort(key=lambda e: e["order"])

    # ── Flatten items per form (in group + item order) ───────────────────
    items = []
    for form in forms:
        foid = form["oid"]
        seen_names = set()
        for goid in form["item_groups"]:
            for ref in sorted(group_items.get(goid, []), key=lambda r: r["order"]):
                idef = item_defs.get(ref["item_oid"])
                if idef is None:
                    continue
                name = _attr(idef, "Name") or _strip_prefix(ref["item_oid"])
                # keep field_name unique within a form
                field_name = name
                suffix = 2
                while field_name in seen_names:
                    field_name = f"{name}_{suffix}"
                    suffix += 1
                seen_names.add(field_name)

                data_type = _attr(idef, "DataType")
                label = ""
                q = next((q for q in _find_all(idef, "Question")), None)
                if q is not None:
                    for tt in _find_all(q, "TranslatedText"):
                        label = _text(tt)
                        break
                if not label:
                    label = _attr(idef, "Comment") or name

                code_ref = next((c for c in _find_all(idef, "CodeListRef")), None)
                options = None
                if code_ref is not None:
                    cl_oid = _attr(code_ref, "CodeListOID")
                    options = code_lists.get(cl_oid) or None

                response_type = _response_type_for(idef, foid)
                field_type = _map_field_type(
                    data_type, response_type,
                    has_options=bool(options),
                    n_options=len(options or []),
                )

                items.append({
                    "form_oid": foid,
                    "group_oid": goid,
                    "oid": ref["item_oid"],
                    "name": field_name,
                    "label": label,
                    "field_type": field_type,
                    "required": ref["mandatory"],
                    "order": ref["order"],
                    "validation_rule": _parse_range_checks(idef),
                    "options": options,
                })

    return {
        "study": {"oid": study_oid, "name": study_name},
        "events": events,
        "forms": forms,
        "items": items,
    }


def _to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _strip_prefix(oid):
    """'I_SCREE_WEIGHT' -> 'WEIGHT' (best-effort readable field_name)."""
    parts = (oid or "").split("_")
    return parts[-1] if parts else oid


def _derive_version(form_oid):
    """OC form OIDs often end with a version token, e.g. 'F_SCREEN_V10' -> '1.0'."""
    tokens = (form_oid or "").split("_")
    for tok in reversed(tokens):
        if tok and tok[0] in ("v", "V") and tok[1:].isdigit():
            digits = tok[1:]
            if len(digits) >= 2:
                return f"{digits[:-1]}.{digits[-1]}"
            return digits
    return "1.0"
