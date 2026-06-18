import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

URL = os.environ["API_URL"]
TOKEN = os.environ["API_TOKEN"]
COOKIES = "; ".join([
    f".Stackify.Rum={os.environ['COOKIE_STACKIFY']}",
    f"ASP.NET_SessionId={os.environ['COOKIE_SESSION']}",
    f"ASPSESSIONIDSWQAABCQ={os.environ['COOKIE_ASPNET']}",
])

PAYLOAD = {
    "id_emp_gcom": 109350, "id_mrc": 58, "dc_pro_nf": None, "cd_pro": None,
    "id_fab_pro": None, "cd_ref_pro": None, "cd_bar": None, "id_mat_pro": None,
    "dc_pro_red": None, "id_gru_fsc": None, "id_fam_pro1": 2, "dc_fam_pro1": None,
    "id_fam_pro2": 2, "dc_fam_pro2": None, "id_fam_pro3": None, "dc_fam_pro3": None,
    "id_fam_pro4": None, "dc_fam_pro4": None, "id_fam_pro5": None, "dc_fam_pro5": None,
    "id_fam_pro6": None, "dc_fam_pro6": None, "ic_tip_pro_sped": None, "dc_order_by": "",
    "ic_atv_ina": "A,I", "ic_pro_dsp_ecm": "", "ic_pro_dsp_app": "", "ic_not_cre_pro": None,
    "ic_pro_stq": "", "ic_eng_pro": "", "ic_pro_atu_so_franqueadora": None,
    "dt_cri_pro_ini": "", "dt_cri_pro_fim": "", "dt_alt_pro_ini": "", "dt_alt_pro_fim": "",
    "nm_pes_usu": None, "id_pto_vnd_de": None, "id_pto_vnd_ate": None,
    "id_pes_frn": None, "cd_pro_pulse": None,
}

FIELD_MAP = {
    "DC_PRO_NF":   "product_name",
    # Response uses ID_FAM_NIV2..NIV6 for levels 2-6; kept as-is (lowercased)
    "ID_FAM_PRO":  "id_fam_pro",
    "ID_FAM_NIV2": "id_fam_niv2",
    "ID_FAM_NIV3": "id_fam_niv3",
    "ID_FAM_NIV4": "id_fam_niv4",
    "ID_FAM_NIV5": "id_fam_niv5",
    "ID_FAM_NIV6": "id_fam_niv6",
    "DC_FAM_PRO":  "goal",
    "DC_FAM_PRO2": "group",
    "DC_FAM_PRO3": "dc_fam_pro3",
    "DC_FAM_PRO4": "category",
    "DC_FAM_PRO5": "dc_fam_pro5",
    "DC_FAM_PRO6": "dc_fam_pro6",
}

REQUEST_FAM_FIELDS = [
    "id_fam_pro1", "id_fam_pro2", "id_fam_pro3",
    "id_fam_pro4", "id_fam_pro5", "id_fam_pro6",
]


def fetch_products() -> list[dict]:
    body = json.dumps(PAYLOAD).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=body,
        headers={
            "Authorization": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": COOKIES,
            "User-Agent": "Mozilla/5.0 (compatible; GcomClient/1.0)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        raw = response.read().decode("utf-8")

    data = json.loads(raw)
    if isinstance(data, str):
        data = json.loads(data)

    return data if isinstance(data, list) else [data]


def filter_products(products: list[dict]) -> list[dict]:
    request_fam = {f: PAYLOAD.get(f) for f in REQUEST_FAM_FIELDS}
    return [
        {**{new_key: record.get(api_key) for api_key, new_key in FIELD_MAP.items()},
         **{"request": request_fam}}
        for record in products
    ]


def main():
    print("Fetching products...")
    products = fetch_products()
    print(f"Total records: {len(products)}")

    filtered = filter_products(products)

    print("\nFiltered output (sample — first 3):")
    print(json.dumps(filtered[:3], indent=2, ensure_ascii=False))

    os.makedirs("output", exist_ok=True)
    with open("output/products.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    print(f"\nAll {len(filtered)} records saved to output/products.json")


if __name__ == "__main__":
    main()
