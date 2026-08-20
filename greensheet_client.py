from asyncio.log import logger
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import (
    sync_playwright,
)

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from config import (
    GREENSHEET_USERNAME,
    GREENSHEET_PASSWORD,
    GREENSHEET_LOGIN_URL,
    GREENSHEET_PROJECTS_URL,
    GREENSHEET_PERMITS_URL,
    DOWNLOAD_DIR,
    HEADLESS,
    BROWSER_TIMEOUT,
)


class GreenSheetClient:

    def __init__(self, logger):

        self.logger = logger

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # -----------------------------------------------------
    # Start browser
    # -----------------------------------------------------

    def start(self):

        self.logger.info(
            "Starting Chromium..."
        )

        self.playwright = (
            sync_playwright().start()
        )

        self.browser = (
            self.playwright.chromium.launch(
                headless=HEADLESS
            )
        )

        self.context = (
            self.browser.new_context(
                accept_downloads=True
            )
        )

        self.page = (
            self.context.new_page()
        )

        self.page.set_default_timeout(
            BROWSER_TIMEOUT
        )

    # -----------------------------------------------------
    # Login
    # -----------------------------------------------------

    def login(self):
        logger.info("Opening Green Sheet login...")

        self.page.goto(
            GREENSHEET_LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        logger.info("Entering Green Sheet credentials...")

        self.page.get_by_placeholder(
            "Username"
        ).fill(
            GREENSHEET_USERNAME
        )

        self.page.get_by_placeholder(
            "Password"
        ).fill(
            GREENSHEET_PASSWORD
        )

        logger.info("Submitting Green Sheet login...")

        self.page.get_by_role(
            "button",
            name="Login",
            exact=True,
        ).click()

        self.page.wait_for_load_state(
            "domcontentloaded"
        )

        logger.info(
            "Green Sheet login submitted. Current URL: %s",
            self.page.url,
        )

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    def download_projects(self):

        if not GREENSHEET_PROJECTS_URL:
            raise RuntimeError(
                "GREENSHEET_PROJECTS_URL "
                "has not been configured yet."
            )

        self.logger.info(
            "Opening Green Sheet Projects..."
        )

        self.page.goto(
            GREENSHEET_PROJECTS_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        self.logger.info(
            "Member page loaded: %s",
            self.page.url,
        )

        projects_url = (
            "https://greensheet.ca/members/"
            "project_results.php"
            "?button_clicked=btn_basic"
            "&do=projectsall"
        )

        self.logger.info(
            "Opening All Projects results..."
        )

        self.page.goto(
            projects_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        self.page.wait_for_timeout(2000)

        self.logger.info(
            "Projects results loaded: %s",
            self.page.url,
        )

        #
        # First-stage Excel / CSV button.
        #
        self.logger.info(
            "Opening Excel / CSV export page..."
        )

        csv_locator = self.page.locator(
            "#viewexcel"
        )

        csv_locator.wait_for(
            state="visible",
            timeout=15000,
        )

        #
        # Clicking #viewexcel runs CheckSelectBoxes()
        # and navigates to project_set_output.php.
        #
        with self.page.expect_navigation(
            wait_until="domcontentloaded",
            timeout=60000,
        ):
            csv_locator.click()

        self.logger.info(
            "Export page loaded: %s",
            self.page.url,
        )

        if "project_set_output.php" not in self.page.url:
            raise RuntimeError(
                "Unexpected page after clicking "
                "Excel / CSV: "
                f"{self.page.url}"
            )

        self.page.wait_for_timeout(1500)

        #
        # Look for the actual download control
        # on project_set_output.php.
        #
        self.logger.info(
            "Looking for final CSV/Excel download control..."
        )

        controls = self.page.locator(
            "a, button, input[type='submit'], "
            "input[type='button']"
        )

        download_locator = None

        for i in range(controls.count()):

            control = controls.nth(i)

            try:
                if not control.is_visible():
                    continue

                text = (
                    control.inner_text()
                    or control.get_attribute("value")
                    or control.get_attribute("title")
                    or control.get_attribute("aria-label")
                    or ""
                ).strip()

                href = (
                    control.get_attribute("href")
                    or ""
                )

                control_id = (
                    control.get_attribute("id")
                    or ""
                )

                name = (
                    control.get_attribute("name")
                    or ""
                )

                combined = (
                    f"{text} {href} {control_id} {name}"
                ).lower()

                if (
                    "csv" in combined
                    or "excel" in combined
                    or "download" in combined
                ):
                    self.logger.info(
                        "Export candidate %s: "
                        "text=%r href=%r "
                        "id=%r name=%r",
                        i,
                        text,
                        href,
                        control_id,
                        name,
                    )

                    download_locator = control
                    break

            except Exception:
                continue

        if download_locator is None:

            self.logger.error(
                "Could not find final CSV/Excel "
                "download control."
            )

            #
            # Print everything useful on this page
            # so we can identify the real control.
            #
            for i in range(
                min(controls.count(), 150)
            ):

                try:
                    control = controls.nth(i)

                    if not control.is_visible():
                        continue

                    text = (
                        control.inner_text()
                        or control.get_attribute("value")
                        or control.get_attribute("title")
                        or control.get_attribute("aria-label")
                        or ""
                    ).strip()

                    href = (
                        control.get_attribute("href")
                        or ""
                    )

                    control_id = (
                        control.get_attribute("id")
                        or ""
                    )

                    name = (
                        control.get_attribute("name")
                        or ""
                    )

                    onclick = (
                        control.get_attribute("onclick")
                        or ""
                    )

                    if (
                        text
                        or href
                        or control_id
                        or name
                        or onclick
                    ):
                        self.logger.info(
                            "Control %s: "
                            "text=%r href=%r "
                            "id=%r name=%r "
                            "onclick=%r",
                            i,
                            text,
                            href,
                            control_id,
                            name,
                            onclick,
                        )

                except Exception:
                    continue

            raise RuntimeError(
                "Final export control was not found "
                "on project_set_output.php."
            )

        #
        # Try actual download.
        #
        self.logger.info(
            "Starting final Projects download..."
        )

        download = None

        try:

            with self.page.expect_download(
                timeout=15000,
            ) as info:

                download_locator.click(
                    timeout=15000,
                )

            download = info.value

        except Exception:
            self.logger.warning(
                "Final export control did not "
                "trigger a Playwright download event."
            )

        if download is None:

            self.logger.info(
                "URL after final export click: %s",
                self.page.url,
            )

            try:
                self.logger.info(
                    "Final export outerHTML: %s",
                    download_locator.evaluate(
                        "(el) => el.outerHTML"
                    ),
                )
            except Exception:
                pass

            raise RuntimeError(
                "Final export did not produce "
                "a browser download."
            )

        suggested = download.suggested_filename

        suffix = Path(suggested).suffix

        if not suffix:
            suffix = ".xlsx"

        filename = (
            DOWNLOAD_DIR
            / (
                "projects-"
                f"{datetime.now():%Y%m%d-%H%M%S}"
                f"{suffix}"
            )
        )

        download.save_as(
            str(filename)
        )

        self.logger.info(
            "Projects saved to %s",
            filename,
        )

        return filename
    # -----------------------------------------------------
    # Permits
    # -----------------------------------------------------

    def download_permits(self):

        if not GREENSHEET_PERMITS_URL:
            raise RuntimeError(
                "GREENSHEET_PERMITS_URL "
                "has not been configured yet."
            )

        self.logger.info(
            "Opening Green Sheet Permits..."
        )

        self.page.goto(
            GREENSHEET_PERMITS_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        self.page.wait_for_timeout(2000)

        self.logger.info(
            "Permits page loaded: %s",
            self.page.url,
        )

        self.logger.info(
            "Permit page title: %s",
            self.page.title(),
        )

        try:
            body_text = (
                self.page.locator("body")
                .inner_text()
            )

            self.logger.info(
                "Permit page text preview: %r",
                body_text[:1000],
            )

        except Exception as exc:
            self.logger.warning(
                "Could not read Permit page text: %s",
                exc,
            )

        self.logger.info(
            "Looking for Permits Excel / CSV export..."
        )

        #
        # Search visible controls for anything
        # associated with Excel, CSV, or downloading.
        #
        controls = self.page.locator(
            "a, button, input[type='submit'], "
            "input[type='button']"
        )

        export_locator = None

        for i in range(controls.count()):

            control = controls.nth(i)

            try:
                if not control.is_visible():
                    continue

                text = (
                    control.inner_text()
                    or control.get_attribute("value")
                    or control.get_attribute("title")
                    or control.get_attribute("aria-label")
                    or ""
                ).strip()

                href = (
                    control.get_attribute("href")
                    or ""
                )

                control_id = (
                    control.get_attribute("id")
                    or ""
                )

                name = (
                    control.get_attribute("name")
                    or ""
                )

                onclick = (
                    control.get_attribute("onclick")
                    or ""
                )

                combined = (
                    f"{text} "
                    f"{href} "
                    f"{control_id} "
                    f"{name} "
                    f"{onclick}"
                ).lower()

                if (
                    "csv" in combined
                    or "excel" in combined
                    or "download" in combined
                ):
                    self.logger.info(
                        "Permit export candidate %s: "
                        "text=%r href=%r "
                        "id=%r name=%r onclick=%r",
                        i,
                        text,
                        href,
                        control_id,
                        name,
                        onclick,
                    )

                    export_locator = control
                    break

            except Exception:
                continue

        #
        # If no export control exists, print useful
        # diagnostics about the actual page.
        #
        if export_locator is None:

            self.logger.error(
                "Could not find a visible Permit "
                "Excel / CSV export control."
            )

            self.logger.info(
                "Current Permit URL: %s",
                self.page.url,
            )

            diagnostic_controls = (
                self.page.locator(
                    "a, button, input, select"
                )
            )

            self.logger.info(
                "Permit page controls found: %s",
                diagnostic_controls.count(),
            )

            for i in range(
                min(
                    diagnostic_controls.count(),
                    200,
                )
            ):

                try:
                    control = (
                        diagnostic_controls.nth(i)
                    )

                    if not control.is_visible():
                        continue

                    tag = control.evaluate(
                        "(el) => el.tagName"
                    )

                    text = (
                        control.inner_text()
                        or control.get_attribute("value")
                        or control.get_attribute("title")
                        or control.get_attribute(
                            "aria-label"
                        )
                        or ""
                    ).strip()

                    href = (
                        control.get_attribute("href")
                        or ""
                    )

                    control_id = (
                        control.get_attribute("id")
                        or ""
                    )

                    name = (
                        control.get_attribute("name")
                        or ""
                    )

                    onclick = (
                        control.get_attribute("onclick")
                        or ""
                    )

                    self.logger.info(
                        "Permit control %s: "
                        "tag=%r text=%r href=%r "
                        "id=%r name=%r onclick=%r",
                        i,
                        tag,
                        text,
                        href,
                        control_id,
                        name,
                        onclick,
                    )

                except Exception:
                    continue

            #
            # Export may be implemented as a form.
            #
            forms = self.page.locator("form")

            self.logger.info(
                "Permit forms found: %s",
                forms.count(),
            )

            for i in range(forms.count()):

                try:
                    form = forms.nth(i)

                    self.logger.info(
                        "Permit form %s: "
                        "action=%r method=%r "
                        "id=%r name=%r",
                        i,
                        form.get_attribute("action"),
                        form.get_attribute("method"),
                        form.get_attribute("id"),
                        form.get_attribute("name"),
                    )

                except Exception:
                    continue

            raise RuntimeError(
                "Could not find Permit export control. "
                "Check the logged Permit page text, "
                "controls, and forms."
            )

        #
        # Log the actual element before clicking it.
        #
        try:
            self.logger.info(
                "Permit export outerHTML: %s",
                export_locator.evaluate(
                    "(el) => el.outerHTML"
                ),
            )

        except Exception as exc:
            self.logger.warning(
                "Could not inspect Permit "
                "export control: %s",
                exc,
            )

        self.logger.info(
            "Opening Permit export..."
        )

        old_url = self.page.url
        download = None

        #
        # First try a normal browser download.
        #
        try:

            with self.page.expect_download(
                timeout=5000,
            ) as info:

                export_locator.click(
                    timeout=15000,
                )

            download = info.value

        except Exception:

            self.logger.info(
                "No direct Permit download event "
                "detected; checking navigation..."
            )

        #
        # Case 1:
        # the first export control caused a real download.
        #
        if download is not None:
            suggested = download.suggested_filename
            suffix = Path(suggested).suffix
            if not suffix:
                suffix = ".xlsx"
            filename = (
                DOWNLOAD_DIR
                / (
                    "permits-"
                    f"{datetime.now():%Y%m%d-%H%M%S}"
                    f"{suffix}"
                )
            )

            download.save_as(
                str(filename)
            )

            self.logger.info(
                "Permits saved to %s",
                filename,
            )

            return filename

        #
        # Case 2:
        # export may have navigated to another page.
        #
        self.page.wait_for_timeout(3000)

        self.logger.info(
            "Permit URL before export: %s",
            old_url,
        )

        self.logger.info(
            "Permit URL after export: %s",
            self.page.url,
        )

        if self.page.url == old_url:

            raise RuntimeError(
                "Permit export control did not "
                "trigger a download or navigation."
            )

        self.logger.info(
            "Permit export navigated to another page."
        )

        self.page.wait_for_load_state(
            "domcontentloaded"
        )

        self.page.wait_for_timeout(1500)

        #
        # Search the intermediate export page for the
        # final download button.
        #
        self.logger.info(
            "Looking for final Permit "
            "CSV/Excel download control..."
        )

        final_controls = self.page.locator(
            "a, button, input[type='submit'], "
            "input[type='button']"
        )

        final_export = None

        for i in range(
            final_controls.count()
        ):

            control = final_controls.nth(i)

            try:
                if not control.is_visible():
                    continue

                text = (
                    control.inner_text()
                    or control.get_attribute("value")
                    or control.get_attribute("title")
                    or control.get_attribute(
                        "aria-label"
                    )
                    or ""
                ).strip()

                href = (
                    control.get_attribute("href")
                    or ""
                )

                control_id = (
                    control.get_attribute("id")
                    or ""
                )

                name = (
                    control.get_attribute("name")
                    or ""
                )

                onclick = (
                    control.get_attribute("onclick")
                    or ""
                )

                combined = (
                    f"{text} "
                    f"{href} "
                    f"{control_id} "
                    f"{name} "
                    f"{onclick}"
                ).lower()

                if (
                    "csv" in combined
                    or "excel" in combined
                    or "download" in combined
                ):

                    self.logger.info(
                        "Final Permit export "
                        "candidate %s: "
                        "text=%r href=%r "
                        "id=%r name=%r "
                        "onclick=%r",
                        i,
                        text,
                        href,
                        control_id,
                        name,
                        onclick,
                    )

                    final_export = control
                    break

            except Exception:
                continue

        #
        # Nothing found on the intermediate page.
        #
        if final_export is None:

            self.logger.error(
                "Could not find final Permit "
                "download control."
            )

            self.logger.info(
                "Intermediate Permit page URL: %s",
                self.page.url,
            )

            for i in range(
                min(
                    final_controls.count(),
                    200,
                )
            ):

                try:
                    control = (
                        final_controls.nth(i)
                    )

                    if not control.is_visible():
                        continue

                    text = (
                        control.inner_text()
                        or control.get_attribute(
                            "value"
                        )
                        or control.get_attribute(
                            "title"
                        )
                        or control.get_attribute(
                            "aria-label"
                        )
                        or ""
                    ).strip()

                    href = (
                        control.get_attribute(
                            "href"
                        )
                        or ""
                    )

                    control_id = (
                        control.get_attribute(
                            "id"
                        )
                        or ""
                    )

                    name = (
                        control.get_attribute(
                            "name"
                        )
                        or ""
                    )

                    onclick = (
                        control.get_attribute(
                            "onclick"
                        )
                        or ""
                    )

                    self.logger.info(
                        "Final Permit control %s: "
                        "text=%r href=%r "
                        "id=%r name=%r "
                        "onclick=%r",
                        i,
                        text,
                        href,
                        control_id,
                        name,
                        onclick,
                    )

                except Exception:
                    continue

            raise RuntimeError(
                "Permit export reached an "
                "intermediate page, but the "
                "final download control was "
                "not found."
            )

        #
        # Log the final export HTML.
        #
        try:
            self.logger.info(
                "Final Permit export "
                "outerHTML: %s",
                final_export.evaluate(
                    "(el) => el.outerHTML"
                ),
            )

        except Exception:
            pass

        #
        # Attempt final download.
        #
        self.logger.info(
            "Starting final Permit download..."
        )

        download = None

        try:

            with self.page.expect_download(
                timeout=15000,
            ) as info:

                final_export.click(
                    timeout=15000,
                )

            download = info.value

        except Exception:

            self.logger.warning(
                "Final Permit export control "
                "did not trigger a browser "
                "download."
            )

        if download is None:

            self.logger.info(
                "URL after final Permit "
                "export click: %s",
                self.page.url,
            )

            raise RuntimeError(
                "Final Permit export did not "
                "produce a browser download."
            )

        #
        # Save final CSV.
        #
        filename = (
            DOWNLOAD_DIR
            / (
                "permits-"
                f"{datetime.now():%Y%m%d-%H%M%S}"
                ".csv"
            )
        )

        download.save_as(
            str(filename)
        )

        self.logger.info(
            "Permits saved to %s",
            filename,
        )

        return filename
    # -----------------------------------------------------
    # Close browser
    # -----------------------------------------------------

    def close(self):

        self.logger.info(
            "Closing browser..."
        )

        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()