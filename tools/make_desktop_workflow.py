"""Writes .github/workflows/desktop.yml: Euro-Office's own desktop build (Windows, Linux, macOS), pinned to the
DesktopEditors commit in upstream.lock.json, rebranded as MNOffice.

We start from Euro-Office's unbranded, unsigned "euro-office" rows, rename them, point the icons and packaging overlay at
desktop/brand/ in this repository, drop the Nextcloud brand and Euro-Office's own publishing jobs, and add one job that
publishes everything as a GitHub release. Re-run after updating the pin:

    python3 tools/make_desktop_workflow.py
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pin = json.load(open(os.path.join(ROOT, "upstream.lock.json")))["desktop"]["commit"]
src = urllib.request.urlopen("https://raw.githubusercontent.com/euro-office/DesktopEditors/%s/.github/workflows/build.yml" % pin).read().decode()
lines = src.split("\n")

# 1. drop every "- name: nextcloud-office" matrix row (up to the next row or the end of the list)
out, skip, indent = [], False, 0
for ln in lines:
    stripped = ln.lstrip(); ind = len(ln) - len(stripped)
    if stripped.startswith("- name: nextcloud-office"):
        skip, indent = True, ind; continue
    if skip:
        if stripped and (ind < indent or (ind == indent and stripped.startswith("- "))) or (stripped and ind <= indent - 2):
            skip = False
        else:
            continue
    out.append(ln)
text = "\n".join(out)

# 2. Euro-Office's own publishing jobs need its servers and secrets; keep the build jobs only
cut = re.search(r"\n  pr-comment:\n", text)
text = text[:cut.start()] + "\n" if cut else text

# 3. the brand: names, bundle id, icons and the packaging overlay
rename = [("app_bundle: Euro-Office.app", "app_bundle: MNOffice.app"),
          ("package_name: Euro-Office-DesktopEditors", "package_name: MNOffice"),
          ("company_name: Euro-Office", "company_name: Mundus Novus"),
          ("product_name: Euro-Office", "product_name: MNOffice"),
          ("publisher_name: Euro-Office", "publisher_name: Mundus Novus"),
          ("publisher_url: https://github.com/Euro-Office/DesktopEditors", "publisher_url: https://office.mundusnovus.org"),
          ("bundle_id: asc.euro-office.Euro-Office", "bundle_id: org.mundusnovus.office"),
          ('app_icon_svg: ""', "app_icon_svg: build/brands/mn-office-brand/svg/app-icon.svg"),
          ('tab_icon_light_svg: ""', "tab_icon_light_svg: build/brands/mn-office-brand/svg/logo-light.svg"),
          ('tab_icon_dark_svg: ""', "tab_icon_dark_svg: build/brands/mn-office-brand/svg/logo-dark.svg"),
          ('branding_dir: "."', 'branding_dir: "./build/brands/mn-office-brand"'),
          ("- name: euro-office", "- name: mn-office"),
          ("REGISTRY: ghcr.io/euro-office", "REGISTRY: ghcr.io/mundusnovus")]
for a, b in rename:
    text = text.replace(a, b)

# 4. checkouts: Euro-Office's repository at our pin, and our brand overlay instead of the Nextcloud brand repo
text = re.sub(r"\n(\s*)token: \$\{\{ secrets\.EURO_OFFICE_MIRROR_TOKEN \}\}", "", text)
brand_step = re.compile(r"- name: Checkout nextcloud-office-brand repo\n(\s*)uses: [^\n]+\n(?:\s+[^\n]+\n)*?\s*path: build/brands/nextcloud-office-brand")
def our_brand(m):
    sp = m.group(1)
    # only desktop/brand, and nothing of ours left in the build folder afterwards: the whole repository there ends up
    # in the Docker build of the editors and broke it
    return ("- name: Checkout the MNOffice brand\n" + sp + "uses: actions/checkout@v4\n" + sp + "with:\n" + sp + "  repository: ${{ github.repository }}\n"
            + sp + "  path: build/mn-office\n" + sp + "  sparse-checkout: desktop/brand\n"
            + sp[:-2] + "- name: Place the brand overlay\n" + sp + "run: mkdir -p build/brands && cp -R build/mn-office/desktop/brand build/brands/mn-office-brand && rm -rf build/mn-office")
text, n = brand_step.subn(our_brand, text)
if n == 0:
    sys.exit("could not find the brand checkout steps; the upstream workflow changed")
def fix_checkout(m):
    block = m.group(0)
    if "repository:" in block:
        return block
    ind = re.search(r"\n(\s*)with:", block)
    if not ind:
        return block + "\n        with:\n          repository: Euro-Office/DesktopEditors\n          ref: %s" % pin
    sp = ind.group(1) + "  "
    return block.replace(ind.group(0), ind.group(0) + "\n" + sp + "repository: Euro-Office/DesktopEditors\n" + sp + "ref: " + pin, 1)
text = re.sub(r"- (?:name: [^\n]+\n\s*)?uses: actions/checkout@[^\n]+(?:\n\s+with:(?:\n\s{10,}[^\n]+)*)?", fix_checkout, text)
text = text.replace("nextcloud-office-brand", "mn-office-brand")

# 4a. the shared build (build-common) stays exactly as Euro-Office's own row: it builds the editors that every brand
#     shares, and the brand is applied afterwards in each platform's job.
a, b = text.find("\n  build-common:"), text.find("\n  build-windows:")
if a < 0 or b < 0:
    sys.exit("could not find build-common; the upstream workflow changed")
common = text[a:b]
for ours, theirs in (('branding_dir: "./build/brands/mn-office-brand"', 'branding_dir: "."'),
                     ("company_name: Mundus Novus", "company_name: Euro-Office"),
                     ("product_name: MNOffice", "product_name: Euro-Office")):
    common = common.replace(ours, theirs)
text = text[:a] + common + text[b:]

# 4b. sign the macOS app ad hoc before it goes into the disk image, so macOS does not call it damaged
dmg_step = '      - name: Build the DMG installer\n'
if dmg_step not in text:
    sys.exit("could not find the DMG step; the upstream workflow changed")
text = text.replace(dmg_step, """      - name: Sign the app (ad hoc) so Gatekeeper accepts it
        run: |
          codesign --force --deep --sign - "build/macos/out/${{ matrix.brand.app_bundle }}"
          codesign --verify --deep --strict "build/macos/out/${{ matrix.brand.app_bundle }}"

