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
    f"{os.environ['COOKIE_ASPNET_NAME']}={os.environ['COOKIE_ASPNET']}",
])

PAYLOAD = {
    "id_emp_gcom": 109350, "id_mrc": 58, "dc_pro_nf": None, "cd_pro": None,
    "id_fab_pro": None, "cd_ref_pro": None, "cd_bar": None, "id_mat_pro": None,
    "dc_pro_red": None, "id_gru_fsc": None, "id_fam_pro1": None, "dc_fam_pro1": None,
    "id_fam_pro2": None, "dc_fam_pro2": None, "id_fam_pro3": None, "dc_fam_pro3": None,
    "id_fam_pro4": None, "dc_fam_pro4": None, "id_fam_pro5": None, "dc_fam_pro5": None,
    "id_fam_pro6": None, "dc_fam_pro6": None, "ic_tip_pro_sped": None, "dc_order_by": "",
    "ic_atv_ina": "A,I", "ic_pro_dsp_ecm": "", "ic_pro_dsp_app": "", "ic_not_cre_pro": None,
    "ic_pro_stq": "", "ic_eng_pro": "", "ic_pro_atu_so_franqueadora": None,
    "dt_cri_pro_ini": "", "dt_cri_pro_fim": "", "dt_alt_pro_ini": "", "dt_alt_pro_fim": "",
    "nm_pes_usu": None, "id_pto_vnd_de": None, "id_pto_vnd_ate": None,
    "id_pes_frn": None, "cd_pro_pulse": None,
}

FINALIDADE_LOOKUP = {
    1: "VENDAS",
    2: "INSUMOS",
    3: "USO E CONSUMO",
    4: "IMOBILIZADOS",
    5: "OPERACIONAL",
    6: "MANUTENCOES E SERVICOS",
    7: "MATERIAL PARA OBRA",
}

GRUPO_LOOKUP = {
    1:  "ACOMPANHAMENTO",
    2:  "ALIMENTACAO",
    3:  "BEBIDAS",
    4:  "BEX CAFE",
    5:  "BRINDE",
    6:  "CAFE",
    7:  "CARNES",
    8:  "EMBALAGEM",
    9:  "EMPORIO",
    10: "FRIOS",
    11: "HORTIFRUTTI",
    12: "MARKETING",
    13: "MATERIAL DE FESTA",
    14: "MOLHOS",
    15: "PAES",
    16: "PAPELARIA",
    17: "PRATO",
    18: "SALGADOS E SANDUICHES",
    19: "SANDUICHES",
    20: "SECOS",
    21: "SOBREMESAS",
    22: "UNIFORMES",
    23: "USO E CONSUMO",
    25: "PECAS E EQUIPAMENTOS",
    26: "UTENSILIOS",
    27: "MATERIAL PARA OBRA",
    28: "MATERIAL DE ESCRITORIO",
    29: "MATERIAL DE LIMPEZA",
    30: "MATERIAL ELETRICO",
    31: "SERVICOS",
    32: "INVESTIMENTO",
}

SUBGROUP_LOOKUP = {
    1:  "ACHOCOLATADO",
    2:  "ADICIONAL",
    3:  "AGUA",
    4:  "AGUA SABORIZADA",
    5:  "ALCOOLICA",
    6:  "ALIMENTACAO",
    7:  "ANEIS DE CEBOLA",
    8:  "BASICOS",
    9:  "BATATA CANOA",
    10: "BATATA PALITO",
    11: "BEBIDAS",
    12: "BEX CAFE",
    13: "BISCOITO",
    14: "BOBS KIDS",
    15: "BOBS PLAY",
    16: "CAFE",
    17: "CAPPUCCINO",
    18: "CARNES",
    19: "CERVEJA E CHOPP",
    20: "CHA",
    21: "CHOCOLATE E MOKA",
    22: "CLASSICOS",
    23: "COMPOSICAO",
    24: "DOCE",
    25: "EMBALAGEM",
    26: "ENERGETICO",
    27: "FRANLITOS",
    28: "FRIOS",
    29: "GELADO E MILK SHAKE",
    30: "HORTIFRUTTI",
    31: "ISOTONICO",
    32: "MARKETING",
    33: "MATERIAL DE FESTA",
    34: "MOLHOS",
    35: "NATAL",
    36: "OMELETE",
    37: "PAES",
    38: "PAPELARIA",
    39: "PREMIUM",
    40: "REFRIGERANTE",
    41: "RESPONSA",
    42: "SALADA",
    43: "SALGADO",
    44: "SANDUICHES",
    45: "SECOS",
    46: "SOBREMESAS",
    47: "SUCO",
    48: "UNIFORMES",
    49: "INSUMOS",
    50: "TOSTES",
    51: "BACONZUDOS",
    52: "BATATA MINIONS",
    57: "MAQUINARIO",
    58: "ADMINISTRACAO E RETAGUARDA",
    59: "FRANQUIA BOBS",
    60: "INVESTIMENTO",
    61: "FRANGO EM TIRAS",
    62: "BLISTER",
    63: "COLABORADOR",
    68: "BATATA SABOR BIG BOB",
    69: "REFRESH",
}

