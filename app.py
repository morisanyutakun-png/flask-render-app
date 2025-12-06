from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    context = {}  # ← これ必須！
    if request.method == "POST":
        # --- ペルソナ（必須） ---
        persona_age_select = request.form.get("persona_age")
        persona_age = request.form.get("persona_age_other_input") if persona_age_select == "その他" else persona_age_select

        persona_gender = request.form.get("persona_gender")  # ← これを忘れずに追加

        persona_job_select = request.form.get("persona_job")
        persona_job = request.form.get("persona_job_other_input") if persona_job_select == "その他" else persona_job_select

        persona_hobby_select = request.form.get("persona_hobby")
        persona_hobby = request.form.get("persona_hobby_other_input") if persona_hobby_select == "その他" else persona_hobby_select

        persona_pain_select = request.form.get("persona_pain")
        persona_pain = request.form.get("persona_pain_other_input") if persona_pain_select == "その他" else persona_pain_select

        persona_goal_select = request.form.get("persona_goal")
        persona_goal = request.form.get("persona_goal_other_input") if persona_goal_select == "その他" else persona_goal_select

        # --- 追加項目 ---
        persona_level_select = request.form.get("persona_level")
        persona_level = request.form.get("persona_level_other_input") if persona_level_select == "その他" else persona_level_select

        persona_situation_select = request.form.get("persona_situation")
        persona_situation = request.form.get("persona_situation_other_input") if persona_situation_select == "その他" else persona_situation_select

        persona_failed_select = request.form.get("persona_failed")
        persona_failed = request.form.get("persona_failed_other_input") if persona_failed_select == "その他" else persona_failed_select

        persona_fear_select = request.form.get("persona_fear")
        persona_fear = request.form.get("persona_fear_other_input") if persona_fear_select == "その他" else persona_fear_select

        persona_life_select = request.form.get("persona_life")
        persona_life = request.form.get("persona_life_other_input") if persona_life_select == "その他" else persona_life_select

        # context にまとめる
        context["persona"] = {
            "age": persona_age,
            "gender": persona_gender,
            "job": persona_job,
            "hobby": persona_hobby,
            "pain": persona_pain,
            "goal": persona_goal,
            "level": persona_level,
            "situation": persona_situation,
            "failed": persona_failed,
            "fear": persona_fear,
            "life": persona_life,
        }
        # context["persona"] は既に作成済み
        persona = context["persona"]


        # --- 記事テーマ ---
        article_main = request.form.get("article_main")
        article_type_select = request.form.get("article_type")
        article_type = request.form.get("article_type_other_input") if article_type_select == "その他" else article_type_select

        # --- 記事目的・価値 ---
        article_purpose_select = request.form.get("article_purpose")
        article_purpose = request.form.get("article_purpose_other_input") if article_purpose_select == "その他" else article_purpose_select

        article_value = request.form.get("article_value")  # 任意
        article_cta = request.form.get("article_cta")      # 任意
        
        article_headings_template = request.form.get("article_headings_template")

        # --- トーン・文体 ---
        tone_style_select = request.form.get("tone_style")
        tone_style = request.form.get("tone_style_other_input") if tone_style_select == "その他" else tone_style_select

        tone_keywords = request.form.get("tone_keywords")  # 任意

        # --- 著者情報 ---
        author_viewpoint_select = request.form.get("author_viewpoint")
        author_viewpoint = (
            request.form.get("author_viewpoint_other_input")
            if author_viewpoint_select == "その他"
            else author_viewpoint_select
        )

        author_strengths_select = request.form.get("author_strengths")
        author_strengths = (
            request.form.get("author_strengths_other_input")
            if author_strengths_select == "その他"
            else author_strengths_select
        )
        author_name = request.form.get("author_name", "")
        author_name_include = request.form.get("author_name_include") == "yes"

        # --- 段落情報取得 ---
        article_headings_manual = request.form.getlist("article_headings[]")
        article_headings_auto = request.form.getlist("article_headings_auto[]")
        article_purposes_raw = request.form.getlist("article_purposes[]")
        article_methods_raw = request.form.getlist("article_method_suggest[]")

        # AI/手動切替は手動入力があれば manual、空なら auto
        article_modes = []
        article_headings = []

        for manual, auto in zip(article_headings_manual, article_headings_auto):
            if manual.strip():
                article_headings.append(manual.strip())
                article_modes.append("manual")
            else:
                article_headings.append(auto.strip() if auto else "")
                article_modes.append("auto")

        article_methods = [m.strip() for m in article_methods_raw]
        article_purposes = [p.strip() for p in article_purposes_raw]

        # 長さを揃える
        max_len = max(len(article_headings), len(article_methods), len(article_purposes), len(article_modes))
        while len(article_headings) < max_len: article_headings.append("")
        while len(article_methods) < max_len: article_methods.append("")
        while len(article_purposes) < max_len: article_purposes.append("")
        while len(article_modes) < max_len: article_modes.append("auto")

        # 段落情報構築
        article_sections = []
        for h, p, m, mode in zip(article_headings, article_purposes, article_methods, article_modes):
            if not h and not p and not m:
                continue
            article_sections.append({
                "heading": h,
                "purpose": p,
                "method": m,
                "mode": mode
            })

        context["article_sections"] = article_sections

        # プロンプト向け article_flow（自然文形式）
        if article_sections:
            article_flow_lines = []
            for idx, sec in enumerate(article_sections):
                # Mode が manual の場合は実際の見出しを大見出しとして表示
                if sec["mode"] == "manual" and sec["heading"]:
                    mode_text = sec["heading"]  # 手動入力した見出しを大見出しとして表示
                else:
                    mode_text = "AIでSEO最適生成"  # AI生成の場合の表示

                method_text = sec["method"] or "記事全体設定に従う"
                purpose_text = sec["purpose"] or "-"

                article_flow_lines.append(
                    f"{idx+1}. {sec['heading']}\n"
                    f"   - 段落の役割: {purpose_text}\n"
                    f"   - 段落生成手法: {method_text}\n"
                    f"   - 大見出し: {mode_text}"
                )
            article_flow = "\n".join(article_flow_lines)
        else:
            article_flow = "指定なし"

        context["article_flow"] = article_flow

        # --- 補助情報 ---
        constraint_length = request.form.get("constraint_length", "")
        constraint_forbidden = request.form.get("constraint_forbidden", "")
        constraint_seo = request.form.get("constraint_seo", "").strip()

        search_intent = request.form.get("search_intent", "")
        search_intent_other = request.form.get("search_intent_other", "").strip()
        if search_intent == "other" and search_intent_other:
            search_intent = search_intent_other

        must_include = request.form.get("must_include", "")
        avoid_tone = request.form.get("avoid_tone", "")

        # extra_reference は未定義だとエラーになるので安全に初期化
        extra_reference = request.form.getlist("extra_reference") if "extra_reference" in request.form else []

        # --- 著者情報ブロック ---
        author_info_block = f"""
【著者情報】
- 記事の視点: {author_viewpoint}
- 著者の強み: {author_strengths}
- 著者名: {author_name}
"""
        if not author_name_include:
            author_info_block = "※著者情報は書かないでください" 

        # --- プロンプト生成 ---
        prompt = f"""
あなたは高度なコンテンツクリエイター兼note編集者です。読者に価値あるnote記事を段落ごとに順番に生成してください。生成にあたっては以下の専門手法を意識してください：
・ストーリーテリング法：導入→葛藤→解決→結論の流れ
・PREP法：Point→Reason→Example→Point
・AIDAモデル：Attention→Interest→Desire→Action
・具体例・箇条書き活用：視覚的にわかりやすく、実用的に

{author_info_block}

【ペルソナ（読者像）】
- 年齢: {persona['age']}
- 性別: {persona['gender']}
- 職業: {persona['job']}
- 趣味・興味: {persona['hobby']}
- 読者の悩み: {persona['pain']}
- 読者のゴール: {persona['goal']}
- 知識レベル: {persona['level']}
- 現在の状況: {persona['situation']}
- 過去の失敗経験: {persona['failed']}
- 恐れていること: {persona['fear']}
- 生活スタイル: {persona['life']}

【SEO】
- 想定検索意図: {search_intent}
- SEOキーワード: {constraint_seo}

【記事テーマ】
- 主題: {article_main}
- 記事タイプ: {article_type}

【記事目的・価値】
- 読者に伝えたいこと: {article_purpose}
- 補足（任意）: {article_value}
- CTA: {article_cta}

【トーン・文体】
- スタイル: {tone_style}
- 補足: {tone_keywords}

【記事の大まかな流れ】
{article_flow}

【補助情報】
- 文字量: {constraint_length}
- 禁止ワード: {constraint_forbidden}
- SEOキーワード: {constraint_seo}
- 参考記事・URL: {', '.join(extra_reference) if extra_reference else 'なし'}
- 記事に必ず含めたい要素・具体例: {must_include}
- 記事に避けたい表現・トーン: {avoid_tone}

【生成ルール】
1. まず、タイトルと、【著者情報】のみをもとにした著者紹介や導入の段落を作成してください。
2. 次の段落も自動で続けて生成できます。
3. 生成途中で止めたい場合は「STOP」と入力してください。
4. 次の段落を生成するときは、必ず前の段落の内容を踏まえて文脈を保持してください。
5. 大まかな流れを意識しつつ、より具体的に生成してください。

【段落生成条件】
0. 文字総量指定は{constraint_length}でありますが、1000文字ほど多めに見積もってください。
1. 各段落は本文の総文字量が{constraint_length}であることを考慮して分割し、各々の段落をかなり具体的に膨らませて書いててください。
2. メイントピックの段落は、全体の3割ほどのボリューミーでより具体的に書くこと。
3. 箇条書きや太字を頻繁に使うこと。
4. 改行を頻繁に行い、空白行を2文あたりに1度以上入れること。
5. 各段落は起承転結を意識して論理的かつ具体的に書くこと。
6. 導入（読者の共感を引く部分）から始めてください。
7. 既に生成した段落がある場合は、その内容を渡して文脈を保持しつつ次の段落を生成してください。
8. 段落ごとにCTAや読者への気づきが自然に含まれるようにしてください。CTAの直接的な表現はしないように。
9. 禁止ワードを絶対に使用しないでください。
10. 各段落を生成したら、その段落だけを出力してください。次の段落は別で生成してください。
11. 段落生成後、コピーして順番に貼り付けるだけで記事完成できる設計にしてください。
"""
        context["prompt"] = prompt  # ← 必須
        return render_template("result.html", **context)

    # GET のときは空の context で index.html
    return render_template("index.html", **context)


if __name__ == "__main__":
    # Render 用に外部アクセス & ポート指定
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)  # 外部アクセス可能に
