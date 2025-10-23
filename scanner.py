import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse

def scan_forms(url, timeout=10, headers=None):
    headers = headers or {"User-Agent": "form-scanner/1.0 (+Ghostting@bugcrowdninja.com)"}
    try:
        r = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
    except requests.exceptions.RequestException as e:
        return {"Error": "request_failed", "details": str(e)}
    
    content_type = r.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        return {"Error": "not_html", "status_code": r.status_code, "content_type": content_type}
    
    soup = BeautifulSoup(r.text, "html.parser")
    forms = []

    for idx, f in enumerate(soup.find_all("form")):
        action = f.get("action")
        method = f.get("method")
        form_info = {
            "index": idx,
            "action_raw": action,
            "action_abs": urljoin(url, action) if action else url,
            "method": method,
            "id": f.get("id"),
            "name": f.get("name"),
            "class": f.get("class"),
            "inputs": []
        }
        # extrai os campos (input, texteare e select)
        for i in f.find_all(["input", "textarea", "select"]):
            tag = i.name
            field = {
                "tag": tag,
                "name": i.get("name"),
                "type": i.get("type") if tag == "input" else tag,
                "value": i.get("value"),
                "required": i.has_attr("required"),
                "maxlength": i.get("maxlength"),
                "pattern": i.get("pattern")
            }
        # se for <select> pega as opções
        if tag == "select":
            options = []
            for opt in i.find_all("option"):
                options.append({
                    "value": opt.get("value"),
                    "text": opt.text.strip(),
                    "selected": opt.has_attr("selected")
                })
            field["options"] = options
            field["multiple"] = i.has_attr("multiple")
        
        form_info["inputs"].append(field)

        forms.append(form_info)

    result = {
        "url": url,
        "final_url": r.url,
        "status_code": r.status_code,
        "forms_count": len(forms),
        "forms": forms
    }

    return json.dumps(result, indent=2, ensure_ascii=False)

# ---------------------------
# CLI - terminal entry point
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scanner de forms HTML..."
    )
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="URL alvo (ex: https://exemplo.com)"
    )

    args = parser.parse_args()

    print(f"\n[+] Escaneando formulários em: {args.url}\n")
    resultado = scan_forms(args.url)
    print(resultado)