CATEGORIA_LOOKUP = {
    1:  "ALCOOLICA",
    2:  "BIG CASCAO",
    3:  "BOBS MAX",
    4:  "BOVINO",
    5:  "CASQUINHA",
    6:  "COPO",
    7:  "DOCE",
    8:  "FRANGO",
    9:  "HAMBURGUERES",
    10: "LATA",
    11: "LONG NECK",
    12: "MILK SHAKE",
    13: "MOLHOS",
    14: "PEIXE",
    15: "PET",
    16: "REFRIGERANTE",
    17: "SUINO",
    18: "SUNDAE",
    19: "SUCO",
    20: "TOP",
    21: "TORRE",
    22: "VEGETARIANO",
    23: "ADICIONAIS",
    24: "BATATAS",
    25: "FRANLITOS",
    26: "AGUAS",
    27: "REFRESH",
}

TIPO_LOOKUP = {
    1: "CLASSICOS",
    2: "COLHER",
    3: "PREMIUM",
    4: "RECHEADA",
    5: "ESPECIAIS",
}


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
    result = []
    for record in products:
        entry = {
            "product_code": record.get("CD_PRO"),
            "product_name": record.get("DC_PRO_NF"),
            "goal":     FINALIDADE_LOOKUP.get(record.get("ID_FAM_PRO")),
            "group":    GRUPO_LOOKUP.get(record.get("ID_FAM_NIV2")),
            "subgroup": SUBGROUP_LOOKUP.get(record.get("ID_FAM_NIV3")),
            "category": CATEGORIA_LOOKUP.get(record.get("ID_FAM_NIV4")),
            "type":     TIPO_LOOKUP.get(record.get("ID_FAM_NIV5")),
        }
        result.append(entry)
    return result


def detail_products(products: list[dict]) -> list[dict]:
    result = []
    for record in products:
        entry = {
            "product_code": record.get("CD_PRO"),
            "product_name": record.get("DC_PRO_NF"),
            "goal":     FINALIDADE_LOOKUP.get(record.get("ID_FAM_PRO")),
            "group":    GRUPO_LOOKUP.get(record.get("ID_FAM_NIV2")),
            "subgroup": SUBGROUP_LOOKUP.get(record.get("ID_FAM_NIV3")),
            "category": CATEGORIA_LOOKUP.get(record.get("ID_FAM_NIV4")),
            "type":     TIPO_LOOKUP.get(record.get("ID_FAM_NIV5")),
            "ids": {
                "id_fam_pro":  record.get("ID_FAM_PRO"),
                "id_fam_niv2": record.get("ID_FAM_NIV2"),
                "id_fam_niv3": record.get("ID_FAM_NIV3"),
                "id_fam_niv4": record.get("ID_FAM_NIV4"),
                "id_fam_niv5": record.get("ID_FAM_NIV5"),
                "id_fam_niv6": record.get("ID_FAM_NIV6"),
            },
            "dc_fam_pro": {
                "dc_fam_pro":  record.get("DC_FAM_PRO"),
                "dc_fam_pro2": record.get("DC_FAM_PRO2"),
                "dc_fam_pro3": record.get("DC_FAM_PRO3"),
                "dc_fam_pro4": record.get("DC_FAM_PRO4"),
                "dc_fam_pro5": record.get("DC_FAM_PRO5"),
                "dc_fam_pro6": record.get("DC_FAM_PRO6"),
            },
        }
        result.append(entry)
    return result


def main():
    print("Fetching products...")
    products = fetch_products()
    print(f"Total records: {len(products)}")

    filtered = filter_products(products)
    detailed = detail_products(products)

    print("\nFiltered output (sample — first 3):")
    print(json.dumps(filtered[:3], indent=2, ensure_ascii=False))

    os.makedirs("output", exist_ok=True)
    with open("output/products.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    print(f"\nAll {len(filtered)} records saved to output/products.json")

    with open("output/detailed_products.json", "w", encoding="utf-8") as f:
        json.dump(detailed, f, indent=2, ensure_ascii=False)
    print(f"All {len(detailed)} records saved to output/detailed_products.json")


if __name__ == "__main__":
    main()
