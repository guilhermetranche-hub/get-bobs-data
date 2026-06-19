"""
Automates the GCOM product wizard to discover the real id_fam_pro3 for each
subgroup label by intercepting the POST to SelecionarProduto.

The SUBGRUPO picker is <app-familia-produto-select nivel="3"> containing an
ng-select component.  We target it with a precise CSS descendant selector,
click each option, click PESQUISAR, and read id_fam_pro3 off the POST body.

Run (local, headed):
    HEADLESS=false .venv/bin/python scrape_subgroups.py

Useful env knobs:
    LIST_ONLY=true   open the dropdown, print all options, then exit
    HEADLESS=false   show the browser window (default: false = headed)
"""

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
API_PATH = "/GcomProdutoService/Produto/SelecionarProduto"

# Scope to the search modal — the creation wizard behind it has identical components
# which cause strict-mode violations when both forms are mounted simultaneously.
SUBGROUP_SELECTOR = (
    '#modal-app-cadastro-produto-consulta '
    'app-familia-produto-select:has(label:text-is("SUBGRUPO")) '
    'ng-select.app-familia-produto-select'
)
PANEL = ".ng-dropdown-panel"
OPTION = ".ng-option"

LIST_ONLY = os.environ.get("LIST_ONLY", "false").lower() == "true"


def _build_local_storage_script() -> str:
    """Return a JS snippet that pre-populates localStorage before Angular boots."""
    items = {
        "jwtToken": os.environ.get("LS_JWT_TOKEN", ""),
        "timerNotificacao": "N",
        "activeModuleSearch": "PRODUTOS",
        "activeModule": "PRODUTOS",
        "activeSubmodule": "CADASTROS",
    }
    # LS_USER is already a JSON object string — store it as-is
    ls_user = os.environ.get("LS_USER", "")
    if ls_user:
        items["user"] = ls_user

    lines = [f"localStorage.setItem({json.dumps(k)}, {json.dumps(v)});"
             for k, v in items.items() if v]
    return "\n".join(lines)


def _build_cookies() -> list[dict]:
    cookies = []
    for name, env_key in [
        (".Stackify.Rum", "COOKIE_STACKIFY"),
        ("ASP.NET_SessionId", "COOKIE_SESSION"),
    ]:
        val = os.environ.get(env_key)
        if val:
            cookies.append({"name": name, "value": val,
                            "domain": "www2.gcom.com.br", "path": "/"})
    aspnet_name = os.environ.get("COOKIE_ASPNET_NAME", "ASPSESSIONIDCEDTABAR")
    aspnet_val = os.environ.get("COOKIE_ASPNET")
    if aspnet_val:
        cookies.append({"name": aspnet_name, "value": aspnet_val,
                        "domain": "www2.gcom.com.br", "path": "/"})
    return cookies


async def open_dropdown(page, ng):
    await ng.click()
    panel = page.locator(PANEL)
    await panel.wait_for(state="visible", timeout=8_000)
    return panel


async def list_options(page, ng) -> list[str]:
    panel = await open_dropdown(page, ng)
    opts = panel.locator(OPTION)
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


async def select_option(page, ng, label: str) -> bool:
    panel = await open_dropdown(page, ng)
    inp = ng.locator("input[type='text']")
    if await inp.count() > 0:
        await inp.fill("")
        await inp.type(label, delay=15)
        await page.wait_for_timeout(400)

    # Exact match: strip surrounding whitespace, must equal label exactly
    exact_pattern = re.compile(r"^\s*" + re.escape(label) + r"\s*$")
    option = panel.locator(OPTION).filter(has_text=exact_pattern).first
    if await option.count() == 0:
        await page.keyboard.press("Escape")
        return False

    await option.click()
    await page.wait_for_timeout(200)
    return True


