"""
Scrapes id_fam_proN → label lookup tables for family levels
FINALIDADE, GRUPO, CATEGORIA, and TIPO by intercepting the POST
to SelecionarProduto after selecting each dropdown option.

Run (local, headed — Akamai bot detection):
    HEADLESS=false python scrape_families.py              # all 4 levels
    HEADLESS=false python scrape_families.py --level finalidade
    HEADLESS=false python scrape_families.py --level grupo
    HEADLESS=false python scrape_families.py --level categoria
    HEADLESS=false python scrape_families.py --level tipo

Useful env knobs:
    LIST_ONLY=true    open each dropdown, print all options, then exit
    HEADLESS=false    show the browser window (default: false = headed)
"""

import argparse
import asyncio
import json
import os
import random
import re
import sys
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

WIZARD_URL = "https://www2.gcom.com.br/novoerp/#/novoerp/produto/wizard-cadastro-produto"
API_PATH   = "/GcomProdutoService/Produto/SelecionarProduto"
MODAL      = "#modal-app-cadastro-produto-consulta"
PANEL      = ".ng-dropdown-panel"
OPTION     = ".ng-option"

LEVELS = {
    "finalidade": {"label": "FINALIDADE", "field": "id_fam_pro1"},
    "grupo":      {"label": "GRUPO",      "field": "id_fam_pro2"},
    "categoria":  {"label": "CATEGORIA",  "field": "id_fam_pro4"},
    "tipo":       {"label": "TIPO",       "field": "id_fam_pro5"},
}

LIST_ONLY = os.environ.get("LIST_ONLY", "false").lower() == "true"


def _ng_selector(label: str) -> str:
    return (
        f"{MODAL} "
        f'app-familia-produto-select:has(label:text-is("{label}")) '
        f"ng-select.app-familia-produto-select"
    )


def _progress_path(level: str) -> str:
    return f"output/family_progress_{level}.json"


def _output_path(level: str) -> str:
    return f"output/family_lookup_{level}.json"


def _build_local_storage_script() -> str:
    items = {
        "jwtToken":            os.environ.get("LS_JWT_TOKEN", ""),
        "timerNotificacao":    "N",
        "activeModuleSearch":  "PRODUTOS",
        "activeModule":        "PRODUTOS",
        "activeSubmodule":     "CADASTROS",
    }
    ls_user = os.environ.get("LS_USER", "")
    if ls_user:
        items["user"] = ls_user
    return "\n".join(
        f"localStorage.setItem({json.dumps(k)}, {json.dumps(v)});"
        for k, v in items.items() if v
    )


def _build_cookies() -> list[dict]:
    cookies = []
    for name, env_key in [
        (".Stackify.Rum",   "COOKIE_STACKIFY"),
        ("ASP.NET_SessionId", "COOKIE_SESSION"),
    ]:
        val = os.environ.get(env_key)
        if val:
            cookies.append({"name": name, "value": val,
                            "domain": "www2.gcom.com.br", "path": "/"})
    aspnet_name = os.environ.get("COOKIE_ASPNET_NAME", "ASPSESSIONIDCEDTABAR")
    aspnet_val  = os.environ.get("COOKIE_ASPNET")
    if aspnet_val:
        cookies.append({"name": aspnet_name, "value": aspnet_val,
                        "domain": "www2.gcom.com.br", "path": "/"})
    return cookies


async def _open_dropdown(page, ng):
    await ng.click()
    panel = page.locator(PANEL)
    await panel.wait_for(state="visible", timeout=8_000)
    return panel


async def _list_options(page, ng) -> list[str]:
    panel = await _open_dropdown(page, ng)
    opts  = panel.locator(OPTION)
    await opts.first.wait_for(timeout=8_000)

    labels, seen = [], set()
    for i in range(await opts.count()):
        t = (await opts.nth(i).text_content() or "").strip()
        if t and t.lower() not in ("selecione", "") and t not in seen:
            seen.add(t)
            labels.append(t)

    await page.keyboard.press("Escape")
    await page.wait_for_timeout(200)
    return labels


async def _select_option(page, ng, label: str) -> bool:
    panel = await _open_dropdown(page, ng)
    inp   = ng.locator("input[type='text']")
    if await inp.count() > 0:
        await inp.fill("")
        await inp.type(label, delay=15)
        await page.wait_for_timeout(400)

    exact = re.compile(r"^\s*" + re.escape(label) + r"\s*$")
    option = panel.locator(OPTION).filter(has_text=exact).first
    if await option.count() == 0:
        await page.keyboard.press("Escape")
        return False

    await option.click()
    await page.wait_for_timeout(200)
    return True


async def _wait_for_wizard(page) -> bool:
    """Navigate to the wizard URL and wait until the modal is ready. Returns False on failure."""
    await page.goto(WIZARD_URL)
    try:
        await page.wait_for_url("**wizard-cadastro-produto**", timeout=60_000)
        os.makedirs("output", exist_ok=True)
        await page.screenshot(path="output/debug_landing.png", full_page=True)

        overlay = page.locator(".swal2-container")
        if await overlay.count() > 0:
            print("Loading overlay detected, waiting for it to clear...")
            await overlay.wait_for(state="hidden", timeout=30_000)

        await page.screenshot(path="output/debug_ready.png", full_page=True)
        await page.evaluate("document.querySelector('.modal-body')?.scrollTo(0, 99999)")
        await page.wait_for_timeout(500)
        return True
    except Exception as e:
        print(f"ERROR waiting for wizard: {e}", file=sys.stderr)
        await page.screenshot(path="output/debug_timeout.png", full_page=True)
        return False


