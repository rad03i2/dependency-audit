# Security Policy

## Supported version

The current `main` branch is supported.

## Security model

Dependency Audit is designed for local static inspection. It reads supported text manifests and does not install dependencies, execute audited project code, or make network requests. JSON and TOML parsing use Python's standard library.

The findings are dependency-hygiene and reproducibility signals. They are **not vulnerability findings**. A clean report does not prove that dependencies are safe.

## Reporting a vulnerability

Please report security issues privately through GitHub's security reporting facilities when available. Do not publish credentials, private manifests, access tokens, or exploitable details in a public issue.

## سياسة الأمان

الأداة تفحص ملفات الاعتماديات محليًا ولا تثبت الحزم ولا تشغل كود المشروع ولا تتصل بالشبكة. نتائجها مؤشرات على جودة تعريف الاعتماديات وقابلية إعادة البناء وليست إثباتًا لوجود أو غياب ثغرات أمنية. لا تنشر أسرارًا أو بيانات اعتماد ضمن بلاغ عام.
