# Hands 4 Unity website

Static website for Hands 4 Unity CLG, replacing the old WordPress site at hands4unity.org.
Plain HTML, CSS and JavaScript. No frameworks, no build dependencies.

## Editing content

All page content lives in `_build/`:

| File | What it holds |
| --- | --- |
| `_build/content.py` | Contact details, vision and mission, services, team bios, supporters, financial summary |
| `_build/projects.py` | Every project page: text, photos, dates, event details |
| `_build/build.py` | Shared header and footer, and the layout of each page |

After editing, rebuild the HTML pages:

```sh
python3 _build/build.py
```

The generated `index.html` files are committed, so the site can be hosted as-is.
Don't edit the generated HTML by hand, because the next build overwrites it.

To add a project, copy one of the entries in `projects.py`, give it a new `slug`,
put its photos in `assets/img/projects/<folder>/`, and rebuild.

## Previewing locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Forms

The contact, get involved and newsletter forms send to a Google Apps Script web app
in the info@hands4unity.org Google account. Each submission is saved as a row in the
"Hands 4 Unity website" Google Sheet (tabs: Messages, Get Involved, Newsletter) and
emailed to info@hands4unity.org.

The script's code is in `google-apps-script/forms/Code.gs`. To change it, paste the new
version into the Sheet's Extensions → Apps Script editor, then Deploy → Manage deployments
→ edit → Version: New version → Deploy. The web app URL stays the same.

The URL is `FORM_ENDPOINT` at the top of `js/main.js`. If it is ever emptied, the forms fall
back to opening the visitor's email app with the message addressed to info@hands4unity.org.

## URLs

Pages keep the same addresses as the old WordPress site
(for example `/about-us/` and `/projects/africa-day-2025/`), so existing links and search results keep working.

## Hosting

Any static host works: GitHub Pages, Netlify, Cloudflare Pages or the current web host.
Upload everything except the `_build/` folder (uploading it is harmless).
For GitHub Pages with the hands4unity.org domain, add a `CNAME` file containing `hands4unity.org`.