async def _scrape_level(page, level: str, cfg: dict) -> dict[str, int | None]:
    """Scrape one family level. Returns {label: id} mapping."""
    label_text = cfg["label"]
    field      = cfg["field"]
    ng         = page.locator(_ng_selector(label_text))
    pesquisar  = page.locator(f"{MODAL} button.btn-success").first
    toolbar    = page.locator("#buscaToolbar")
    modal      = page.locator(MODAL)

    print(f"\n{'='*60}")
    print(f"  Level: {level.upper()}  (label={label_text!r}, field={field!r})")
    print(f"{'='*60}")

    # Wait for this dropdown to be in the DOM
    try:
        await ng.wait_for(state="attached", timeout=20_000)
    except Exception:
        print(f"  ! {label_text} dropdown not found — skipping level", file=sys.stderr)
        return {}

    labels = await _list_options(page, ng)
    print(f"  {len(labels)} option(s) in dropdown:")
    for lbl in labels:
        print(f"    - {lbl}")

    if LIST_ONLY:
        return {}

    # Load crash-resume progress
    prog_path = _progress_path(level)
    captured: dict[str, int | None] = {}
    if os.path.exists(prog_path):
        with open(prog_path) as f:
            captured = json.load(f)
        print(f"  Resuming — {len(captured)} already captured.")

    print()
    for i, label in enumerate(labels, 1):
        if label in captured:
            print(f"  [{i}/{len(labels)}] {label!r}  (skipped — already done)")
            continue

        print(f"  [{i}/{len(labels)}] {label!r}", end="", flush=True)

        # Re-open modal if it closed after the previous search
        if not await modal.is_visible():
            await page.mouse.move(random.randint(200, 600), random.randint(200, 400))
            await page.wait_for_timeout(random.randint(400, 900))
            await toolbar.click()
            await modal.wait_for(state="visible", timeout=10_000)
            await page.wait_for_timeout(random.randint(600, 1200))

        # Scroll so the target dropdown is in view
        await page.evaluate(
            """() => {
                const mb = document.querySelector('.modal-body');
                if (mb) mb.scrollTop = mb.scrollHeight / 2;
            }"""
        )
        await page.wait_for_timeout(random.randint(300, 600))

        ok = await _select_option(page, ng, label)
        if not ok:
            print("  ! could not select, skipping")
            captured[label] = None
            with open(prog_path, "w") as f:
                json.dump(captured, f, ensure_ascii=False)
            continue

        await page.wait_for_timeout(random.randint(500, 1200))
        await page.mouse.move(random.randint(400, 700), random.randint(500, 650))
        await page.wait_for_timeout(random.randint(200, 500))

        id_val = None
        try:
            async with page.expect_request(
                lambda r: API_PATH in r.url and r.method == "POST",
                timeout=10_000,
            ) as req_info:
                await pesquisar.click()
            req    = await req_info.value
            body   = req.post_data_json or {}
            id_val = body.get(field)
        except Exception:
            await pesquisar.click()

        captured[label] = id_val
        print(f"  → {field} = {id_val}")

        with open(prog_path, "w") as f:
            json.dump(captured, f, ensure_ascii=False)

        await page.wait_for_timeout(random.randint(2000, 5000))

    # Write final output
    out = _output_path(level)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(captured, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved {len(captured)} entries to {out}")

    return captured


async def run(levels_to_scrape: list[str]) -> dict[str, dict]:
    results = {}

    async with async_playwright() as pw:
        headless = os.environ.get("HEADLESS", "false").lower() != "false"
        browser  = await pw.chromium.launch(
            headless=headless,
            slow_mo=0,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context()

        cookies = _build_cookies()
        if cookies:
            await context.add_cookies(cookies)
            print(f"Injected {len(cookies)} session cookie(s).")
        else:
            print("No cookies found in .env — log in manually in the browser.")

        ls_script = _build_local_storage_script()
        if ls_script:
            await context.add_init_script(ls_script)
            print("localStorage auth items queued for injection.")

        page = await context.new_page()

        ok = await _wait_for_wizard(page)
        if not ok:
            await browser.close()
            return {}

        print("Wizard ready.")
        os.makedirs("output", exist_ok=True)

        for level in levels_to_scrape:
            cfg = LEVELS[level]
            results[level] = await _scrape_level(page, level, cfg)

            # After scraping each level, reset the modal for the next level
            if level != levels_to_scrape[-1]:
                modal = page.locator(MODAL)
                if not await modal.is_visible():
                    toolbar = page.locator("#buscaToolbar")
                    await toolbar.click()
                    await modal.wait_for(state="visible", timeout=10_000)
                    await page.wait_for_timeout(random.randint(800, 1500))

                # Reload page between levels to clear all selections cleanly
                print(f"\nReloading page before next level...")
                ok = await _wait_for_wizard(page)
                if not ok:
                    print("WARNING: wizard reload failed, remaining levels may fail.")

        await browser.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="Scrape family-level lookup tables from Gcom UI")
    parser.add_argument(
        "--level",
        choices=list(LEVELS.keys()),
        default=None,
        help="Single level to scrape (default: all levels in order)",
    )
    args = parser.parse_args()

    levels_to_scrape = [args.level] if args.level else list(LEVELS.keys())
    print(f"Levels to scrape: {levels_to_scrape}")

    results = asyncio.run(run(levels_to_scrape))
    if not results:
        print("\nNo data captured.")
        return

    print("\n\n# ── Summary ──────────────────────────────────────────────────────")
    for level, captured in results.items():
        field = LEVELS[level]["field"]
        print(f"\n# {level.upper()} ({field})")
        print(f"LOOKUP_{level.upper()} = {{")
        for label, id_val in sorted(captured.items(), key=lambda x: (x[1] is None, x[1] or 0)):
            print(f"    {id_val}: {label!r},")
        print("}")


if __name__ == "__main__":
    main()
