# Dependency Audit

A small, offline-first dependency manifest auditor for Python and Node.js projects. It helps developers catch reproducibility and dependency-hygiene problems before they reach CI or a release.

> **Scope:** Dependency Audit performs static local checks. It does **not** query vulnerability databases and must not be presented as a CVE/security-vulnerability scanner.

## Why it exists

Dependency manifests often accumulate unpinned packages, broad ranges, direct URLs, conflicting declarations, or missing lockfiles. These are easy to miss in review and can make builds less reproducible. Dependency Audit provides a deterministic, network-free check suitable for laptops and CI.

## Key features

- Reads `requirements.txt`, PEP 621 dependencies in `pyproject.toml`, and Node.js `package.json`.
- Checks unpinned/unbounded dependencies, ranges, direct/non-registry sources, conflicting declarations, and missing Node lockfiles.
- Never installs packages, executes project code, or contacts a registry.
- Human-readable and JSON reports.
- Configurable CI failure threshold: `info`, `warning`, `error`, or `never`.
- Reusable Python API.
- No runtime third-party dependencies.

## Requirements

Python 3.10 or newer.

## Installation

```bash
python -m pip install -e .
```

For development/testing:

```bash
python -m pip install pytest
pytest
```

## Usage

Audit the current project:

```bash
dependency-audit .
```

Audit another directory and produce JSON:

```bash
dependency-audit ../my-project --json
```

Fail CI on warnings or errors:

```bash
dependency-audit . --fail-on warning
```

Only fail on errors (default):

```bash
dependency-audit . --fail-on error
```

Never fail, useful for advisory reports:

```bash
dependency-audit . --fail-on never
```

You can also run it without the installed console script:

```bash
python -m dependency_audit .
```

### Exit codes

- `0`: audit completed and no finding reached the configured failure threshold.
- `1`: one or more findings reached the threshold.
- `2`: invalid path or operational input error.

## Python API

```python
from dependency_audit import audit

report = audit(".")
print(report.dependencies)
for finding in report.findings:
    print(finding.severity, finding.code, finding.package)
```

## What the checks mean

| Code | Meaning |
|---|---|
| `UNPINNED` | Python dependency has no explicit version constraint |
| `UNBOUNDED` | Node dependency uses `*`, `latest`, or an empty version |
| `RANGE` | A version range is used; a lock/constraints file improves reproducibility |
| `DIRECT_URL` | Python dependency appears to use a direct URL |
| `NON_REGISTRY` | Node dependency points to Git/file/URL source |
| `CONFLICTING_SPEC` | Same normalized package has different declarations across supported manifests |
| `NO_LOCKFILE` | Node project has no recognized npm/Yarn/pnpm lockfile |
| `INVALID_MANIFEST` | A supported manifest could not be parsed |
| `NO_MANIFEST` | No supported manifest was found |

## Configuration

The tool intentionally has no configuration file in v1.0. Its behavior is controlled through CLI flags so CI behavior remains explicit and easy to review.

## Project structure

```text
src/dependency_audit/
  __init__.py     Public API
  __main__.py     python -m entry point
  core.py         Parsers and audit engine
  cli.py          Command-line interface
tests/             Automated tests
.github/workflows/ CI test matrix
```

## Testing

```bash
python -m pip install pytest
pytest -q
python -m compileall -q src tests
```

CI runs the test suite on Linux, Windows, and macOS across supported Python versions.

## Preview / screenshots

This is a terminal-first tool. A useful repository screenshot can show `dependency-audit .` beside a sample project manifest. No GUI is implemented or claimed.

## Security & privacy

All analysis is local. The tool does not send manifest contents anywhere and does not execute dependency or project code. Treat warnings about direct/non-registry dependencies as review prompts, not proof of malicious behavior. See [SECURITY.md](SECURITY.md).

## Limitations

- This is **not** a vulnerability/CVE scanner and does not query OSV, PyPI, npm, GitHub Advisories, or any remote database.
- Supported manifests are intentionally limited to `requirements.txt`, PEP 621 `pyproject.toml`, and `package.json`.
- It does not fully implement every requirements-file directive or every package-manager version grammar.
- It does not validate whether package versions actually exist.
- A pinned dependency can still be vulnerable or malicious; pinning is about reproducibility, not trust.

## Optional roadmap

Future versions may add opt-in parsers for more lock/manifests and an explicitly opt-in vulnerability-data provider. These features are not currently implemented.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

## Author

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# تدقيق الاعتماديات — Dependency Audit

