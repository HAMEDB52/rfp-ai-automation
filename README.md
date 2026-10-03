# rfp-ai-automation — أتمتة إعداد طلبات العروض وتقييمها

خط عمل كامل يأخذ **موجز العميل** وينتج **مستند طلب عرض (RFP)**، ثم يقرأ **عروض المورّدين** ويقيّمها مقابل المتطلبات، وينتج **تقريراً مُعلَّلاً** بالدرجات والأدلة النصية.

[![tests](https://img.shields.io/badge/tests-18%20passed-brightgreen)](#الاختبارات)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](#التثبيت)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## المشكلة

إعداد طلب عرض وتقييم العروض الواردة عمل يدوي بطيء ومتفاوت الأحكام: كل مُقيِّم يقرأ العروض بترتيب مختلف، والدرجة النهائية غالباً بلا أثر يوضّح سبب منحها. هذا المشروع يحوّل العملية إلى خط قابل لإعادة الإنتاج والتدقيق.

## ما الذي ينفّذه

```
موجز العميل (JSON)
      │
      ▼
 [generate_rfp] ──► مستند RFP كامل الأقسام (Markdown)
      │
      ▼
 [load_proposals] ──► قراءة عروض المورّدين (txt / md / pdf)
      │
      ├── لا توجد عروض ──► [no_proposals] ──► إنهاء
      ▼
 [score] ──► تغطية كل متطلب + دليل نصي + عقوبة المتطلبات الإلزامية المفقودة
      │
      ▼
 [report] ──► evaluation.md + evaluation.json + evaluation.pdf (اختياري)
```

- **سير عمل كرسم بياني للحالة**: عقد وحوافّ شرطية، على نمط LangGraph، لكنه **منفَّذ من الصفر** (`graph.py`) ليبقى المشروع خفيفاً وقابلاً للاختبار بالكامل. كل تشغيل يُرجع `trace` بالمسار المنفَّذ فعلاً.
- **تقييم قابل للتفسير**: لكل متطلب نسبة تغطية ودرجة والفقرة التي بُنيت عليها — لا صندوق أسود.
- **معالجة عربية صحيحة**: تطبيع وتجذير خفيف، فـ«المراسلات» تطابق «مراسلات» و«الإجازةُ» تطابق «الاجازه».
- **كشف التحفّظات**: عبارات مثل «خارج النطاق» و«مقابل رسوم إضافية» تخفض الدرجة وتُسجَّل كملاحظة.
- **PDF عربي سليم**: التصدير عبر Chromium بدل مكتبات PDF التي لا تشكّل الحروف العربية.

## التثبيت

```bash
git clone https://github.com/<اسم-المستخدم>/rfp-ai-automation.git
cd rfp-ai-automation
pip install -r requirements-dev.txt
```

## التشغيل

```bash
python -m rfp_automation.cli \
    --brief data/brief.json \
    --proposals data/proposals \
    --out out --pdf
```

مخرجات التشغيل على البيانات المرفقة:

```
المسار المنفَّذ: generate_rfp ← load_proposals ← score ← report
  شركة_الأفق_التقني             97.19
  شركة_نماء_للحلول              84.91
  مؤسسة_بيانات_الشرق            31.14  (ينقصه: R5)
```

المورّد الثالث عرض تشغيلاً على السحابة العامة بينما المتطلب **R5** يفرض النشر داخل مركز بيانات الجهة — فأُسقطت درجته وسُجِّل سبب الإسقاط.

### كمكتبة

```python
from rfp_automation import ProjectBrief, build_rfp, score_proposal, rank

brief = ProjectBrief.from_json("data/brief.json")
print(build_rfp(brief).to_markdown())

cards = [score_proposal(brief, "المورّد أ", text_a),
         score_proposal(brief, "المورّد ب", text_b)]
for card in rank(cards):
    print(card.vendor, card.total, card.missing_mandatory)
```

## صيغة موجز المشروع

```json
{
  "project_name": "منصة معالجة المراسلات",
  "organization": "الإدارة العامة لتقنية المعلومات",
  "summary": "...",
  "budget_sar": 850000,
  "duration_weeks": 20,
  "requirements": [
    { "id": "R1", "title": "...", "description": "...",
      "category": "فني", "weight": 3, "mandatory": true }
  ]
}
```

## كيف تُحتسب الدرجة

| الخطوة | القاعدة |
|---|---|
| التغطية | نسبة مفاتيح المتطلب (بعد التطبيع والتجذير) الظاهرة في العرض — على مستوى المستند أو أفضل فقرة |
| مكافأة الالتزام | وجود صيغة التزام صريحة («نلتزم»، «نضمن») مع تغطية ≥ 50% ترفع الدرجة 0.1 |
| عقوبة التحفّظ | «خارج النطاق»، «مقابل رسوم إضافية» تضرب الدرجة في 0.5 |
| الدرجة الكلية | متوسط موزون بأوزان المتطلبات |
| عقوبة الإلزامي | إغفال أي متطلب إلزامي (تغطية < 34%) يضرب الإجمالي في 0.6 ويُسجَّل |

## الوحدات

| الملف | المسؤولية |
|---|---|
| `schema.py` | نماذج البيانات: المتطلب، الموجز، المستند، بطاقة الدرجات |
| `generator.py` | بناء أقسام مستند RFP من الموجز |
| `parser.py` | قراءة العروض من PDF/نص وتقطيعها إلى أقسام |
| `arabic_text.py` | تطبيع، تجذير خفيف، حساب التغطية |
| `scoring.py` | منطق الدرجات والأدلة والعقوبات |
| `graph.py` | محرك سير العمل (عقد + حوافّ شرطية + تتبّع) |
| `workflow.py` | ربط العقد في خط العمل الكامل |
| `report.py` | مخرجات JSON و Markdown و PDF |

## الاختبارات

```bash
python -m pytest -q      # 18 اختباراً
```

تغطي: محرّك الرسم البياني (مسار خطي، تفرّع شرطي، كشف الحلقات، عقدة مفقودة) · التطبيع العربي · اكتمال أقسام المستند · ترتيب العروض · رصد المتطلب الإلزامي المفقود · أثر التحفّظ على الدرجة · الخط الكامل بفرعيه.

## الحدود المعروفة

- المطابقة **معجمية**: عرض يصف المتطلب بمرادفات لا تظهر في نصه قد تُحتسب تغطيته أقل من الواقع. المعالجة: تمرير مولّد لغوي أو متجهات دلالية في `scoring.py`.
- قراءة PDF تعتمد `pdfplumber` ولا تتعامل مع الملفات **الممسوحة ضوئياً** (تحتاج OCR أولاً).
- الدرجة أداة ترشيح وترتيب تسبق المراجعة البشرية، لا بديل عنها.

## الترخيص

MIT — انظر [LICENSE](LICENSE).

---

## English summary

**rfp-ai-automation** turns a client brief into a complete RFP document, then parses vendor proposals (txt/md/pdf) and scores them against each requirement with an interpretable rubric: per-requirement coverage, supporting evidence, commitment bonus, hedging penalty, and a hard penalty for missing mandatory requirements. The pipeline is a from-scratch state-graph engine (LangGraph-style: nodes, conditional edges, execution trace) with no heavy dependencies. Arabic text is normalized and lightly stemmed so morphological variants match. Outputs are Markdown, structured JSON, and an optional Arabic-correct PDF rendered through Chromium. 18 tests cover the graph engine, scoring rules, and both workflow branches.