""" + dmg_step, 1)

# 4c. our release tags are desktop-vX.Y.Z; Euro-Office's version step expects vX.Y.Z
ver = '          REF_NAME=$(echo "$GITHUB_REF_NAME"'
if ver not in text:
    sys.exit("could not find the version step; the upstream workflow changed")
text = text.replace(ver, '          GITHUB_REF_NAME="${GITHUB_REF_NAME#desktop-}"\n' + ver, 1)

# 5. triggers, and one job that publishes every package as a release
text = re.sub(r"^on:\n(?:  .*\n|\n)*?(?=\S)", "on:\n  workflow_dispatch:\n  push:\n    tags: ['desktop-v*']\n\n", text, count=1, flags=re.M)
text = text.rstrip() + """

  # Mundus Novus: publish every package from this run as one GitHub release
  publish:
    needs: [build-linux, build-windows, build-macos]
    if: ${{ always() && startsWith(github.ref, 'refs/tags/') }}
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: '*-packages-mn-office-*'
          path: dist
          merge-multiple: true
      - uses: softprops/action-gh-release@v2
        with:
          name: MNOffice Desktop ${{ github.ref_name }}
          files: dist/**
          fail_on_unmatched_files: false
"""
header = ("# Generated by tools/make_desktop_workflow.py from Euro-Office's DesktopEditors build (commit %s).\n"
          "# Do not edit by hand: change the generator and re-run it. Euro-Office: AGPL-3.0; this file: Mundus Novus Affero License.\n") % pin
os.makedirs(os.path.join(ROOT, ".github", "workflows"), exist_ok=True)
open(os.path.join(ROOT, ".github", "workflows", "desktop.yml"), "w").write(header + text)
print("wrote .github/workflows/desktop.yml; mn-office rows:", text.count("- name: mn-office"))