async def run():
    captured: dict[str, int | None] = {}

    async with async_playwright() as pw:
        headless = os.environ.get("HEADLESS", "false").lower() != "false"
        browser = await pw.chromium.launch(
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

        await page.goto(WIZARD_URL)

        try:
            print("Waiting for wizard page...")
            await page.wait_for_url("**wizard-cadastro-produto**", timeout=60_000)
            print(f"Current URL: {page.url}")
            os.makedirs("output", exist_ok=True)
            await page.screenshot(path="output/debug_landing.png", full_page=True)
            print("Screenshot saved to output/debug_landing.png")
            # SweetAlert2 overlay appears while the app loads dropdown data.
            # With localStorage auth injected it should clear within a few seconds.
            overlay = page.locator(".swal2-container")
            if await overlay.count() > 0:
                print("Loading overlay detected, waiting for it to clear...")
                await overlay.wait_for(state="hidden", timeout=30_000)
            os.makedirs("output", exist_ok=True)
            await page.screenshot(path="output/debug_ready.png", full_page=True)
            print("Screenshot saved to output/debug_ready.png")
            # scroll modal body to bottom so family dropdowns are rendered/visible
            await page.evaluate(
                "document.querySelector('.modal-body')?.scrollTo(0, 99999)"
            )
            await page.wait_for_timeout(500)
            await page.screenshot(path="output/debug_scrolled.png", full_page=True)
            print("Scrolled screenshot saved to output/debug_scrolled.png")
            # wait for the SUBGRUPO component to be in the DOM
            await page.locator(SUBGROUP_SELECTOR).wait_for(state="attached", timeout=20_000)
            print("Wizard ready.")
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            os.makedirs("output", exist_ok=True)
            await page.screenshot(path="output/debug_timeout.png", full_page=True)
            print("Screenshot saved to output/debug_timeout.png")
            await browser.close()
            return {}

        ng = page.locator(SUBGROUP_SELECTOR)
        pesquisar = page.locator(
            '#modal-app-cadastro-produto-consulta button.btn-success'
        ).first

        labels = await list_options(page, ng)
        print(f"\nSUBGRUPO dropdown has {len(labels)} option(s):")
        for lbl in labels:
            print(f"    - {lbl}")

        if LIST_ONLY:
            print("\nLIST_ONLY — stopping here.")
            await browser.close()
            return {}

        # Toolbar button that re-opens the search modal after results are shown
        toolbar_search = page.locator('#buscaToolbar')
        modal = page.locator('#modal-app-cadastro-produto-consulta')

        # Load any progress saved from a previous crashed run
        progress_path = "output/subgroup_progress.json"
        os.makedirs("output", exist_ok=True)
        if os.path.exists(progress_path):
            with open(progress_path) as f:
                captured = json.load(f)
            print(f"Resuming — {len(captured)} already captured.")

        print("\nIterating subgroups...\n")
        for i, label in enumerate(labels, 1):
            if label in captured:
                print(f"  [{i}/{len(labels)}] {label!r}  (skipped — already done)")
                continue

            print(f"  [{i}/{len(labels)}] {label!r}", end="", flush=True)

            # Re-open modal if it closed after the previous search
            if not await modal.is_visible():
                await page.mouse.move(
                    random.randint(200, 600), random.randint(200, 400)
                )
                await page.wait_for_timeout(random.randint(400, 900))
                await toolbar_search.click()
                await modal.wait_for(state="visible", timeout=10_000)
                await page.wait_for_timeout(random.randint(600, 1200))

            # Scroll modal so the SUBGRUPO dropdown is in view
            await page.evaluate(
                """() => {
                    const mb = document.querySelector('.modal-body');
                    if (mb) mb.scrollTop = mb.scrollHeight / 2;
                }"""
            )
            await page.wait_for_timeout(random.randint(300, 600))

            ok = await select_option(page, ng, label)
            if not ok:
                print("  ! could not select, skipping")
                captured[label] = None
                with open(progress_path, "w") as f:
                    json.dump(captured, f, ensure_ascii=False)
                continue

            # Human-like pause before clicking PESQUISAR
            await page.wait_for_timeout(random.randint(500, 1200))
            await page.mouse.move(
                random.randint(400, 700), random.randint(500, 650)
            )
            await page.wait_for_timeout(random.randint(200, 500))

            # Capture exactly the POST triggered by this click (avoids background-request race)
            id_val = None
            try:
                async with page.expect_request(
                    lambda r: API_PATH in r.url and r.method == "POST",
                    timeout=10_000,
                ) as req_info:
                    await pesquisar.click()
                req = await req_info.value
                body = req.post_data_json or {}
                id_val = body.get("id_fam_pro3")
            except Exception:
                await pesquisar.click()
            captured[label] = id_val
            print(f"  → id_fam_pro3 = {id_val}")

            # Save progress after every capture
            with open(progress_path, "w") as f:
                json.dump(captured, f, ensure_ascii=False)

            # Human-like pause between subgroups (2–5 s)
            await page.wait_for_timeout(random.randint(2000, 5000))

        await browser.close()

    return captured


def main():
    result = asyncio.run(run())
    if not result:
        print("\nNo data captured.")
        return

    print("\n\n# ── Corrected SUBGROUP_LOOKUP (id_fam_pro3 → label) ─────────────────")
    print("SUBGROUP_LOOKUP = {")
    for label, id_val in sorted(result.items(), key=lambda x: (x[1] is None, x[1] or 0)):
        print(f"    {id_val}: {label!r},")
    print("}")

    os.makedirs("output", exist_ok=True)
    out_path = "output/subgroup_lookup.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nAlso saved to {out_path}")


if __name__ == "__main__":
    main()
