from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
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
        author_info_include = request.form.get("author_info_include")
        author_family_select = request.form.get("author_family")
        author_family = request.form.get("author_family_other_input") if author_family_select == "その他" else author_family_select
        author_strengths_select = request.form.get("author_strengths")
        author_strengths = request.form.get("author_strengths_other_input") if author_strengths_select == "その他" else author_strengths_select
        # フォームから取得
        author_name = request.form.get("author_name", "")
        author_name_include = request.form.get("author_name_include") == "yes"

        # プロンプトに条件付きで追加
        prompt = "記事生成のプロンプト本文ここから"
        if author_name_include and author_name:
            prompt += f"\n著者名: {author_name}\n"

        # --- 段落見出し ---
        article_headings = request.form.getlist("article_headings[]")  # 無限追加対応

        # --- 補助情報 ---
        constraint_length = request.form.get("constraint_length")
        constraint_forbidden = request.form.get("constraint_forbidden")
        constraint_seo = request.form.get("constraint_seo")
        extra_reference = request.form.getlist("extra_reference[]")  # 複数URL対応
        structure_hint = request.form.get("structure_hint")  # 任意

        # --- 任意補助情報 ---
        must_include = request.form.get("must_include")
        avoid_tone = request.form.get("avoid_tone")

        # --- プロンプト生成 ---
        prompt = f"""
あなたは高度なコンテンツクリエイター兼note編集者です。
note記事として読者に価値ある記事を**段落ごとに順番に生成**してください。

【ペルソナ】
- 年齢: {persona_age}
- 性別: {persona_gender}
- 職業: {persona_job}
- 趣味・興味: {persona_hobby}
- 読者の悩み: {persona_pain}
- 読者のゴール: {persona_goal}

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

【著者情報（記事に含める場合）】
- 記事に含める: {'はい' if author_info_include else 'いいえ'}
- 家族構成: {author_family}
- アピールポイント・経験: {author_strengths}
- 著者名: {author_name}

【記事の大まかな流れ】
- 全体の流れ: {article_headings_template if article_headings_template else "指定なし"}

【補助情報】
- 文字量: {constraint_length}
- 禁止ワード: {constraint_forbidden}
- SEOキーワード: {constraint_seo}
- 参考記事・URL: {', '.join(extra_reference) if extra_reference else 'なし'}
- 記事に必ず含めたい要素・具体例: {must_include}
- 記事に避けたい表現・トーン: {avoid_tone}

【生成ルール】
1. まず、タイトルと、【著者情報（記事に含める場合）】のみをもとにした著者紹介や導入の段落を作成してください。
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
8. 段落ごとにCTAや読者への気づきが自然に含まれるようにしてください。
9. 禁止ワードを絶対に使用しないでください。
10. 各段落を生成したら、その段落だけを出力してください。次の段落は別で生成してください。
11. 段落生成後、コピーして順番に貼り付けるだけで記事完成できる設計にしてください。


【出力フォーマット例】
# 大見出し
本文の内容がここに入ります。  

---

# 次の大見出し
次の段落の内容をここに書きます。  
"""
        return render_template("result.html", prompt=prompt)

    return render_template("index.html")


from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# メインブロックはそのままサーバー起動
if __name__ == "__main__":
    # debug=Trueで開発モード起動
    app.run(debug=True)
