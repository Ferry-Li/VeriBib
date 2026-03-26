"""BibTeX file parser."""


def parse_bib_file(filename):
    """Parse a BibTeX file and return list of entries."""
    entries = []
    current = {}
    inside = False
    entry_type = ""
    key = ""

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("@"):
                if current:
                    entries.append({"type": entry_type, "key": key, **current})
                current = {}
                inside = True
                head = line.split("{")[0]
                entry_type = head.replace("@", "").strip()
                key = line.split("{")[1].strip().strip(",")
            elif inside and line.startswith("}"):
                entries.append({"type": entry_type, "key": key, **current})
                current = {}
                inside = False
            elif inside:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    k = parts[0].strip().lower()
                    v = parts[1].strip().strip("{,}")
                    current[k] = v
    return entries
