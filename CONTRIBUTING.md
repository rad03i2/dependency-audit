# Contributing

Thanks for improving Dependency Audit.

1. Use Python 3.10+ and create a virtual environment.
2. Install the project editable and install pytest: `python -m pip install -e . pytest`.
3. Keep runtime dependencies at zero unless a strong, documented reason requires otherwise.
4. Add tests for every parser or rule change.
5. Run `pytest -q` and `python -m compileall -q src tests` before submitting changes.
6. Keep checks deterministic and offline by default. Never execute code from the project being audited.
7. Document behavior honestly; do not describe this tool as a vulnerability scanner.

Please keep commits focused and avoid including credentials, generated environments, caches, or unrelated files.

## المساهمة

استخدم Python 3.10 أو أحدث، وأضف اختبارات لكل تغيير في المحللات أو القواعد، وشغّل الاختبارات وفحص compile قبل إرسال التغيير. حافظ على كون الفحص محليًا وحتميًا، ولا تنفذ كود المشروع الذي يتم تدقيقه، ولا تضف أسرارًا أو ملفات مولدة إلى المستودع.
