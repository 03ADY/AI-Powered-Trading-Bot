def brief_html(md: str, title: str = "TradePulse Brief") -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:system-ui;max-width:800px;margin:2rem auto;line-height:1.5;}}</style>
</head><body>{md.replace(chr(10), '<br>')}</body></html>"""


def dashboard_html(brief_md: str, kpis: dict) -> str:
    cards = "".join(
        f'<div style="display:inline-block;margin:8px;padding:12px 20px;background:#f1f5f9;border-radius:8px;">'
        f'<b>{k}</b><br>{v}</div>'
        for k, v in kpis.items()
    )
    body = brief_md.replace("\n", "<br>")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>TradePulse Dashboard</title>
<style>body{{font-family:system-ui;margin:2rem;}} .kpi{{margin:1rem 0;}}</style></head>
<body><h1>TradePulse Enterprise — Dashboard Export</h1>
<div class="kpi">{cards}</div><hr>{body}</body></html>"""
