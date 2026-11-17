"""Baut die vis-network-Bibliothek direkt in graphify-out/graph.html ein, damit die Karte auch ohne Internet
bzw. in Vorschauen ohne fremde Skripte funktioniert (17.11.2026: „vis is not defined“).
  python graph_inline.py <pfad zu vis-network.min.js>
"""
import re, sys
p = "graphify-out/graph.html"
html = open(p, encoding="utf-8").read()
js = open(sys.argv[1], encoding="utf-8").read().replace("</script", "<\\/script")
neu, n = re.subn(r'<script[^>]*src="https://unpkg\.com/vis-network[^"]*"[^>]*>\s*</script>', lambda m: "<script>" + js + "</script>", html)
if n:
    open(p, "w", encoding="utf-8").write(neu)
print("eingebaut" if n else "nichts zu tun")
