# 🚀 HTML to PDF Carousel Converter - دليل الاستخدام

محول متقدم لتحويل ملفات HTML التعليمية إلى ملفات PDF تفاعلية مع تنقل carousel.

## 📋 المميزات

- ✅ تحويل كل card في HTML إلى صفحة منفصلة في PDF
- 🔗 روابط تنقل تفاعلية (carousel navigation)
- 📖 فهرس محتويات تلقائي
- 💻 دعم عرض الكود مع تنسيق مناسب
- 🎨 تصميم جميل مع دعم النصوص العربية
- 📱 تصميم متجاوب وقابل للطباعة

## 📦 التثبيت

### المتطلبات الأساسية

```bash
# تثبيت المكتبات المطلوبة
pip install reportlab beautifulsoup4
```

أو استخدم ملف requirements.txt:

```bash
pip install -r requirements.txt
```

## 🎯 طرق الاستخدام

### 1. تحويل ملف واحد

```bash
# الطريقة الأساسية
python carousel_pdf_converter.py 'path/to/file.html'

# تحديد اسم الملف الناتج
python carousel_pdf_converter.py 'path/to/file.html' 'output.pdf'

# مثال عملي
python carousel_pdf_converter.py 'explain/4.1 reflection_pattern_explained.html'
```

### 2. تحويل مجلد كامل (Batch Conversion)

```bash
# تحويل كل ملفات HTML في مجلد
python carousel_pdf_converter.py --batch explain

# تحديد مجلد الإخراج
python carousel_pdf_converter.py --batch explain pdfs/

# مثال مع مجلدات مختلفة
python carousel_pdf_converter.py --batch input_folder output_folder
```

### 3. اختبار المحول

```bash
# تشغيل اختبار سريع
python carousel_pdf_converter.py --test
```

### 4. عرض المساعدة

```bash
# إظهار تعليمات الاستخدام
python carousel_pdf_converter.py
```

## 🔧 أمثلة عملية

### تحويل ملف واحد مع مسار كامل

```bash
python carousel_pdf_converter.py 'explain/4.1 reflection_pattern_explained.html' 'pdfs/reflection_pattern.pdf'
```

### تحويل جميع الملفات في مجلد explain

```bash
python carousel_pdf_converter.py --batch explain explain/pdfs
```

### تحويل مع استخدام Virtual Environment

```bash
# إذا كنت تستخدم virtual environment
"/path/to/venv/bin/python" carousel_pdf_converter.py 'file.html'

# مثال عملي للمشروع
"/Users/I550080/ML study/agentic-ai-for-developers-concepts-and-applications-for-enterprises-3913172/.venv/bin/python" carousel_pdf_converter.py 'explain/4.1 reflection_pattern_explained.html'
```

## 📁 بنية الملفات

```
project/
├── carousel_pdf_converter.py    # المحول الرئيسي
├── simple_html_converter.py     # محلل HTML بسيط للاختبار
├── requirements.txt             # المكتبات المطلوبة
├── explain/                     # ملفات HTML المراد تحويلها
│   ├── 4.1 reflection_pattern_explained.html
│   ├── 4.2 router_pattern_explained.html
│   └── ...
└── pdfs/                       # مجلد الإخراج (يتم إنشاؤه تلقائياً)
    ├── reflection_pattern_carousel.pdf
    └── ...
```

## 🎨 هيكل PDF الناتج

### صفحة الفهرس
- العنوان الرئيسي
- قائمة بجميع الـ cards مع أرقام الصفحات
- خطوط منقطة للربط بين العناوين والصفحات

### صفحات الـ Cards
- عنوان الـ card
- محتوى نصي منسق
- كود مع خلفية رمادية (إذا وُجد)
- شريط تنقل في الأسفل

### شريط التنقل
- زر "السابق" و"التالي"
- رقم الصفحة الحالية
- رابط للعودة للفهرس

## ⚙️ إعدادات التخصيص

يمكنك تعديل الإعدادات في الكود:

```python
# في فئة CarouselPDFConverter
def __init__(self, page_size: Tuple = A4):
    self.page_size = page_size        # حجم الصفحة
    self.margin = 2 * cm              # الهوامش
    
    # الألوان
    self.primary_color = Color(0.17, 0.24, 0.31)    # لون أساسي
    self.secondary_color = Color(0.90, 0.30, 0.24)  # لون ثانوي
```

## 🔍 تحليل HTML قبل التحويل

للتأكد من بنية HTML قبل التحويل:

```bash
# تحليل ملف واحد
python simple_html_converter.py 'explain/4.1 reflection_pattern_explained.html'

# تحليل مجلد كامل
python simple_html_converter.py --analyze explain
```

## 📊 مثال على الناتج

```
🔄 Converting: explain/4.1 reflection_pattern_explained.html
📄 Output: 4.1 reflection_pattern_explained_carousel.pdf
✅ Successfully created PDF: 4.1 reflection_pattern_explained_carousel.pdf
✅ Conversion successful!
📊 File size: 12.9 KB
```

## 🐛 استكشاف الأخطاء

### خطأ "Module not found"
```bash
# تأكد من تثبيت المكتبات
pip install reportlab beautifulsoup4
```

### خطأ "File not found"
```bash
# تأكد من المسار الصحيح
ls -la explain/  # للتحقق من وجود الملفات
```

### مشاكل التشفير
```bash
# تأكد من أن الملفات بتشفير UTF-8
file -I explain/*.html
```

## 📈 الأداء

- **ملف واحد**: ~1-3 ثواني حسب حجم المحتوى
- **معالجة مجموعية**: ~2-5 ثوانِ لكل ملف
- **حجم PDF**: عادة 10-50 KB لكل ملف

## 🤝 المساهمة

لتحسين المحول:

1. Fork المشروع
2. أنشئ branch جديد (`git checkout -b feature/improvement`)
3. اعمل Commit للتغييرات (`git commit -am 'Add improvement'`)
4. Push للـ branch (`git push origin feature/improvement`)
5. افتح Pull Request

## 📝 ملاحظات مهمة

- ⚠️ تأكد من أن ملفات HTML تحتوي على `<div class="card">` للكشف الصحيح
- 🎯 النصوص العربية مدعومة بالكامل
- 💾 يتم إنشاء مجلدات الإخراج تلقائياً
- 🔄 في حالة وجود ملف بنفس الاسم، سيتم استبداله

## 📞 الدعم

في حالة وجود مشاكل:
1. تأكد من إصدار Python (3.7+)
2. تحقق من تثبيت المكتبات
3. راجع رسائل الخطأ في Terminal
4. استخدم `--test` للتحقق من عمل المحول