أداة محلية صغيرة لتدقيق ملفات اعتماديات مشاريع Python وNode.js دون الحاجة إلى الإنترنت. هدفها كشف مشكلات قابلية إعادة البناء ونظافة تعريف الاعتماديات قبل وصول المشروع إلى CI أو الإصدار.

> **النطاق:** الأداة تنفذ فحوصًا ثابتة محلية فقط، ولا تستعلم عن قواعد بيانات الثغرات، ولذلك فهي **ليست** ماسح CVE أو بديلًا عن أدوات فحص الثغرات الأمنية.

## لماذا توجد هذه الأداة؟

مع مرور الوقت قد تحتوي ملفات المشروع على حزم بلا قيود إصدار، أو نطاقات واسعة، أو روابط مباشرة، أو تعريفات متعارضة، أو قد يفتقد مشروع Node إلى lockfile. هذه الأمور قد تجعل البناء أقل قابلية للتكرار. توفر الأداة فحصًا ثابتًا وواضحًا يعمل محليًا وفي CI.

## أهم الميزات

- قراءة `requirements.txt` واعتماديات PEP 621 في `pyproject.toml` و`package.json`.
- كشف الاعتماديات غير المقيدة، ونطاقات الإصدارات، والمصادر المباشرة وغير القياسية، والتعريفات المتعارضة، وغياب lockfile في Node.
- لا تثبت أي حزمة ولا تشغل كود المشروع ولا تتصل بمخازن الحزم.
- تقارير نصية أو JSON.
- حد فشل قابل للضبط لاستخدامها في CI.
- Python API قابلة لإعادة الاستخدام.
- لا توجد اعتماديات تشغيل خارج مكتبة Python القياسية.

## المتطلبات والتثبيت

Python 3.10 أو أحدث:

```bash
python -m pip install -e .
```

للتطوير والاختبارات:

```bash
python -m pip install pytest
pytest
```

## الاستخدام

فحص المجلد الحالي:

```bash
dependency-audit .
```

تقرير JSON:

```bash
dependency-audit . --json
```

جعل التحذيرات سببًا لفشل CI:

```bash
dependency-audit . --fail-on warning
```

ويمكن التشغيل أيضًا هكذا:

```bash
python -m dependency_audit .
```

رموز الخروج: `0` نجاح ضمن الحد المحدد، و`1` عند وصول نتيجة إلى حد الفشل، و`2` لخطأ تشغيلي مثل مسار غير صالح.

## Python API

```python
from dependency_audit import audit

report = audit(".")
for finding in report.findings:
    print(finding.severity, finding.code, finding.package)
```

## الإعداد

لا يوجد ملف إعداد في الإصدار 1.0 عمدًا. يتم التحكم بالسلوك عبر خيارات CLI حتى تكون قواعد CI صريحة وسهلة المراجعة.

## بنية المشروع

الكود موجود في `src/dependency_audit`، والاختبارات في `tests`، وGitHub Actions في `.github/workflows`.

## الاختبارات

```bash
python -m pip install pytest
pytest -q
python -m compileall -q src tests
```

## المعاينة

الأداة موجهة للطرفية ولا تحتوي واجهة رسومية. يمكن استخدام لقطة شاشة لأمر `dependency-audit .` مع ملف اعتماديات تجريبي عند عرض المشروع.

## الخصوصية والأمان

كل التحليل محلي. لا ترسل الأداة محتوى الملفات إلى أي جهة ولا تنفذ كود المشروع أو الاعتماديات. التحذير من مصدر مباشر هو إشارة للمراجعة وليس دليلًا على أن المصدر ضار. راجع [SECURITY.md](SECURITY.md).

## القيود

- ليست ماسح ثغرات ولا تتصل بقواعد OSV أو PyPI أو npm أو GitHub Advisories.
- الملفات المدعومة حاليًا هي `requirements.txt` وPEP 621 `pyproject.toml` و`package.json`.
- لا تنفذ كامل قواعد كل صيغة أو مدير حزم.
- لا تتحقق من وجود الإصدار فعليًا على الإنترنت.
- تثبيت إصدار محدد لا يعني أن الحزمة آمنة؛ التثبيت يتعلق بقابلية إعادة البناء.

## تطوير اختياري مستقبلًا

يمكن لاحقًا إضافة صيغ أخرى أو مزود اختياري لبيانات الثغرات، لكن هذه الميزات غير موجودة حاليًا ولا يدعي المشروع دعمها.

## المساهمة والترخيص

راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص وفق MIT؛ راجع [LICENSE](LICENSE).

## المؤلف

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
