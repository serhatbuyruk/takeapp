# partner_courier_fields Development Skill

Use this project note when working on `partner_courier_fields` or a new addon that extends it.

## Environment

- Odoo version: 16.0 only.
- Addons root: `/odoo/odoo16/odoo-custom-addons`
- Current addon: `/odoo/odoo16/odoo-custom-addons/partner_courier_fields`
- Runtime config: `/etc/odoo16-ktsite.conf`
- Database: `ktsite`
- Custom addons path is included in the runtime config.

## Existing Addon Shape

- Technical module name: `partner_courier_fields`
- Manifest depends on `base` and `contacts`.
- The addon extends `res.partner` in `models/res_partner.py`.
- The addon inherits partner form and tree views in `views/res_partner_view.xml`.
- It adds courier identity, invoice, payment, bank, work area, login, debt, archive, equipment, and attachment fields.
- Courier first and last name onchange updates `res.partner.name`.
- `debt_info` is a `fields.Monetary` using `currency_id`, defaulting to `base.TRY`.

## Development Rules

- Target Odoo 16 APIs and XML conventions only.
- Prefer extending this addon through a new small addon when adding extra behavior, unless the requested change is clearly a fix inside this addon.
- New dependent addons should include `partner_courier_fields` in `depends`.
- Keep `res.partner` extensions scoped and avoid changing unrelated standard partner behavior.
- Use stable XML inheritance anchors such as field names, page names, and official external IDs.
- Do not store environment-specific secrets in code, manifests, XML, or data files.
- Be careful with personal data fields such as T.C. numbers, IBAN, passwords, and attachments.
- Avoid exposing sensitive courier fields in portal/public controllers or permissive record rules.
- Prefer `groups` or access checks for any new sensitive menus, reports, buttons, exports, or server actions.

## Odoo 16 Architecture Defaults

- Read nearby code and official Odoo 16 patterns before editing.
- Keep modules small, explicit, and upgrade-safe.
- Use `_inherit` without `_name` when extending existing Odoo models such as `res.partner`.
- Use `_name` only for a new business object with its own lifecycle, access rights, menus, reports, or records.
- Add `_description` on every new persistent model.
- Keep business logic in models; controllers should validate input and delegate to model methods.
- Keep UI-only behavior in `@api.onchange`; enforce real business rules with constraints, SQL constraints, or `create`/`write` overrides.
- Keep compute methods batch-safe, assign every record, and use complete `@api.depends(...)`.
- Use `store=True` only when search, grouping, reporting, or performance requires it.
- Use `Many2one(ondelete=...)` deliberately for relational integrity.
- Use `selection_add` when extending official selections, with Odoo 16-compatible `ondelete` fallback when required.
- Avoid direct SQL unless there is a proven performance reason; when used, handle flush/cache invalidation carefully.
- Use `sudo()` only in narrow, justified boundaries and re-check ownership, company, partner, website, token, or group constraints before returning data.

## Addon Layout Rules

- Keep only directories that are needed.
- Typical layout:

```text
module_name/
├── __init__.py
├── __manifest__.py
├── models/
├── security/
├── views/
├── data/
├── demo/
├── controllers/
├── static/src/
├── report/
└── tests/
```

- `__init__.py` should import only existing packages/modules.
- Use stable import order: `models`, `controllers`, `wizard`, then specialized packages.
- Put one coherent business area per Python model file.
- Put inherited views under `views/` and name files by the model or feature they modify.
- Add `security/ir.model.access.csv` for every new persistent model.
- Do not add empty folders.

## Manifest Rules

- Use Odoo 16 versioning, for example `16.0.1.0.0`.
- Add every directly referenced module to `depends`; do not rely on transitive dependencies.
- Keep dependencies minimal but explicit.
- Preferred manifest data order:

```python
'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'data/sequence.xml',
    'views/model_views.xml',
    'views/action_views.xml',
    'views/menu_views.xml',
    'report/report_views.xml',
]
```

- Load menus after actions and parent menus exist.
- Use `demo` only for sample records, never required behavior.
- Use `assets` in the manifest for Odoo 16 backend/frontend assets.
- Use `noupdate="1"` only for records administrators may customize, such as cron jobs, mail templates, or default configuration.

## View and XML Rules

- Use stable inheritance targets: field names, page names, group names, button names, and official external IDs.
- Avoid fragile xpath expressions based on positional indexes, translated strings, CSS classes only, or deep tree paths.
- For this addon, avoid repeating the current fragile pattern `//tree/field[1]` in new code.
- Prefer adding a new inherited view with a clear XML ID instead of modifying unrelated view blocks.
- Keep form pages/groups compact and meaningful; do not hide standard fields unless the business request is explicit.
- If a field contains sensitive information, consider `groups` on the field in the view and on the model field when appropriate.

## Security and Data Sensitivity

- Treat T.C. numbers, IBAN, passwords, debt data, and courier attachments as sensitive.
- Do not expose these fields in public/portal routes, website templates, broad exports, or unaudited automated emails.
- If adding new models, define access rules before views/actions/menus.
- Add record rules when users must only see their own company, region, manager, or assigned courier records.
- Avoid storing real passwords as plain `fields.Char`; prefer integration tokens, encrypted external systems, or access-controlled configuration if a future feature needs credentials.

## Upgrade and Runtime Workflow

- Validate syntax and structure before touching the live database.
- For existing modules, prefer `-u module_name --stop-after-init` against `ktsite` using `/etc/odoo16-ktsite.conf`.
- For new modules, install with `-i module_name --stop-after-init` after checking manifest, imports, XML IDs, and security.
- Watch `/var/log/odoo/odoo16-ktsite.log` when an install or upgrade fails.
- Do not rename fields, models, XML IDs, or selection keys in live modules without a migration plan.
- Adding a required field on existing records requires a default, compute, or data preparation.
- Removing XML files from the manifest does not remove database records; plan cleanup explicitly if needed.

## Validation Commands

Run these from `/odoo/odoo16/odoo-custom-addons` when relevant:

```bash
python3 /root/.codex/skills/odoo16-development/scripts/validate_manifest.py partner_courier_fields
python3 /root/.codex/skills/odoo16-development/scripts/check_xml_ids.py partner_courier_fields
python3 /root/.codex/skills/odoo16-development/scripts/check_security_csv.py partner_courier_fields
python3 /root/.codex/skills/odoo16-development/scripts/find_unsafe_xpath.py partner_courier_fields
```

For install or upgrade checks on the configured database:

```bash
odoo-bin -c /etc/odoo16-ktsite.conf -d ktsite -u partner_courier_fields --stop-after-init
```

If `odoo-bin` is not on PATH, locate the Odoo 16 server entry point used by this installation before running the upgrade.

## Current Extension Starting Point

When creating the next module with extra features:

- Scaffold a new addon beside this one under `/odoo/odoo16/odoo-custom-addons`.
- Add `partner_courier_fields` to the new addon's manifest dependencies.
- Put model extensions under `models/`.
- Put inherited views under `views/`.
- Add security files only if the new module creates new models, groups, record rules, server actions, or protected menus.
- Add tests when introducing compute logic, constraints, scheduled actions, controllers, or non-trivial state transitions.
