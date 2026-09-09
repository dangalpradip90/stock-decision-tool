
import math
import re
import subprocess
from io import BytesIO
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from urllib.parse import quote_plus, urljoin

st.set_page_config(page_title="Stock Decision Tool", layout="wide")

LANGUAGES = {
    "日本語": {
        "code": "ja",
        "title": "株式判断ツール",
        "tool_mode": "分析メニュー",
        "stock_analysis": "上場株式・円相場",
        "ipo_analysis": "国内IPO判断",
        "caption": "株価・企業指標とUSD/JPYを取得し、企業・相場・円の方向を合わせて判断します。最終判断は自分で行うための補助ツールです。",
        "weights_header": "判断ウェイト",
        "investment_style": "投資スタイル",
        "long_stable": "長期・安定重視",
        "growth": "成長重視",
        "short_entry": "短期エントリー重視",
        "item": "項目",
        "weight": "ウェイト",
        "sidebar_info": "決算直前は自動で減点します。ニュースは見出しベースの簡易判定です。",
        "ticker": "ティッカー",
        "ticker_help": "米国株: NVDA / 日本株: 6501.T の形式",
        "analyze": "分析する",
        "scan": "お気に入り一括スキャン",
        "loading": "データ取得中...",
        "current_price": "現在値",
        "total_score": "総合スコア",
        "decision": "判断",
        "next_earnings": "次回決算",
        "unavailable": "取得不可",
        "buy_zones": "分割買いゾーン（自動計算）",
        "buy1": "1回目",
        "buy2": "2回目",
        "buy3": "強い押し目",
        "buy_caption": "価格が下がるたびに目標を後付けで下げないよう、分析時点で3段階を固定表示します。",
        "score_breakdown": "スコア内訳",
        "score": "スコア",
        "fundamental": "ファンダメンタル",
        "valuation": "バリュエーション",
        "technical": "テクニカル",
        "news": "ニュース",
        "event": "イベント",
        "risk_settings": "リスク管理設定",
        "capital_label": "利用可能資金（銘柄の通貨換算後）",
        "capital_help": "米国株ならUSD、日本株ならJPYなど、分析銘柄と同じ通貨で入力します。",
        "risk_per_trade": "1回の取引で許容する損失（%）",
        "max_position": "1銘柄への最大配分（%）",
        "risk_dashboard": "リスクダッシュボード",
        "data_confidence": "データ信頼度",
        "confidence_caption": "取得できた主要データの割合です。低い場合は判断スコアを制限します。",
        "annual_volatility": "年率ボラティリティ",
        "max_drawdown": "1年最大下落率",
        "rsi14": "RSI（14日）",
        "atr14": "ATR（14日）",
        "momentum_3m": "3か月モメンタム",
        "volume_ratio": "出来高比（20日平均比）",
        "strengths": "プラス要因",
        "risks": "リスク要因",
        "no_strengths": "明確なプラス要因は検出されませんでした。",
        "no_risks": "重大なリスク要因は検出されませんでした。",
        "position_plan": "資金管理の目安",
        "planned_entry": "想定エントリー",
        "risk_review_price": "リスク見直し価格",
        "suggested_shares": "数量上限の目安",
        "position_value": "想定投資額",
        "risk_budget": "許容損失額",
        "two_r_reference": "2R参考価格",
        "stop_warning": "リスク見直し価格は約定を保証するストップ価格ではありません。窓開けや急変時は想定より大きな損失が出る可能性があります。",
        "company": "企業",
        "currency": "通貨",
        "as_of": "分析時刻",
        "data_source": "データ取得元",
        "fallback_notice": "Yahoo Financeの企業指標が取得できないため、価格・テクニカル中心の代替分析です。データ信頼度と判断スコアを制限しています。",
        "risk_downtrend": "長期下降トレンド（株価と50日線が200日線を下回る）",
        "risk_high_vol": "値動きが非常に大きい",
        "risk_drawdown": "52週高値から大きく下落している",
        "risk_balance": "負債・流動性に注意が必要",
        "risk_news": "ネガティブニュースが優勢",
        "risk_earnings": "決算発表が近い",
        "risk_low_confidence": "取得データが不足している",
        "risk_overbought": "RSIが過熱圏にある",
        "positive_uptrend": "株価が50日線・200日線を上回る上昇トレンド",
        "positive_growth": "売上と利益がともに成長している",
        "positive_cashflow": "フリーキャッシュフローがプラス",
        "positive_balance": "負債と流動性が比較的健全",
        "positive_valuation": "PERが保守的な範囲にある",
        "currency_factor": "円相場",
        "fx_sensitivity": "日本株の為替感応度",
        "fx_auto": "自動（海外株=外貨、日本株=中立）",
        "fx_foreign": "外貨建て資産（円換算）",
        "fx_exporter": "円安メリット（輸出型）",
        "fx_importer": "円高メリット（輸入型）",
        "fx_neutral": "中立・不明",
        "fx_auto_help": "日本株は企業ごとの海外売上・輸入コストが必要なため、自動では中立にします。分かる場合だけ変更してください。",
        "yen_dashboard": "円相場ダッシュボード",
        "usd_jpy": "ドル円（1USD）",
        "yen_regime": "円の方向",
        "yen_strong": "円高方向",
        "yen_weak": "円安方向",
        "yen_sideways": "方向感なし",
        "yen_3m_change": "ドル円3か月変化",
        "yen_position_1y": "1年レンジ内の位置",
        "fx_action": "為替面の判断",
        "fx_action_buy": "買いに有利",
        "fx_action_sell": "売却・円転の検討に有利",
        "fx_action_wait": "様子見",
        "fx_action_neutral": "為替だけでは判断しない",
        "fx_unavailable": "円相場を取得できないため、為替は採点していません。",
        "fx_disclaimer": "円高・円安だけで売買せず、株価トレンドと企業業績も合わせて判断します。海外株は株価が上昇しても円高で円換算利益が減る場合があります。",
        "risk_fx_headwind": "現在の円相場が買付または企業業績の逆風になりやすい",
        "positive_fx_tailwind": "現在の円相場が買付または企業業績の追い風になりやすい",
        "ipo_title": "国内IPO判断",
        "ipo_intro": "JPXの新規上場一覧・会社概要・Iの部を自動取得して評価します。銘柄を選ぶだけで、手入力は不要です。",
        "ipo_select_company": "評価するIPO",
        "ipo_refresh": "JPX情報を更新",
        "ipo_loading_list": "JPXから新規上場一覧を取得中...",
        "ipo_loading_details": "JPXの公式PDFから業績・発行情報を取得中...",
        "ipo_no_data": "評価できる国内IPOが見つかりませんでした。",
        "ipo_fetch_failed": "IPO情報の自動取得に失敗しました",
        "ipo_data_unavailable": "JPXの一覧または公式PDFを取得できませんでした。時間を置いて再実行してください。",
        "ipo_rate_limited": "JPXへのアクセスが一時的に制限されています。連続操作を避け、時間を置いてください。",
        "ipo_listing_date": "上場予定日",
        "ipo_approval_date": "上場承認日",
        "ipo_price_status": "価格の状態",
        "ipo_price_fixed": "公開価格決定済み",
        "ipo_price_tentative": "仮条件上限を暫定使用",
        "ipo_price_unavailable": "価格未定",
        "ipo_public_shares": "公募株（千株）",
        "ipo_secondary_shares": "売出株（千株）",
        "ipo_oa_shares": "OA（千株）",
        "ipo_shares_outstanding": "上場時発行済株式数",
        "ipo_business": "事業内容",
        "ipo_data_confidence": "自動取得率",
        "ipo_source_documents": "公式資料",
        "ipo_outline": "会社概要PDF",
        "ipo_report": "Iの部PDF",
        "ipo_auto_note": "数値はJPX掲載資料から自動抽出しています。仮条件しかない場合は上限価格で暫定計算します。",
        "ipo_missing_warning": "一部のPDF項目を抽出できなかったため、取得できた項目だけで暫定評価しています。公式PDFも確認してください。",
        "ipo_company_name": "会社名",
        "ipo_code": "証券コード",
        "ipo_market": "上場市場",
        "ipo_growth_market": "グロース",
        "ipo_standard_market": "スタンダード",
        "ipo_prime_market": "プライム",
        "ipo_offer_price": "公開価格（円）",
        "ipo_eps": "概算EPS（円）",
        "ipo_revenue_growth": "売上成長率（%）",
        "ipo_operating_margin": "経常利益率（%）",
        "ipo_market_cap": "公開価格ベース時価総額（億円）",
        "ipo_offering_amount": "吸収金額・OA含む（億円）",
        "ipo_secondary_ratio": "売出株比率（%）",
        "ipo_lockup": "ロックアップ対象比率（%）",
        "ipo_vc_ratio": "VC等保有比率（%）",
        "ipo_evaluate": "ネットから取得して評価",
        "ipo_total_score": "IPO総合スコア",
        "ipo_decision": "申込判断",
        "ipo_per": "参考PER",
        "ipo_absorption_ratio": "吸収金額/時価総額",
        "ipo_components": "IPOスコア内訳",
        "ipo_growth": "成長性",
        "ipo_profitability": "収益性",
        "ipo_valuation": "価格設定",
        "ipo_supply_demand": "需給",
        "ipo_shareholder": "公募・売出構成",
        "ipo_apply_strong": "🟢 積極的に申込検討",
        "ipo_apply_consider": "🟢 申込検討",
        "ipo_apply_selective": "🟡 条件付き・少額で検討",
        "ipo_caution": "🟠 慎重",
        "ipo_skip": "🔴 見送り候補",
        "ipo_strength_growth": "売上成長率が高い",
        "ipo_strength_profit": "経常利益率が良好",
        "ipo_strength_valuation": "公開価格のPERが抑えられている",
        "ipo_strength_supply": "吸収金額が時価総額に対して小さい",
        "ipo_strength_primary": "公募株の比率が高く、資金調達色が強い",
        "ipo_strength_lockup": "ロックアップのカバー率が高い",
        "ipo_risk_loss": "概算EPSが0以下で赤字・利益未確立",
        "ipo_risk_expensive": "参考PERが高い",
        "ipo_risk_absorption": "吸収金額が大きく需給負担になりやすい",
        "ipo_risk_secondary": "売出株の比率が高く、既存株主の換金色が強い",
        "ipo_risk_tentative": "公開価格が未決定のため、仮条件上限による暫定評価",
        "ipo_risk_missing": "公式PDFから抽出できない主要項目がある",
        "ipo_risk_lockup": "ロックアップのカバー率が低い",
        "ipo_risk_vc": "VC等の保有比率が高く、将来の売り圧力に注意",
        "ipo_primary_source": "JPX新規上場会社情報を開く",
        "ipo_disclaimer": "必ず最新の目論見書で事業内容、資金使途、主要株主、ロックアップ解除条件、業績予想を確認してください。上場直後は価格変動が非常に大きくなることがあります。",
        "input_error": "入力値を確認してください。公開価格と時価総額は0より大きい必要があります。",
        "key_metrics": "主要指標",
        "indicator": "指標",
        "value": "値",
        "revenue_growth": "売上成長率",
        "earnings_growth": "利益成長率",
        "operating_margin": "営業利益率",
        "roe": "ROE",
        "fcf_yield": "FCF利回り",
        "debt_equity": "負債資本比率",
        "current_ratio": "流動比率",
        "beta": "ベータ",
        "forward_pe": "Forward PER",
        "ma50": "50日線",
        "ma200": "200日線",
        "high52": "52週高値",
        "low52": "52週安値",
        "chart": "1年チャート",
        "close": "終値",
        "recent_news": "最近のニュース",
        "negative_news": "⚠️ ネガティブ見出し検出",
        "positive_news": "✅ ポジティブ見出し検出",
        "analysis_failed": "取得/分析に失敗しました",
        "price_unavailable": "株価データを取得できませんでした",
        "rate_limited": "Yahoo Financeのアクセス制限に達しました。連続して再試行せず、しばらく待ってからもう一度お試しください。",
        "scan_rate_limited": "アクセス制限を悪化させないため、一括スキャンを途中で停止しました。時間を置いて再実行してください。",
        "scan_failed": "取得失敗",
        "ticker_col": "ティッカー",
        "price_col": "価格",
        "decision_col": "判断",
        "confidence_col": "信頼度",
        "volatility_col": "年率変動率",
        "risk_count_col": "リスク数",
        "download_csv": "スキャン結果をCSV保存",
        "footer": "注意: このツールは投資助言や利益保証ではありません。円相場とIPOの表示はルールベースの参考評価です。売買前に最新の一次情報を確認してください。",
        "buy_candidate": "🟢 買い候補",
        "buy_small": "🟢 少量なら買い",
        "wait_split": "🟡 待つ / 分割",
        "caution": "🟠 慎重",
        "skip": "🔴 見送り",
    },
    "नेपाली": {
        "code": "ne",
        "title": "शेयर निर्णय उपकरण",
        "tool_mode": "विश्लेषण मेनु",
        "stock_analysis": "सूचीकृत शेयर र येन",
        "ipo_analysis": "जापानी IPO मूल्याङ्कन",
        "caption": "शेयर मूल्य, कम्पनीका सूचक र USD/JPY लिएर कम्पनी, बजार र येनको दिशालाई सँगै मूल्याङ्कन गर्छ। यो तपाईंको अन्तिम निर्णयलाई सहयोग गर्ने उपकरण हो।",
        "weights_header": "निर्णयका भारहरू",
        "investment_style": "लगानी शैली",
        "long_stable": "दीर्घकालीन तथा स्थिरता केन्द्रित",
        "growth": "वृद्धि केन्द्रित",
        "short_entry": "छोटो अवधिको प्रवेश केन्द्रित",
        "item": "विषय",
        "weight": "भार",
        "sidebar_info": "आम्दानी विवरण नजिक हुँदा अंक स्वतः घट्छ। समाचारको मूल्याङ्कन शीर्षकका शब्दमा आधारित सामान्य जाँच हो।",
        "ticker": "टिकर",
        "ticker_help": "अमेरिकी शेयर: NVDA / जापानी शेयर: 6501.T",
        "analyze": "विश्लेषण गर्नुहोस्",
        "scan": "मनपर्ने सूची स्क्यान गर्नुहोस्",
        "loading": "डेटा प्राप्त हुँदैछ...",
        "current_price": "हालको मूल्य",
        "total_score": "कुल अंक",
        "decision": "निर्णय",
        "next_earnings": "अर्को आय विवरण",
        "unavailable": "प्राप्त भएन",
        "buy_zones": "चरणबद्ध खरिद क्षेत्र (स्वचालित गणना)",
        "buy1": "पहिलो खरिद",
        "buy2": "दोस्रो खरिद",
        "buy3": "ठूलो गिरावटमा खरिद",
        "buy_caption": "मूल्य घटेपछि लक्ष्यलाई पछि सार्न नपरोस् भनेर विश्लेषणको समयमा तीन चरणका मूल्य निश्चित रूपमा देखाइन्छ।",
        "score_breakdown": "अंकको विवरण",
        "score": "अंक",
        "fundamental": "आधारभूत अवस्था",
        "valuation": "मूल्याङ्कन",
        "technical": "प्राविधिक",
        "news": "समाचार",
        "event": "घटना जोखिम",
        "risk_settings": "जोखिम व्यवस्थापन सेटिङ",
        "capital_label": "उपलब्ध पूँजी (टिकरको मुद्रामा)",
        "capital_help": "अमेरिकी शेयरका लागि USD र जापानी शेयरका लागि JPY जस्ता, विश्लेषण गरिएको शेयरकै मुद्रामा प्रविष्ट गर्नुहोस्।",
        "risk_per_trade": "प्रति कारोबार स्वीकार्य जोखिम (%)",
        "max_position": "एउटा शेयरमा अधिकतम लगानी (%)",
        "risk_dashboard": "जोखिम ड्यासबोर्ड",
        "data_confidence": "डेटा विश्वसनीयता",
        "confidence_caption": "प्राप्त भएका मुख्य डेटाको अनुपात हो। डेटा कम हुँदा निर्णय अंक सीमित गरिन्छ।",
        "annual_volatility": "वार्षिक अस्थिरता",
        "max_drawdown": "१ वर्षको अधिकतम गिरावट",
        "rsi14": "RSI (१४ दिन)",
        "atr14": "ATR (१४ दिन)",
        "momentum_3m": "३ महिनाको गति",
        "volume_ratio": "कारोबार मात्रा अनुपात (२०-दिने औसत)",
        "strengths": "सकारात्मक पक्षहरू",
        "risks": "जोखिम संकेतहरू",
        "no_strengths": "स्पष्ट सकारात्मक पक्ष फेला परेन।",
        "no_risks": "गम्भीर जोखिम संकेत फेला परेन।",
        "position_plan": "पूँजी व्यवस्थापनको अनुमान",
        "planned_entry": "अनुमानित प्रवेश मूल्य",
        "risk_review_price": "जोखिम पुनरावलोकन मूल्य",
        "suggested_shares": "सुझाव गरिएको अधिकतम संख्या",
        "position_value": "अनुमानित लगानी रकम",
        "risk_budget": "स्वीकार्य जोखिम रकम",
        "two_r_reference": "2R सन्दर्भ मूल्य",
        "stop_warning": "जोखिम पुनरावलोकन मूल्यले स्टप अर्डरको वास्तविक निष्पादन मूल्य सुनिश्चित गर्दैन। मूल्यको अन्तर वा तीव्र परिवर्तन हुँदा नोक्सानी अनुमानभन्दा ठूलो हुन सक्छ।",
        "company": "कम्पनी",
        "currency": "मुद्रा",
        "as_of": "विश्लेषण समय",
        "data_source": "डेटा स्रोत",
        "fallback_notice": "Yahoo Finance का कम्पनी सूचक प्राप्त नभएकाले यो मूल्य र प्राविधिक डेटामा आधारित वैकल्पिक विश्लेषण हो। डेटा विश्वसनीयता र निर्णय अंक सीमित गरिएको छ।",
        "risk_downtrend": "दीर्घकालीन घट्दो प्रवृत्ति (मूल्य र ५०-दिने औसत २००-दिने औसतभन्दा तल)",
        "risk_high_vol": "मूल्यमा अत्यधिक उतारचढाव",
        "risk_drawdown": "५२-हप्ताको उच्च मूल्यबाट ठूलो गिरावट",
        "risk_balance": "ऋण वा तरलतामा सावधानी आवश्यक",
        "risk_news": "नकारात्मक समाचार बढी छन्",
        "risk_earnings": "आय विवरण घोषणा नजिक छ",
        "risk_low_confidence": "आवश्यक डेटा पर्याप्त छैन",
        "risk_overbought": "RSI अत्यधिक खरिद क्षेत्रमा छ",
        "positive_uptrend": "मूल्य ५० र २००-दिने औसतभन्दा माथि छ",
        "positive_growth": "राजस्व र नाफा दुवै बढिरहेका छन्",
        "positive_cashflow": "फ्री क्यास फ्लो सकारात्मक छ",
        "positive_balance": "ऋण र तरलताको अवस्था तुलनात्मक रूपमा स्वस्थ छ",
        "positive_valuation": "P/E सावधानीपूर्ण सीमाभित्र छ",
        "currency_factor": "येन विनिमय दर",
        "fx_sensitivity": "जापानी शेयरको विनिमय संवेदनशीलता",
        "fx_auto": "स्वचालित (विदेशी शेयर=विदेशी मुद्रा, जापानी शेयर=तटस्थ)",
        "fx_foreign": "विदेशी मुद्रामा सम्पत्ति (येन रूपान्तरण)",
        "fx_exporter": "कमजोर येनबाट लाभ (निर्यातकर्ता)",
        "fx_importer": "बलियो येनबाट लाभ (आयातकर्ता)",
        "fx_neutral": "तटस्थ वा अज्ञात",
        "fx_auto_help": "जापानी कम्पनीका लागि विदेशी बिक्री र आयात लागत आवश्यक हुने भएकाले स्वचालित मोड तटस्थ हुन्छ। जानकारी भएमा मात्र परिवर्तन गर्नुहोस्।",
        "yen_dashboard": "येन विनिमय ड्यासबोर्ड",
        "usd_jpy": "USD/JPY (1 USD)",
        "yen_regime": "येनको दिशा",
        "yen_strong": "येन बलियो हुँदै",
        "yen_weak": "येन कमजोर हुँदै",
        "yen_sideways": "स्पष्ट दिशा छैन",
        "yen_3m_change": "USD/JPY ३-महिने परिवर्तन",
        "yen_position_1y": "१-वर्ष दायराको स्थान",
        "fx_action": "विनिमय दरको निर्णय",
        "fx_action_buy": "खरिदका लागि अनुकूल",
        "fx_action_sell": "बिक्री वा येनमा रूपान्तरण विचार गर्न अनुकूल",
        "fx_action_wait": "प्रतीक्षा",
        "fx_action_neutral": "विनिमय दरबाट मात्र निर्णय नगर्नुहोस्",
        "fx_unavailable": "येन विनिमय दर प्राप्त भएन, त्यसैले यसलाई अंकमा समावेश गरिएको छैन।",
        "fx_disclaimer": "येन बलियो वा कमजोर भएको आधारमा मात्र कारोबार नगर्नुहोस्; शेयरको प्रवृत्ति र कम्पनीको नतिजा पनि हेर्नुहोस्। विदेशी शेयर बढे पनि येन बलियो हुँदा येनमा नाफा घट्न सक्छ।",
        "risk_fx_headwind": "हालको येन अवस्था खरिद वा कम्पनीको नतिजाका लागि प्रतिकूल हुन सक्छ",
        "positive_fx_tailwind": "हालको येन अवस्था खरिद वा कम्पनीको नतिजाका लागि अनुकूल हुन सक्छ",
        "ipo_title": "जापानी IPO मूल्याङ्कन",
        "ipo_intro": "JPX को नयाँ सूची, कम्पनी रूपरेखा र आधिकारिक रिपोर्ट स्वतः लिएर मूल्याङ्कन गर्छ। कम्पनी छान्नुहोस्; हातैले संख्या हाल्नुपर्दैन।",
        "ipo_select_company": "मूल्याङ्कन गर्ने IPO",
        "ipo_refresh": "JPX जानकारी अपडेट गर्नुहोस्",
        "ipo_loading_list": "JPX बाट नयाँ सूची ल्याउँदै...",
        "ipo_loading_details": "JPX का आधिकारिक PDF बाट वित्तीय र शेयर जानकारी ल्याउँदै...",
        "ipo_no_data": "मूल्याङ्कन गर्न मिल्ने जापानी IPO भेटिएन।",
        "ipo_fetch_failed": "IPO जानकारी स्वतः प्राप्त गर्न असफल",
        "ipo_data_unavailable": "JPX सूची वा आधिकारिक PDF प्राप्त भएन। केही समयपछि पुनः प्रयास गर्नुहोस्।",
        "ipo_rate_limited": "JPX पहुँच अस्थायी रूपमा सीमित छ। लगातार प्रयास नगरी केही समय पर्खनुहोस्।",
        "ipo_listing_date": "सूचीकरण मिति",
        "ipo_approval_date": "सूचीकरण स्वीकृति मिति",
        "ipo_price_status": "मूल्यको अवस्था",
        "ipo_price_fixed": "अफर मूल्य निश्चित",
        "ipo_price_tentative": "अस्थायी रूपमा दायराको माथिल्लो मूल्य",
        "ipo_price_unavailable": "मूल्य तय भएको छैन",
        "ipo_public_shares": "नयाँ शेयर (हजार)",
        "ipo_secondary_shares": "पुराना शेयर बिक्री (हजार)",
        "ipo_oa_shares": "OA (हजार)",
        "ipo_shares_outstanding": "सूचीकरणपछि जारी शेयर",
        "ipo_business": "व्यवसाय",
        "ipo_data_confidence": "स्वतः प्राप्त दर",
        "ipo_source_documents": "आधिकारिक कागजात",
        "ipo_outline": "कम्पनी रूपरेखा PDF",
        "ipo_report": "आधिकारिक रिपोर्ट PDF",
        "ipo_auto_note": "संख्या JPX कागजातबाट स्वतः निकालिन्छ। अफर मूल्य नआएमा दायराको माथिल्लो मूल्य अस्थायी रूपमा प्रयोग हुन्छ।",
        "ipo_missing_warning": "PDF का केही मुख्य तथ्य निकाल्न नसकेकाले उपलब्ध तथ्यबाट मात्र अस्थायी मूल्याङ्कन गरिएको छ। आधिकारिक PDF पनि जाँच गर्नुहोस्।",
        "ipo_company_name": "कम्पनीको नाम",
        "ipo_code": "सेक्युरिटी कोड",
        "ipo_market": "सूचीकरण बजार",
        "ipo_growth_market": "Growth",
        "ipo_standard_market": "Standard",
        "ipo_prime_market": "Prime",
        "ipo_offer_price": "अफर मूल्य (येन)",
        "ipo_eps": "अनुमानित EPS (येन)",
        "ipo_revenue_growth": "राजस्व वृद्धि (%)",
        "ipo_operating_margin": "साधारण नाफा मार्जिन (%)",
        "ipo_market_cap": "अफर मूल्यमा बजार पूँजीकरण (१० करोड येन)",
        "ipo_offering_amount": "कुल प्रस्ताव आकार, OA सहित (१० करोड येन)",
        "ipo_secondary_ratio": "पुराना शेयर बिक्री अनुपात (%)",
        "ipo_lockup": "लक-अपले समेटेको अनुपात (%)",
        "ipo_vc_ratio": "VC आदि स्वामित्व (%)",
        "ipo_evaluate": "इन्टरनेटबाट लिएर मूल्याङ्कन",
        "ipo_total_score": "IPO कुल अंक",
        "ipo_decision": "आवेदन निर्णय",
        "ipo_per": "सन्दर्भ P/E",
        "ipo_absorption_ratio": "प्रस्ताव आकार/बजार पूँजीकरण",
        "ipo_components": "IPO अंक विवरण",
        "ipo_growth": "वृद्धि",
        "ipo_profitability": "नाफाक्षमता",
        "ipo_valuation": "मूल्य निर्धारण",
        "ipo_supply_demand": "माग र आपूर्ति",
        "ipo_shareholder": "नयाँ/पुराना शेयर संरचना",
        "ipo_apply_strong": "🟢 सक्रिय रूपमा आवेदन विचार",
        "ipo_apply_consider": "🟢 आवेदन विचार",
        "ipo_apply_selective": "🟡 सर्तसहित वा सानो रकम",
        "ipo_caution": "🟠 सावधानी",
        "ipo_skip": "🔴 छोड्ने विचार",
        "ipo_strength_growth": "राजस्व वृद्धि उच्च छ",
        "ipo_strength_profit": "साधारण नाफा मार्जिन राम्रो छ",
        "ipo_strength_valuation": "अफर मूल्य P/E उचित छ",
        "ipo_strength_supply": "बजार पूँजीकरणको तुलनामा प्रस्ताव सानो छ",
        "ipo_strength_primary": "नयाँ शेयरको अनुपात उच्च भएकाले पूँजी जुटाउने उद्देश्य बलियो छ",
        "ipo_strength_lockup": "लक-अप कभरेज उच्च छ",
        "ipo_risk_loss": "अनुमानित EPS शून्य वा ऋणात्मक छ",
        "ipo_risk_expensive": "अफर मूल्य P/E उच्च छ",
        "ipo_risk_absorption": "ठूलो प्रस्तावले माग-आपूर्तिमा दबाब दिन सक्छ",
        "ipo_risk_secondary": "पुराना शेयर बिक्री धेरै भएकाले निकासको संकेत बलियो छ",
        "ipo_risk_tentative": "अफर मूल्य निश्चित नभएकाले दायराको माथिल्लो मूल्यमा अस्थायी मूल्याङ्कन",
        "ipo_risk_missing": "आधिकारिक PDF बाट केही मुख्य तथ्य निकाल्न सकिएन",
        "ipo_risk_lockup": "लक-अप कभरेज कम छ",
        "ipo_risk_vc": "VC स्वामित्व धेरै भएकाले भविष्यको बिक्री दबाबमा ध्यान दिनुहोस्",
        "ipo_primary_source": "JPX नयाँ सूची जानकारी खोल्नुहोस्",
        "ipo_disclaimer": "पछिल्लो प्रॉस्पेक्टसमा व्यवसाय, रकमको प्रयोग, मुख्य शेयरधनी, लक-अप खुल्ने सर्त र अनुमानित नतिजा जाँच गर्नुहोस्। सूचीकरणपछि मूल्य अत्यधिक चल्न सक्छ।",
        "input_error": "इनपुट जाँच गर्नुहोस्। अफर मूल्य र बजार पूँजीकरण शून्यभन्दा ठूलो हुनुपर्छ।",
        "key_metrics": "मुख्य सूचकहरू",
        "indicator": "सूचक",
        "value": "मान",
        "revenue_growth": "राजस्व वृद्धि",
        "earnings_growth": "नाफा वृद्धि",
        "operating_margin": "सञ्चालन नाफा मार्जिन",
        "roe": "ROE",
        "fcf_yield": "FCF प्रतिफल",
        "debt_equity": "ऋण/इक्विटी अनुपात",
        "current_ratio": "चालु अनुपात",
        "beta": "बिटा",
        "forward_pe": "Forward PER",
        "ma50": "५०-दिने औसत",
        "ma200": "२००-दिने औसत",
        "high52": "५२-हप्ताको उच्च",
        "low52": "५२-हप्ताको न्यून",
        "chart": "१ वर्षको चार्ट",
        "close": "बन्द मूल्य",
        "recent_news": "हालका समाचार",
        "negative_news": "⚠️ नकारात्मक शीर्षक फेला पर्यो",
        "positive_news": "✅ सकारात्मक शीर्षक फेला पर्यो",
        "analysis_failed": "डेटा प्राप्ति/विश्लेषण असफल भयो",
        "price_unavailable": "शेयर मूल्यको डेटा प्राप्त भएन",
        "rate_limited": "Yahoo Finance को पहुँच सीमा पुगेको छ। लगातार पुनः प्रयास नगरी केही समयपछि फेरि प्रयास गर्नुहोस्।",
        "scan_rate_limited": "पहुँच सीमा नबढोस् भनेर सामूहिक स्क्यान बीचमै रोकियो। केही समयपछि पुनः प्रयास गर्नुहोस्।",
        "scan_failed": "प्राप्त गर्न असफल",
        "ticker_col": "टिकर",
        "price_col": "मूल्य",
        "decision_col": "निर्णय",
        "confidence_col": "विश्वसनीयता",
        "volatility_col": "वार्षिक अस्थिरता",
        "risk_count_col": "जोखिम संख्या",
        "download_csv": "स्क्यान नतिजा CSV मा सुरक्षित गर्नुहोस्",
        "footer": "चेतावनी: यो उपकरण लगानी सल्लाह वा नाफाको ग्यारेन्टी होइन। येन र IPO मूल्याङ्कन नियममा आधारित सन्दर्भ मात्र हो। कारोबारअघि नवीनतम प्राथमिक स्रोत जाँच गर्नुहोस्।",
        "buy_candidate": "🟢 खरिदका लागि उम्मेदवार",
        "buy_small": "🟢 थोरै मात्रामा खरिद",
        "wait_split": "🟡 प्रतीक्षा / चरणबद्ध खरिद",
        "caution": "🟠 सावधानी",
        "skip": "🔴 नकिन्नुहोस्",
    },
    "English": {
        "code": "en",
        "title": "Stock Decision Tool",
        "tool_mode": "Analysis menu",
        "stock_analysis": "Listed stocks and yen",
        "ipo_analysis": "Japan IPO review",
        "caption": "Combines stock prices, company metrics, and USD/JPY direction into a rule-based decision aid. You remain responsible for the final decision.",
        "weights_header": "Decision weights",
        "investment_style": "Investment style",
        "long_stable": "Long-term and stability",
        "growth": "Growth focused",
        "short_entry": "Short-term entry focused",
        "item": "Item",
        "weight": "Weight",
        "sidebar_info": "The score is reduced automatically just before earnings. News analysis is a simple headline-based check.",
        "ticker": "Ticker",
        "ticker_help": "US stock: NVDA / Japanese stock: 6501.T",
        "analyze": "Analyze",
        "scan": "Scan favorites",
        "loading": "Fetching data...",
        "current_price": "Current price",
        "total_score": "Total score",
        "decision": "Decision",
        "next_earnings": "Next earnings",
        "unavailable": "Unavailable",
        "buy_zones": "Staged buy zones (automatic)",
        "buy1": "First buy",
        "buy2": "Second buy",
        "buy3": "Strong pullback",
        "buy_caption": "The three price levels are fixed at analysis time so the targets are not moved lower after every price decline.",
        "score_breakdown": "Score breakdown",
        "score": "Score",
        "fundamental": "Fundamental",
        "valuation": "Valuation",
        "technical": "Technical",
        "news": "News",
        "event": "Event risk",
        "risk_settings": "Risk management settings",
        "capital_label": "Available capital (in the ticker's currency)",
        "capital_help": "Enter the amount in the analyzed ticker's currency, such as USD for US stocks or JPY for Japanese stocks.",
        "risk_per_trade": "Maximum loss per trade (%)",
        "max_position": "Maximum allocation per stock (%)",
        "risk_dashboard": "Risk dashboard",
        "data_confidence": "Data confidence",
        "confidence_caption": "Percentage of key inputs that were available. The decision score is capped when too much data is missing.",
        "annual_volatility": "Annualized volatility",
        "max_drawdown": "1-year maximum drawdown",
        "rsi14": "RSI (14-day)",
        "atr14": "ATR (14-day)",
        "momentum_3m": "3-month momentum",
        "volume_ratio": "Volume ratio (vs. 20-day avg.)",
        "strengths": "Positive factors",
        "risks": "Risk factors",
        "no_strengths": "No clear positive factors were detected.",
        "no_risks": "No major risk factors were detected.",
        "position_plan": "Position sizing guide",
        "planned_entry": "Planned entry",
        "risk_review_price": "Risk review price",
        "suggested_shares": "Suggested maximum quantity",
        "position_value": "Estimated position value",
        "risk_budget": "Risk budget",
        "two_r_reference": "2R reference price",
        "stop_warning": "The risk review price is not a guaranteed stop execution price. Gaps and fast markets can produce a larger loss than estimated.",
        "company": "Company",
        "currency": "Currency",
        "as_of": "Analysis time",
        "data_source": "Data source",
        "fallback_notice": "Yahoo Finance company metrics were unavailable, so this is a fallback analysis based mainly on price and technical data. Confidence and the decision score are capped.",
        "risk_downtrend": "Long-term downtrend (price and 50-day average are below the 200-day average)",
        "risk_high_vol": "Price volatility is very high",
        "risk_drawdown": "Price is far below its 52-week high",
        "risk_balance": "Debt or liquidity requires caution",
        "risk_news": "Negative news is dominant",
        "risk_earnings": "Earnings announcement is near",
        "risk_low_confidence": "Important data is missing",
        "risk_overbought": "RSI is in an overbought range",
        "positive_uptrend": "Price is above both the 50-day and 200-day averages",
        "positive_growth": "Revenue and earnings are both growing",
        "positive_cashflow": "Free cash flow is positive",
        "positive_balance": "Debt and liquidity are relatively healthy",
        "positive_valuation": "P/E is within a conservative range",
        "currency_factor": "Yen movement",
        "fx_sensitivity": "FX sensitivity of Japanese stock",
        "fx_auto": "Automatic (foreign stock=FX asset, Japan stock=neutral)",
        "fx_foreign": "Foreign-currency asset (JPY basis)",
        "fx_exporter": "Benefits from weak yen (exporter)",
        "fx_importer": "Benefits from strong yen (importer)",
        "fx_neutral": "Neutral or unknown",
        "fx_auto_help": "Automatic mode treats Japanese stocks as neutral because overseas sales and import costs differ by company. Change it only when you know the exposure.",
        "yen_dashboard": "Yen dashboard",
        "usd_jpy": "USD/JPY (1 USD)",
        "yen_regime": "Yen direction",
        "yen_strong": "Yen strengthening",
        "yen_weak": "Yen weakening",
        "yen_sideways": "No clear direction",
        "yen_3m_change": "3-month USD/JPY change",
        "yen_position_1y": "Position in 1-year range",
        "fx_action": "FX view",
        "fx_action_buy": "Favorable for buying",
        "fx_action_sell": "Favorable for selling or converting to yen",
        "fx_action_wait": "Wait",
        "fx_action_neutral": "Do not decide from FX alone",
        "fx_unavailable": "Yen data was unavailable, so FX was not scored.",
        "fx_disclaimer": "Do not trade from yen direction alone; combine it with the stock trend and company performance. A foreign stock can rise while its yen-denominated return falls when the yen strengthens.",
        "risk_fx_headwind": "The current yen environment may be a headwind for buying or company earnings",
        "positive_fx_tailwind": "The current yen environment may support buying or company earnings",
        "ipo_title": "Japan IPO Review",
        "ipo_intro": "Automatically retrieves the JPX new-listing table, company outline, and filing. Select a company; no manual figures are required.",
        "ipo_select_company": "IPO to evaluate",
        "ipo_refresh": "Refresh JPX data",
        "ipo_loading_list": "Loading new listings from JPX...",
        "ipo_loading_details": "Loading financial and offering data from official JPX PDFs...",
        "ipo_no_data": "No Japanese IPOs available for evaluation were found.",
        "ipo_fetch_failed": "Automatic IPO retrieval failed",
        "ipo_data_unavailable": "The JPX list or official PDF could not be retrieved. Wait and try again later.",
        "ipo_rate_limited": "JPX access is temporarily limited. Avoid repeated requests and wait before retrying.",
        "ipo_listing_date": "Listing date",
        "ipo_approval_date": "Listing approval date",
        "ipo_price_status": "Price status",
        "ipo_price_fixed": "Offer price fixed",
        "ipo_price_tentative": "Tentative range upper bound used",
        "ipo_price_unavailable": "Price not yet available",
        "ipo_public_shares": "Primary shares (thousands)",
        "ipo_secondary_shares": "Secondary shares (thousands)",
        "ipo_oa_shares": "OA shares (thousands)",
        "ipo_shares_outstanding": "Shares outstanding at listing",
        "ipo_business": "Business",
        "ipo_data_confidence": "Automatic data coverage",
        "ipo_source_documents": "Official documents",
        "ipo_outline": "Company outline PDF",
        "ipo_report": "Securities report PDF",
        "ipo_auto_note": "Figures are extracted automatically from JPX documents. Until an offer price is fixed, the upper end of the indicated range is used provisionally.",
        "ipo_missing_warning": "Some PDF fields could not be extracted, so the score is provisional and uses only available items. Check the official PDFs as well.",
        "ipo_company_name": "Company name",
        "ipo_code": "Security code",
        "ipo_market": "Listing market",
        "ipo_growth_market": "Growth",
        "ipo_standard_market": "Standard",
        "ipo_prime_market": "Prime",
        "ipo_offer_price": "Offer price (JPY)",
        "ipo_eps": "Approximate EPS (JPY)",
        "ipo_revenue_growth": "Revenue growth (%)",
        "ipo_operating_margin": "Ordinary-profit margin (%)",
        "ipo_market_cap": "Market cap at offer price (JPY 100m)",
        "ipo_offering_amount": "Offering size incl. OA (JPY 100m)",
        "ipo_secondary_ratio": "Secondary-share ratio (%)",
        "ipo_lockup": "Lock-up coverage (%)",
        "ipo_vc_ratio": "VC ownership (%)",
        "ipo_evaluate": "Fetch online and evaluate",
        "ipo_total_score": "IPO total score",
        "ipo_decision": "Application decision",
        "ipo_per": "Reference P/E",
        "ipo_absorption_ratio": "Offering size / market cap",
        "ipo_components": "IPO score breakdown",
        "ipo_growth": "Growth",
        "ipo_profitability": "Profitability",
        "ipo_valuation": "Pricing",
        "ipo_supply_demand": "Supply and demand",
        "ipo_shareholder": "Primary/secondary mix",
        "ipo_apply_strong": "🟢 Strong application candidate",
        "ipo_apply_consider": "🟢 Consider applying",
        "ipo_apply_selective": "🟡 Conditional or small application",
        "ipo_caution": "🟠 Caution",
        "ipo_skip": "🔴 Consider skipping",
        "ipo_strength_growth": "Revenue growth is high",
        "ipo_strength_profit": "Ordinary-profit margin is healthy",
        "ipo_strength_valuation": "Offer-price P/E is restrained",
        "ipo_strength_supply": "Offering size is small relative to market cap",
        "ipo_strength_primary": "A high primary-share ratio indicates stronger capital raising",
        "ipo_strength_lockup": "Lock-up coverage is high",
        "ipo_risk_loss": "Approximate EPS is zero or negative",
        "ipo_risk_expensive": "Reference P/E is high",
        "ipo_risk_absorption": "A large offering may weigh on supply and demand",
        "ipo_risk_secondary": "A high secondary-share ratio suggests strong existing-holder selling",
        "ipo_risk_tentative": "The offer price is not fixed; this uses the top of the indicated range provisionally",
        "ipo_risk_missing": "Some key fields could not be extracted from the official PDFs",
        "ipo_risk_lockup": "Lock-up coverage is low",
        "ipo_risk_vc": "High VC ownership may create future selling pressure",
        "ipo_primary_source": "Open JPX new-listing information",
        "ipo_disclaimer": "Check the latest prospectus for the business, use of proceeds, major shareholders, lock-up release terms, and forecasts. Prices can be extremely volatile immediately after listing.",
        "input_error": "Check the inputs. Offer price and market cap must be greater than zero.",
        "key_metrics": "Key metrics",
        "indicator": "Indicator",
        "value": "Value",
        "revenue_growth": "Revenue growth",
        "earnings_growth": "Earnings growth",
        "operating_margin": "Operating margin",
        "roe": "Return on equity",
        "fcf_yield": "Free-cash-flow yield",
        "debt_equity": "Debt to equity",
        "current_ratio": "Current ratio",
        "beta": "Beta",
        "forward_pe": "Forward P/E",
        "ma50": "50-day average",
        "ma200": "200-day average",
        "high52": "52-week high",
        "low52": "52-week low",
        "chart": "1-year chart",
        "close": "Close",
        "recent_news": "Recent news",
        "negative_news": "⚠️ Negative headlines detected",
        "positive_news": "✅ Positive headlines detected",
        "analysis_failed": "Data retrieval/analysis failed",
        "price_unavailable": "Stock price data could not be retrieved",
        "rate_limited": "Yahoo Finance rate-limited this request. Avoid repeated retries and try again after waiting for a while.",
        "scan_rate_limited": "The batch scan was stopped early to avoid extending the rate limit. Wait before trying again.",
        "scan_failed": "Retrieval failed",
        "ticker_col": "Ticker",
        "price_col": "Price",
        "decision_col": "Decision",
        "confidence_col": "Confidence",
        "volatility_col": "Annual volatility",
        "risk_count_col": "Risk count",
        "download_csv": "Download scan results as CSV",
        "footer": "Warning: This tool is not investment advice or a profit guarantee. FX and IPO outputs are rule-based reference assessments. Verify current primary sources before trading.",
        "buy_candidate": "🟢 Buy candidate",
        "buy_small": "🟢 Small buy",
        "wait_split": "🟡 Wait / staged buy",
        "caution": "🟠 Caution",
        "skip": "🔴 Skip",
    },
}


def tr(key):
    language = st.session_state.get("language", "日本語")
    return LANGUAGES[language][key]


def localized_error(error):
    if str(error) == "PRICE_DATA_UNAVAILABLE":
        return tr("price_unavailable")
    if str(error) == "YFINANCE_RATE_LIMIT":
        return tr("rate_limited")
    if str(error) == "IPO_DATA_UNAVAILABLE":
        return tr("ipo_data_unavailable")
    if str(error) == "IPO_RATE_LIMIT":
        return tr("ipo_rate_limited")
    return str(error)

def safe_num(v):
    try:
        if v is None:
            return np.nan
        number = float(v)
        return number if np.isfinite(number) else np.nan
    except:
        return np.nan

@st.cache_data(ttl=900, show_spinner=False)
def load_chart_fallback(ticker):
    symbol = quote_plus(ticker)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d&events=history"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException:
        raise RuntimeError("PRICE_DATA_UNAVAILABLE")

    if response.status_code == 429:
        raise RuntimeError("YFINANCE_RATE_LIMIT")
    if response.status_code != 200:
        raise RuntimeError("PRICE_DATA_UNAVAILABLE")

    try:
        payload = response.json()["chart"]
        if payload.get("error") or not payload.get("result"):
            raise ValueError
        result = payload["result"][0]
        timestamps = result.get("timestamp") or []
        quote = result["indicators"]["quote"][0]
        if not timestamps or not quote:
            raise ValueError

        hist = pd.DataFrame({
            "Open": quote.get("open"),
            "High": quote.get("high"),
            "Low": quote.get("low"),
            "Close": quote.get("close"),
            "Volume": quote.get("volume"),
        }, index=pd.to_datetime(timestamps, unit="s", utc=True))
        hist.index.name = "Date"
        hist = hist.dropna(subset=["Close"])
        if hist.empty:
            raise ValueError

        meta = result.get("meta") or {}
        info = {
            "shortName": meta.get("longName") or meta.get("shortName") or ticker,
            "currency": meta.get("currency") or "-",
            "exchange": meta.get("fullExchangeName") or meta.get("exchangeName") or "-",
        }
    except (KeyError, TypeError, ValueError):
        raise RuntimeError("PRICE_DATA_UNAVAILABLE")

    return hist, info, None, "Yahoo chart API", True


@st.cache_data(ttl=900, show_spinner=False)
def load_price(ticker):
    t = yf.Ticker(ticker)
    try:
        hist = t.history(period="1y", auto_adjust=False, timeout=15)
    except Exception as error:
        if error.__class__.__name__ == "YFRateLimitError":
            return load_chart_fallback(ticker)
        try:
            return load_chart_fallback(ticker)
        except Exception:
            raise error
    if hist.empty:
        return load_chart_fallback(ticker)
    info = {}
    try:
        info = t.get_info()
    except Exception as error:
        if error.__class__.__name__ != "YFRateLimitError":
            try:
                info = t.info
            except Exception:
                info = {}
    cal = None
    try:
        cal = t.calendar
    except Exception:
        pass
    return hist, info, cal, "Yahoo Finance / yfinance", False

def pct(a, b):
    if pd.isna(a) or pd.isna(b) or b == 0:
        return np.nan
    return (a / b - 1) * 100

def normalize_component(raw, lo=-5, hi=5):
    return max(lo, min(hi, raw))


def compute_market_metrics(hist):
    close = hist["Close"].dropna()
    high = hist["High"].reindex(close.index)
    low = hist["Low"].reindex(close.index)

    delta = close.diff()
    average_gain = delta.clip(lower=0).rolling(14).mean()
    average_loss = -delta.clip(upper=0).rolling(14).mean()
    relative_strength = average_gain / average_loss.replace(0, np.nan)
    rsi_series = 100 - (100 / (1 + relative_strength))
    if len(average_loss) and average_loss.iloc[-1] == 0:
        rsi14 = 50.0 if average_gain.iloc[-1] == 0 else 100.0
    else:
        rsi14 = float(rsi_series.iloc[-1]) if len(rsi_series.dropna()) else np.nan

    previous_close = close.shift(1)
    true_range = pd.concat([
        high - low,
        (high - previous_close).abs(),
        (low - previous_close).abs(),
    ], axis=1).max(axis=1)
    atr14 = float(true_range.tail(14).mean()) if len(true_range.dropna()) >= 14 else np.nan

    daily_return = close.pct_change().dropna()
    annual_volatility = float(daily_return.tail(20).std() * np.sqrt(252)) if len(daily_return) >= 20 else np.nan
    drawdown = close / close.cummax() - 1
    max_drawdown = float(drawdown.min() * 100) if len(drawdown) else np.nan
    momentum_3m = pct(float(close.iloc[-1]), float(close.iloc[-64])) if len(close) >= 64 else np.nan

    volume = hist["Volume"].reindex(close.index).dropna()
    avg_volume20 = float(volume.tail(20).mean()) if len(volume) >= 20 else np.nan
    volume_ratio = (
        float(volume.iloc[-1] / avg_volume20)
        if len(volume) and not pd.isna(avg_volume20) and avg_volume20 > 0
        else np.nan
    )

    return {
        "rsi14": rsi14,
        "atr14": atr14,
        "annual_volatility": annual_volatility,
        "max_drawdown": max_drawdown,
        "momentum_3m": momentum_3m,
        "volume_ratio": volume_ratio,
    }


@st.cache_data(ttl=900, show_spinner=False)
def load_yen_context():
    """Return the USD/JPY regime. A lower quote means a stronger yen."""
    try:
        hist, _, _, source, _ = load_chart_fallback("JPY=X")
        close = hist["Close"].dropna()
        if len(close) < 64:
            raise RuntimeError("PRICE_DATA_UNAVAILABLE")

        rate = float(close.iloc[-1])
        ma20 = float(close.tail(20).mean())
        ma50 = float(close.tail(50).mean())
        change_3m = pct(rate, float(close.iloc[-64]))
        low_1y = float(close.min())
        high_1y = float(close.max())
        range_width = high_1y - low_1y
        position_1y = (rate - low_1y) / range_width * 100 if range_width > 0 else 50.0

        if rate < ma50 and change_3m <= -2.0:
            regime = "yen_strong"
        elif rate > ma50 and change_3m >= 2.0:
            regime = "yen_weak"
        else:
            regime = "yen_sideways"

        return {
            "available": True,
            "rate": rate,
            "ma20": ma20,
            "ma50": ma50,
            "change_3m": change_3m,
            "position_1y": position_1y,
            "regime": regime,
            "source": source,
        }
    except Exception as error:
        return {
            "available": False,
            "rate": np.nan,
            "ma20": np.nan,
            "ma50": np.nan,
            "change_3m": np.nan,
            "position_1y": np.nan,
            "regime": "yen_sideways",
            "source": "-",
            "error": str(error),
        }


def evaluate_fx(ticker, currency, selected_sensitivity, yen):
    if selected_sensitivity == "fx_auto":
        if ticker.upper().endswith(".T") or str(currency).upper() == "JPY":
            sensitivity = "fx_neutral"
        else:
            sensitivity = "fx_foreign"
    else:
        sensitivity = selected_sensitivity

    if not yen.get("available"):
        return {
            "score": 0.0,
            "action_key": "fx_action_neutral",
            "sensitivity": sensitivity,
            "tailwind": False,
            "headwind": False,
        }

    regime = yen["regime"]
    score = 0.0
    if sensitivity == "fx_foreign":
        score = 1.25 if regime == "yen_strong" else -1.25 if regime == "yen_weak" else 0.0
    elif sensitivity == "fx_exporter":
        score = 1.5 if regime == "yen_weak" else -1.5 if regime == "yen_strong" else 0.0
    elif sensitivity == "fx_importer":
        score = 1.5 if regime == "yen_strong" else -1.5 if regime == "yen_weak" else 0.0

    if score >= 1.0:
        action_key = "fx_action_buy"
    elif score <= -1.0:
        action_key = "fx_action_sell"
    elif sensitivity == "fx_neutral":
        action_key = "fx_action_neutral"
    else:
        action_key = "fx_action_wait"

    return {
        "score": score,
        "action_key": action_key,
        "sensitivity": sensitivity,
        "tailwind": score >= 1.0,
        "headwind": score <= -1.0,
    }


JPX_IPO_URL = "https://www.jpx.co.jp/listing/stocks/new/index.html"
JPX_BASE_URL = "https://www.jpx.co.jp"


def _optional_number(text):
    if text is None:
        return np.nan
    match = re.search(r"\d[\d,]*(?:\.\d+)?", str(text))
    return float(match.group(0).replace(",", "")) if match else np.nan


def _secondary_shares(text):
    main_text = str(text).split("(", 1)[0]
    secondary = _optional_number(main_text)
    oa_match = re.search(r"OA\s*([\d,]+(?:\.\d+)?)", str(text), re.IGNORECASE)
    oa = float(oa_match.group(1).replace(",", "")) if oa_match else 0.0
    return (0.0 if pd.isna(secondary) else secondary), oa


def _pdf_link(cell):
    link = cell.select_one('a[href$=".pdf"]')
    return urljoin(JPX_BASE_URL, link.get("href")) if link else ""


@st.cache_data(ttl=3600, show_spinner=False)
def load_jpx_ipos():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
    }
    try:
        response = requests.get(JPX_IPO_URL, headers=headers, timeout=25)
    except requests.RequestException:
        raise RuntimeError("IPO_DATA_UNAVAILABLE")
    if response.status_code == 429:
        raise RuntimeError("IPO_RATE_LIMIT")
    if response.status_code != 200:
        raise RuntimeError("IPO_DATA_UNAVAILABLE")

    soup = BeautifulSoup(response.content, "html.parser")
    records = []
    pending = None
    for row in soup.select("table tbody tr"):
        cells = row.select("th,td")
        if not cells:
            continue
        dates = re.findall(r"20\d{2}/\d{1,2}/\d{1,2}", cells[0].get_text(" ", strip=True))
        if dates and len(cells) >= 8:
            company_raw = cells[1].get_text(" ", strip=True)
            pending = {
                "listing_date": dates[0],
                "approval_date": dates[1] if len(dates) > 1 else "-",
                "company_name": company_raw.replace("*", "").strip(),
                "technical_listing": "*" in company_raw,
                "code": cells[2].get_text(" ", strip=True),
                "outline_url": _pdf_link(cells[3]),
                "report_url": "",
                "indicated_range": cells[5].get_text(" ", strip=True),
                "public_thousands": _optional_number(cells[6].get_text(" ", strip=True)),
                "trading_unit": _optional_number(cells[7].get_text(" ", strip=True)),
            }
            continue

        if pending is not None and len(cells) >= 5:
            pending["market"] = cells[0].get_text(" ", strip=True)
            pending["report_url"] = _pdf_link(cells[1])
            pending["offer_price"] = _optional_number(cells[3].get_text(" ", strip=True))
            secondary, oa = _secondary_shares(cells[4].get_text(" ", strip=True))
            pending["secondary_thousands"] = secondary
            pending["oa_thousands"] = oa
            if pending["code"] and not pending["technical_listing"]:
                records.append(pending)
            pending = None

    if not records:
        raise RuntimeError("IPO_DATA_UNAVAILABLE")

    today = datetime.now().date()
    records.sort(
        key=lambda item: (
            datetime.strptime(item["listing_date"], "%Y/%m/%d").date() < today,
            abs((datetime.strptime(item["listing_date"], "%Y/%m/%d").date() - today).days),
        )
    )
    return records[:60]


def _extract_pdf_text(url):
    if not url or not url.startswith(JPX_BASE_URL + "/"):
        return ""
    headers = {"User-Agent": "Mozilla/5.0 Chrome/124 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=40)
    except requests.RequestException:
        raise RuntimeError("IPO_DATA_UNAVAILABLE")
    if response.status_code == 429:
        raise RuntimeError("IPO_RATE_LIMIT")
    if response.status_code != 200 or not response.content.startswith(b"%PDF"):
        return ""

    try:
        completed = subprocess.run(
            ["pdftotext", "-layout", "-", "-"],
            input=response.content,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=45,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout:
            return completed.stdout.decode("utf-8", errors="ignore")
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    try:
        reader = PdfReader(BytesIO(response.content))
        return "\n".join((page.extract_text() or "") for page in reader.pages[:15])
    except Exception:
        return ""


def _parse_japanese_number(token):
    value = token.replace(",", "").replace(" ", "")
    negative = "△" in value or value.startswith("-")
    value = value.replace("△", "").lstrip("-")
    try:
        number = float(value)
        return -number if negative else number
    except ValueError:
        return np.nan


def _financial_section(text):
    positions = [match.start() for match in re.finditer(r"主要な経営指標", text)]
    if not positions:
        return text[:20000]
    start = positions[1] if len(positions) > 1 else positions[0]
    return text[start:start + 20000]


def _metric_series(section, labels, units):
    lines = section.splitlines()
    unit_pattern = r"[（(](?:" + "|".join(units) + r")[)）]"
    number_pattern = r"(?:△\s*|-\s*)?\d[\d,]*(?:\.\d+)?"
    for index, line in enumerate(lines):
        if not any(re.search(label, line) for label in labels):
            continue
        for value_line in lines[index:index + 4]:
            unit_match = re.search(unit_pattern, value_line)
            if not unit_match:
                continue
            values = [
                _parse_japanese_number(token)
                for token in re.findall(number_pattern, value_line[unit_match.end():])
            ]
            values = [value for value in values if not pd.isna(value)]
            if values:
                unit = unit_match.group(0)
                scale = 1000000.0 if "百万円" in unit else 1000.0 if "千円" in unit else 1.0
                return values, scale
    return [], 1.0


def _parse_ipo_documents(outline_text, report_text):
    shares_match = re.search(
        r"上\s*場\s*時\s*発\s*行\s*済\s*株\s*式\s*総\s*数\s*([\d,]+)\s*株",
        outline_text,
    )
    shares_outstanding = (
        float(shares_match.group(1).replace(",", "")) if shares_match else np.nan
    )
    business_match = re.search(r"事\s*業\s*の\s*内\s*容\s+([^\r\n]+)", outline_text)
    business = " ".join(business_match.group(1).split()) if business_match else "-"

    section = _financial_section(report_text)
    revenue, revenue_scale = _metric_series(section, [r"売上高", r"売上収益"], ["千円", "百万円"])
    ordinary, ordinary_scale = _metric_series(
        section,
        [r"経常利益", r"経常損失", r"営業利益", r"営業損失"],
        ["千円", "百万円"],
    )
    net_income, net_income_scale = _metric_series(
        section,
        [r"当期純利益", r"当期純損失", r"親会社株主.*当期純利益", r"親会社株主.*当期純損失"],
        ["千円", "百万円"],
    )
    eps_values, _ = _metric_series(
        section,
        [r"１株当たり当期純利益", r"１株当たり当期純損失", r"基本的１株当たり.*利益", r"基本的１株当たり.*損失"],
        ["円"],
    )

    revenue_growth = (
        (revenue[-1] / revenue[-2] - 1) * 100
        if len(revenue) >= 2 and revenue[-2] != 0
        else np.nan
    )
    ordinary_margin = (
        ordinary[-1] * ordinary_scale / (revenue[-1] * revenue_scale) * 100
        if revenue and ordinary and revenue[-1] != 0
        else np.nan
    )
    eps = eps_values[-1] if eps_values else np.nan
    if pd.isna(eps) and net_income and not pd.isna(shares_outstanding) and shares_outstanding > 0:
        eps = net_income[-1] * net_income_scale / shares_outstanding

    return {
        "shares_outstanding": shares_outstanding,
        "business": business,
        "revenue_growth_pct": revenue_growth,
        "ordinary_margin_pct": ordinary_margin,
        "eps": eps,
    }


@st.cache_data(ttl=21600, show_spinner=False)
def load_ipo_document_data(code, outline_url, report_url):
    outline_text = _extract_pdf_text(outline_url)
    report_text = _extract_pdf_text(report_url)
    return _parse_ipo_documents(outline_text, report_text)


def build_ipo_data(record):
    document_data = load_ipo_document_data(
        record["code"],
        record["outline_url"],
        record["report_url"],
    )
    data = dict(record)
    data.update(document_data)

    range_prices = re.findall(r"\d[\d,]*(?:\.\d+)?", record["indicated_range"])
    if not pd.isna(record["offer_price"]):
        effective_price = record["offer_price"]
        price_status = "ipo_price_fixed"
    elif range_prices:
        effective_price = float(range_prices[-1].replace(",", ""))
        price_status = "ipo_price_tentative"
    else:
        effective_price = np.nan
        price_status = "ipo_price_unavailable"

    public_thousands = 0.0 if pd.isna(record["public_thousands"]) else record["public_thousands"]
    total_thousands = public_thousands + record["secondary_thousands"] + record["oa_thousands"]
    secondary_ratio = (
        (record["secondary_thousands"] + record["oa_thousands"]) / total_thousands * 100
        if total_thousands > 0 else np.nan
    )
    shares_outstanding = data["shares_outstanding"]
    market_cap_oku = (
        effective_price * shares_outstanding / 100000000
        if not pd.isna(effective_price) and not pd.isna(shares_outstanding)
        else np.nan
    )
    offering_amount_oku = (
        effective_price * total_thousands / 100000
        if not pd.isna(effective_price) and total_thousands > 0
        else np.nan
    )
    absorption_ratio = (
        offering_amount_oku / market_cap_oku * 100
        if not pd.isna(offering_amount_oku) and not pd.isna(market_cap_oku) and market_cap_oku > 0
        else np.nan
    )
    reference_per = (
        effective_price / data["eps"]
        if not pd.isna(effective_price) and not pd.isna(data["eps"]) and data["eps"] > 0
        else np.nan
    )
    data.update({
        "effective_price": effective_price,
        "price_status": price_status,
        "market_cap_oku": market_cap_oku,
        "offering_amount_oku": offering_amount_oku,
        "secondary_ratio_pct": secondary_ratio,
        "absorption_ratio": absorption_ratio,
        "reference_per": reference_per,
    })
    return data


def evaluate_ipo(data):
    components = {
        "ipo_growth": None,
        "ipo_profitability": None,
        "ipo_valuation": None,
        "ipo_supply_demand": None,
        "ipo_shareholder": None,
    }
    component_max = {
        "ipo_growth": 25,
        "ipo_profitability": 20,
        "ipo_valuation": 20,
        "ipo_supply_demand": 25,
        "ipo_shareholder": 10,
    }

    growth = data["revenue_growth_pct"]
    margin = data["ordinary_margin_pct"]
    per = data["reference_per"]
    absorption = data["absorption_ratio"]
    secondary_ratio = data["secondary_ratio_pct"]

    if not pd.isna(growth):
        components["ipo_growth"] = float(np.interp(growth, [-20, 0, 20, 50], [0, 8, 18, 25]))
    if not pd.isna(margin):
        components["ipo_profitability"] = float(np.interp(margin, [-20, 0, 10, 25], [0, 5, 14, 20]))
    if not pd.isna(data["eps"]):
        if data["eps"] <= 0 or pd.isna(per):
            components["ipo_valuation"] = 2.0
        elif per <= 15:
            components["ipo_valuation"] = 20.0
        elif per <= 25:
            components["ipo_valuation"] = 16.0
        elif per <= 40:
            components["ipo_valuation"] = 10.0
        elif per <= 60:
            components["ipo_valuation"] = 5.0
        else:
            components["ipo_valuation"] = 0.0
    if not pd.isna(absorption):
        if absorption <= 5:
            components["ipo_supply_demand"] = 25.0
        elif absorption <= 10:
            components["ipo_supply_demand"] = 21.0
        elif absorption <= 20:
            components["ipo_supply_demand"] = 15.0
        elif absorption <= 30:
            components["ipo_supply_demand"] = 8.0
        else:
            components["ipo_supply_demand"] = 2.0
    if not pd.isna(secondary_ratio):
        if secondary_ratio <= 20:
            components["ipo_shareholder"] = 10.0
        elif secondary_ratio <= 40:
            components["ipo_shareholder"] = 8.0
        elif secondary_ratio <= 60:
            components["ipo_shareholder"] = 5.0
        elif secondary_ratio <= 80:
            components["ipo_shareholder"] = 2.0
        else:
            components["ipo_shareholder"] = 0.0

    available_keys = [key for key, value in components.items() if value is not None]
    available_max = sum(component_max[key] for key in available_keys)
    confidence = available_max
    total = (
        sum(components[key] for key in available_keys) / available_max * 100
        if available_max > 0 else 0.0
    )

    if not pd.isna(data["eps"]) and data["eps"] <= 0 and (pd.isna(growth) or growth < 10):
        total = min(total, 49)
    if not pd.isna(absorption) and absorption > 30:
        total = min(total, 59)
    if not pd.isna(secondary_ratio) and secondary_ratio > 80:
        total = min(total, 49)
    if confidence < 60:
        total = min(total, 49)
    elif confidence < 80:
        total = min(total, 64)
    total = max(0.0, min(100.0, total))

    if total >= 75:
        decision_key = "ipo_apply_strong"
    elif total >= 65:
        decision_key = "ipo_apply_consider"
    elif total >= 50:
        decision_key = "ipo_apply_selective"
    elif total >= 35:
        decision_key = "ipo_caution"
    else:
        decision_key = "ipo_skip"

    positive_flags = []
    if not pd.isna(growth) and growth >= 20:
        positive_flags.append("ipo_strength_growth")
    if not pd.isna(margin) and margin >= 10:
        positive_flags.append("ipo_strength_profit")
    if not pd.isna(per) and per <= 25:
        positive_flags.append("ipo_strength_valuation")
    if not pd.isna(absorption) and absorption <= 10:
        positive_flags.append("ipo_strength_supply")
    if not pd.isna(secondary_ratio) and secondary_ratio <= 40:
        positive_flags.append("ipo_strength_primary")

    risk_flags = []
    if not pd.isna(data["eps"]) and data["eps"] <= 0:
        risk_flags.append("ipo_risk_loss")
    if not pd.isna(per) and per > 50:
        risk_flags.append("ipo_risk_expensive")
    if not pd.isna(absorption) and absorption > 25:
        risk_flags.append("ipo_risk_absorption")
    if not pd.isna(secondary_ratio) and secondary_ratio > 60:
        risk_flags.append("ipo_risk_secondary")
    if data["price_status"] == "ipo_price_tentative":
        risk_flags.append("ipo_risk_tentative")
    if confidence < 100:
        risk_flags.append("ipo_risk_missing")

    return {
        "score": total,
        "decision_key": decision_key,
        "per": per,
        "absorption_ratio": absorption,
        "confidence": confidence,
        "components": components,
        "component_max": component_max,
        "positive_flags": positive_flags,
        "risk_flags": risk_flags,
    }


def build_position_plan(result, capital, risk_percent, max_position_percent):
    entry = result["buy1"]
    risk_review_price = result["risk_review_price"]
    risk_per_share = max(0.0, entry - risk_review_price)
    risk_budget = max(0.0, capital * risk_percent / 100.0)
    allocation_limit = max(0.0, capital * max_position_percent / 100.0)

    shares_by_risk = math.floor(risk_budget / risk_per_share) if risk_per_share > 0 else 0
    shares_by_allocation = math.floor(allocation_limit / entry) if entry > 0 else 0
    quantity = min(shares_by_risk, shares_by_allocation)

    lot_size = 100 if result["ticker"].endswith(".T") else 1
    quantity = max(0, math.floor(quantity / lot_size) * lot_size)
    position_value = quantity * entry
    estimated_loss = quantity * risk_per_share

    return {
        "quantity": quantity,
        "lot_size": lot_size,
        "position_value": position_value,
        "risk_budget": risk_budget,
        "estimated_loss": estimated_loss,
    }


def analyze(ticker, weights, fx_sensitivity):
    hist, info, cal, data_source, fallback_used = load_price(ticker)

    close = hist["Close"].dropna()
    market = compute_market_metrics(hist)
    px = float(close.iloc[-1])
    ma20 = float(close.tail(20).mean()) if len(close) >= 20 else np.nan
    ma50 = float(close.tail(50).mean()) if len(close) >= 50 else np.nan
    ma200 = float(close.tail(200).mean()) if len(close) >= 200 else np.nan
    high52 = float(hist["High"].max())
    low52 = float(hist["Low"].min())

    company_name = info.get("longName") or info.get("shortName") or ticker
    currency = info.get("currency") or "-"
    sector = info.get("sector") or "-"
    exchange = info.get("exchange") or "-"
    yen = load_yen_context()
    fx = evaluate_fx(ticker, currency, fx_sensitivity, yen)

    rev_growth = safe_num(info.get("revenueGrowth"))
    earn_growth = safe_num(info.get("earningsGrowth"))
    op_margin = safe_num(info.get("operatingMargins"))
    forward_pe = safe_num(info.get("forwardPE"))
    trailing_pe = safe_num(info.get("trailingPE"))
    debt_equity = safe_num(info.get("debtToEquity"))
    current_ratio = safe_num(info.get("currentRatio"))
    return_on_equity = safe_num(info.get("returnOnEquity"))
    free_cash_flow = safe_num(info.get("freeCashflow"))
    market_cap = safe_num(info.get("marketCap"))
    beta = safe_num(info.get("beta"))
    free_cash_flow_yield = (
        free_cash_flow / market_cap * 100
        if not pd.isna(free_cash_flow) and not pd.isna(market_cap) and market_cap > 0
        else np.nan
    )

    # --- Fundamental score (-5 to +5) ---
    f = 0.0
    if not pd.isna(rev_growth):
        f += np.interp(rev_growth, [-0.2, 0.0, 0.15, 0.4], [-2, 0, 2, 3])
    if not pd.isna(earn_growth):
        f += np.interp(earn_growth, [-0.3, 0.0, 0.2, 0.6], [-2, 0, 2, 3])
    if not pd.isna(op_margin):
        f += np.interp(op_margin, [-0.1, 0.05, 0.2, 0.4], [-2, 0, 1, 2])
    if not pd.isna(return_on_equity):
        f += np.interp(return_on_equity, [-0.2, 0.0, 0.15, 0.35], [-2, 0, 1, 2])
    if not pd.isna(free_cash_flow_yield):
        if free_cash_flow_yield > 5:
            f += 1
        elif free_cash_flow_yield < 0:
            f -= 1
    f = normalize_component(f / 2.5)

    # --- Valuation score (-5 to +5); not sector-perfect, deliberately conservative ---
    v = 0.0
    pe = forward_pe if not pd.isna(forward_pe) else trailing_pe
    if not pd.isna(pe) and pe > 0:
        if pe < 15: v += 3
        elif pe < 25: v += 2
        elif pe < 35: v += 1
        elif pe < 50: v += 0
        elif pe < 80: v -= 1.5
        else: v -= 3
    if not pd.isna(debt_equity):
        if debt_equity < 50: v += 1
        elif debt_equity > 200: v -= 1.5
    if not pd.isna(current_ratio):
        if current_ratio >= 1.5: v += 0.5
        elif current_ratio < 0.8: v -= 0.5
    if not pd.isna(free_cash_flow_yield):
        if free_cash_flow_yield >= 5: v += 1
        elif free_cash_flow_yield < 0: v -= 1
    v = normalize_component(v)

    # --- Trend / entry score: avoid rewarding a falling price by itself ---
    t = 0.0
    if not pd.isna(ma50) and not pd.isna(ma200):
        t += 1.5 if ma50 > ma200 else -1.5
    if not pd.isna(ma200):
        t += 1.0 if px > ma200 else -1.0
    if not pd.isna(ma50):
        t += 0.5 if px > ma50 else -0.5
    if not pd.isna(market["momentum_3m"]):
        if market["momentum_3m"] > 10: t += 1.0
        elif market["momentum_3m"] < -10: t -= 1.0
    if not pd.isna(market["rsi14"]):
        if 45 <= market["rsi14"] <= 65: t += 0.5
        elif market["rsi14"] > 75: t -= 0.75
        elif market["rsi14"] < 30: t -= 0.5
    t = normalize_component(t)

    # --- Event risk (earnings proximity) ---
    event = 0.0
    earnings_date = None
    try:
        if isinstance(cal, dict):
            e = cal.get("Earnings Date")
            if isinstance(e, list) and e:
                earnings_date = pd.Timestamp(e[0]).to_pydatetime()
        elif isinstance(cal, pd.DataFrame) and "Earnings Date" in cal.index:
            earnings_date = pd.Timestamp(cal.loc["Earnings Date"].iloc[0]).to_pydatetime()
    except Exception:
        earnings_date = None

    if earnings_date is not None:
        now = datetime.now(timezone.utc)
        if earnings_date.tzinfo is None:
            earnings_date = earnings_date.replace(tzinfo=timezone.utc)
        days = (earnings_date - now).total_seconds()/86400
        if 0 <= days <= 3:
            event = -2.0
        elif 3 < days <= 7:
            event = -1.0

    pe_for_confidence = forward_pe if not pd.isna(forward_pe) else trailing_pe
    confidence_inputs = [
        rev_growth, earn_growth, op_margin, return_on_equity,
        pe_for_confidence, debt_equity, current_ratio, free_cash_flow_yield,
        ma200, market["rsi14"], market["atr14"], market["annual_volatility"],
    ]
    available_inputs = sum(0 if pd.isna(value) else 1 for value in confidence_inputs)
    confidence = round(available_inputs / len(confidence_inputs) * 100)

    drawdown_from_high = pct(px, high52)
    downtrend = (
        not pd.isna(ma50) and not pd.isna(ma200)
        and px < ma200 and ma50 < ma200
    )

    risk_flags = []
    if downtrend:
        risk_flags.append("risk_downtrend")
    if not pd.isna(market["annual_volatility"]) and market["annual_volatility"] > 0.55:
        risk_flags.append("risk_high_vol")
    if not pd.isna(drawdown_from_high) and drawdown_from_high < -35:
        risk_flags.append("risk_drawdown")
    if (
        (not pd.isna(debt_equity) and debt_equity > 200)
        or (not pd.isna(current_ratio) and current_ratio < 0.8)
    ):
        risk_flags.append("risk_balance")
    if event < 0:
        risk_flags.append("risk_earnings")
    if confidence < 60:
        risk_flags.append("risk_low_confidence")
    if not pd.isna(market["rsi14"]) and market["rsi14"] > 75:
        risk_flags.append("risk_overbought")
    if fx["headwind"]:
        risk_flags.append("risk_fx_headwind")

    positive_flags = []
    if not pd.isna(ma50) and not pd.isna(ma200) and px > ma50 > ma200:
        positive_flags.append("positive_uptrend")
    if (
        not pd.isna(rev_growth) and not pd.isna(earn_growth)
        and rev_growth > 0.10 and earn_growth > 0.10
    ):
        positive_flags.append("positive_growth")
    if not pd.isna(free_cash_flow) and free_cash_flow > 0:
        positive_flags.append("positive_cashflow")
    if (
        not pd.isna(debt_equity) and not pd.isna(current_ratio)
        and debt_equity < 100 and current_ratio >= 1.2
    ):
        positive_flags.append("positive_balance")
    if not pd.isna(pe_for_confidence) and 0 < pe_for_confidence < 30:
        positive_flags.append("positive_valuation")
    if fx["tailwind"]:
        positive_flags.append("positive_fx_tailwind")

    # Weighted total
    total = (
        f * weights["fundamental"] +
        v * weights["valuation"] +
        t * weights["technical"] +
        fx["score"] * weights["fx"] +
        event * weights["event"]
    )
    max_abs = (
        5 * (weights["fundamental"] + weights["valuation"] + weights["technical"])
        + 2 * weights["fx"]
        + 2 * weights["event"]
    )
    score100 = 50 + 50 * (total / max_abs)
    score100 = max(0, min(100, score100))

    # Risk gates: incomplete data or a serious risk should prevent a strong buy label.
    if confidence < 45 or event <= -2:
        score100 = min(score100, 54)
    elif confidence < 60:
        score100 = min(score100, 67)
    if downtrend:
        score100 = min(score100, 54)
    if (
        "risk_high_vol" in risk_flags
        and "risk_drawdown" in risk_flags
    ):
        score100 = min(score100, 59)

    if score100 >= 68:
        decision_key = "buy_candidate"
    elif score100 >= 55:
        decision_key = "buy_small"
    elif score100 >= 45:
        decision_key = "wait_split"
    elif score100 >= 32:
        decision_key = "caution"
    else:
        decision_key = "skip"

    # Practical staged buy zones based on ATR, fixed at analysis time.
    if not pd.isna(market["atr14"]) and px > 0:
        base_pullback = market["atr14"] / px
    else:
        annual_volatility = market["annual_volatility"] if not pd.isna(market["annual_volatility"]) else 0.35
        base_pullback = annual_volatility / np.sqrt(252) * 1.5
    base_pullback = max(0.02, min(0.08, base_pullback))
    buy1 = px * (1 - base_pullback * 0.5)
    buy2 = px * (1 - base_pullback * 1.5)
    buy3 = px * (1 - base_pullback * 3.0)

    atr_risk = 2 * market["atr14"] if not pd.isna(market["atr14"]) else buy1 * 0.08
    risk_distance = max(buy1 * 0.07, atr_risk)
    risk_distance = min(buy1 * 0.20, risk_distance)
    risk_review_price = max(0.01, buy1 - risk_distance)

    return {
        "ticker": ticker,
        "company_name": company_name,
        "currency": currency,
        "sector": sector,
        "exchange": exchange,
        "analysis_time": datetime.now(timezone.utc),
        "data_source": data_source,
        "fallback_used": fallback_used,
        "price": px,
        "ma20": ma20, "ma50": ma50, "ma200": ma200,
        "high52": high52, "low52": low52,
        "rev_growth": rev_growth, "earn_growth": earn_growth,
        "op_margin": op_margin, "forward_pe": forward_pe, "trailing_pe": trailing_pe,
        "debt_equity": debt_equity, "current_ratio": current_ratio,
        "return_on_equity": return_on_equity,
        "free_cash_flow_yield": free_cash_flow_yield,
        "beta": beta,
        "fundamental": f, "valuation": v, "technical": t,
        "fx_score": fx["score"], "event": event,
        "yen": yen, "fx": fx,
        "score": score100, "decision_key": decision_key,
        "confidence": confidence,
        "risk_flags": risk_flags,
        "positive_flags": positive_flags,
        "drawdown_from_high": drawdown_from_high,
        "buy1": buy1, "buy2": buy2, "buy3": buy3,
        "risk_review_price": risk_review_price,
        "earnings_date": earnings_date,
        "hist": hist,
        **market,
    }

with st.sidebar:
    selected_language = st.selectbox(
        "🌐 Language / 言語 / भाषा",
        list(LANGUAGES.keys()),
        key="language",
    )
    language_code = LANGUAGES[selected_language]["code"]

    menu_keys = ["stock_analysis", "ipo_analysis"]
    menu_labels = [tr(key) for key in menu_keys]
    selected_menu = st.radio(
        tr("tool_mode"),
        menu_labels,
        key=f"tool_mode_{language_code}",
    )
    tool_mode = menu_keys[menu_labels.index(selected_menu)]

    if tool_mode == "stock_analysis":
        st.subheader(tr("investment_style"))
        style_keys = ["long_stable", "growth", "short_entry"]
        style_labels = [tr(key) for key in style_keys]
        selected_style = st.radio(
            tr("investment_style"),
            style_labels,
            index=0,
            label_visibility="collapsed",
            key=f"investment_style_{language_code}",
        )
        mode = style_keys[style_labels.index(selected_style)]
        if mode == "long_stable":
            weights = dict(fundamental=4, valuation=3, technical=1.5, fx=2, event=2)
        elif mode == "growth":
            weights = dict(fundamental=4, valuation=2, technical=2, fx=1.5, event=2)
        else:
            weights = dict(fundamental=2, valuation=1.5, technical=4, fx=2.5, event=3)

        fx_keys = ["fx_auto", "fx_exporter", "fx_importer", "fx_neutral"]
        fx_labels = [tr(key) for key in fx_keys]
        selected_fx = st.selectbox(
            tr("fx_sensitivity"),
            fx_labels,
            help=tr("fx_auto_help"),
            key=f"fx_sensitivity_{language_code}",
        )
        fx_sensitivity = fx_keys[fx_labels.index(selected_fx)]

        st.subheader(tr("risk_settings"))
        available_capital = st.number_input(
            tr("capital_label"),
            min_value=0.0,
            value=100000.0,
            step=10000.0,
            help=tr("capital_help"),
            key="available_capital",
        )
        risk_percent = st.slider(
            tr("risk_per_trade"),
            min_value=0.25,
            max_value=3.0,
            value=0.75,
            step=0.25,
            key="risk_percent",
        )
        max_position_percent = st.slider(
            tr("max_position"),
            min_value=1,
            max_value=25,
            value=10,
            step=1,
            key="max_position_percent",
        )

if tool_mode == "stock_analysis":
    st.title(f"📈 {tr('title')}")
    st.caption(tr("caption"))

    ticker = st.text_input(tr("ticker"), value="NVDA", help=tr("ticker_help"), key="ticker_input")
    run = st.button(tr("analyze"), type="primary", key="analyze_button")

    if run:
        try:
            with st.spinner(tr("loading")):
                r = analyze(ticker.strip().upper(), weights, fx_sensitivity)

            st.subheader(f"{r['company_name']} ({r['ticker']})")
            st.caption(f"{r['exchange']} | {r['sector']} | {tr('currency')}: {r['currency']}")
            st.caption(f"{tr('as_of')}: {r['analysis_time'].strftime('%Y-%m-%d %H:%M')} UTC")
            st.caption(f"{tr('data_source')}: {r['data_source']}")
            if r["fallback_used"]:
                st.warning(tr("fallback_notice"))

            c1, c2, c3, c4 = st.columns(4)
            c1.metric(tr("current_price"), f"{r['price']:,.2f} {r['currency']}")
            c2.metric(tr("total_score"), f"{r['score']:.0f}/100")
            c3.metric(tr("decision"), tr(r["decision_key"]))
            ed = r["earnings_date"]
            c4.metric(tr("next_earnings"), ed.strftime("%Y-%m-%d") if ed else tr("unavailable"))

            st.subheader(tr("yen_dashboard"))
            if r["yen"]["available"]:
                y1, y2, y3, y4 = st.columns(4)
                y1.metric(tr("usd_jpy"), f"{r['yen']['rate']:.2f} JPY")
                y2.metric(tr("yen_regime"), tr(r["yen"]["regime"]))
                y3.metric(tr("yen_3m_change"), f"{r['yen']['change_3m']:+.1f}%")
                y4.metric(tr("fx_action"), tr(r["fx"]["action_key"]))
                st.caption(
                    f"{tr('yen_position_1y')}: {r['yen']['position_1y']:.0f}% | "
                    f"{tr('fx_sensitivity')}: {tr(r['fx']['sensitivity'])} | "
                    f"{tr('data_source')}: {r['yen']['source']}"
                )
            else:
                st.warning(tr("fx_unavailable"))
            st.info(tr("fx_disclaimer"))

            st.subheader(tr("risk_dashboard"))
            q1, q2, q3, q4 = st.columns(4)
            q1.metric(tr("data_confidence"), f"{r['confidence']}%")
            q2.metric(
                tr("annual_volatility"),
                f"{r['annual_volatility']*100:.1f}%" if not pd.isna(r["annual_volatility"]) else "-",
            )
            q3.metric(
                tr("max_drawdown"),
                f"{r['max_drawdown']:.1f}%" if not pd.isna(r["max_drawdown"]) else "-",
            )
            q4.metric(tr("rsi14"), f"{r['rsi14']:.1f}" if not pd.isna(r["rsi14"]) else "-")
            st.caption(tr("confidence_caption"))

            reason_left, reason_right = st.columns(2)
            with reason_left:
                st.markdown(f"**{tr('strengths')}**")
                if r["positive_flags"]:
                    for flag in r["positive_flags"]:
                        st.success(tr(flag))
                else:
                    st.info(tr("no_strengths"))
            with reason_right:
                st.markdown(f"**{tr('risks')}**")
                if r["risk_flags"]:
                    for flag in r["risk_flags"]:
                        st.warning(tr(flag))
                else:
                    st.success(tr("no_risks"))

            st.subheader(tr("buy_zones"))
            z1, z2, z3 = st.columns(3)
            z1.metric(tr("buy1"), f"{r['buy1']:.2f}")
            z2.metric(tr("buy2"), f"{r['buy2']:.2f}")
            z3.metric(tr("buy3"), f"{r['buy3']:.2f}")
            st.caption(tr("buy_caption"))

            position = build_position_plan(r, available_capital, risk_percent, max_position_percent)
            st.subheader(tr("position_plan"))
            p1, p2, p3 = st.columns(3)
            p1.metric(tr("planned_entry"), f"{r['buy1']:,.2f} {r['currency']}")
            p2.metric(tr("risk_review_price"), f"{r['risk_review_price']:,.2f} {r['currency']}")
            p3.metric(tr("suggested_shares"), f"{position['quantity']:,}")
            p4, p5 = st.columns(2)
            p4.metric(tr("position_value"), f"{position['position_value']:,.2f} {r['currency']}")
            p5.metric(tr("risk_budget"), f"{position['risk_budget']:,.2f} {r['currency']}")
            st.warning(tr("stop_warning"))

            st.subheader(tr("score_breakdown"))
            comp = pd.DataFrame({
                tr("item"): [tr("fundamental"), tr("valuation"), tr("technical"), tr("currency_factor"), tr("event")],
                tr("score"): [r["fundamental"], r["valuation"], r["technical"], r["fx_score"], r["event"]],
            })
            st.dataframe(comp, use_container_width=True, hide_index=True)

            st.subheader(tr("key_metrics"))
            metrics = pd.DataFrame({
                tr("indicator"): [
                    tr("revenue_growth"), tr("earnings_growth"), tr("operating_margin"), tr("roe"),
                    tr("forward_pe"), tr("fcf_yield"), tr("debt_equity"), tr("current_ratio"), tr("beta"),
                    tr("ma50"), tr("ma200"), tr("atr14"), tr("momentum_3m"), tr("volume_ratio"),
                    tr("high52"), tr("low52"),
                ],
                tr("value"): [
                    f"{r['rev_growth']*100:.1f}%" if not pd.isna(r['rev_growth']) else "-",
                    f"{r['earn_growth']*100:.1f}%" if not pd.isna(r['earn_growth']) else "-",
                    f"{r['op_margin']*100:.1f}%" if not pd.isna(r['op_margin']) else "-",
                    f"{r['return_on_equity']*100:.1f}%" if not pd.isna(r['return_on_equity']) else "-",
                    f"{r['forward_pe']:.1f}" if not pd.isna(r['forward_pe']) else "-",
                    f"{r['free_cash_flow_yield']:.1f}%" if not pd.isna(r['free_cash_flow_yield']) else "-",
                    f"{r['debt_equity']:.1f}" if not pd.isna(r['debt_equity']) else "-",
                    f"{r['current_ratio']:.2f}" if not pd.isna(r['current_ratio']) else "-",
                    f"{r['beta']:.2f}" if not pd.isna(r['beta']) else "-",
                    f"{r['ma50']:.2f}" if not pd.isna(r['ma50']) else "-",
                    f"{r['ma200']:.2f}" if not pd.isna(r['ma200']) else "-",
                    f"{r['atr14']:.2f}" if not pd.isna(r['atr14']) else "-",
                    f"{r['momentum_3m']:.1f}%" if not pd.isna(r['momentum_3m']) else "-",
                    f"{r['volume_ratio']:.2f}x" if not pd.isna(r['volume_ratio']) else "-",
                    f"{r['high52']:.2f}", f"{r['low52']:.2f}",
                ],
            })
            st.dataframe(metrics, use_container_width=True, hide_index=True)

            st.subheader(tr("chart"))
            chart_data = r["hist"][["Close"]].copy()
            chart_data[tr("ma50")] = chart_data["Close"].rolling(50).mean()
            chart_data[tr("ma200")] = chart_data["Close"].rolling(200).mean()
            chart_data = chart_data.rename(columns={"Close": tr("close")})
            st.line_chart(chart_data)

        except Exception as error:
            st.error(f"{tr('analysis_failed')}: {localized_error(error)}")

else:
    st.title(f"📊 {tr('ipo_title')}")
    st.caption(tr("ipo_intro"))
    source_col, refresh_col = st.columns([3, 1])
    with source_col:
        st.markdown(f"[{tr('ipo_primary_source')}]({JPX_IPO_URL})")
    with refresh_col:
        if st.button(tr("ipo_refresh"), key="refresh_ipo"):
            load_jpx_ipos.clear()
            load_ipo_document_data.clear()
            st.rerun()
    st.info(tr("ipo_auto_note"))

    ipo_records = []
    try:
        with st.spinner(tr("ipo_loading_list")):
            ipo_records = load_jpx_ipos()
    except Exception as error:
        st.error(f"{tr('ipo_fetch_failed')}: {localized_error(error)}")

    if ipo_records:
        ipo_labels = [
            f"{record['listing_date']} | {record['code']} | {record['company_name']}"
            for record in ipo_records
        ]
        selected_ipo_label = st.selectbox(
            tr("ipo_select_company"),
            ipo_labels,
            key=f"ipo_company_{language_code}",
        )
        selected_record = ipo_records[ipo_labels.index(selected_ipo_label)]
        evaluate_button = st.button(tr("ipo_evaluate"), type="primary", key="evaluate_ipo_auto")

        if evaluate_button:
            try:
                with st.spinner(tr("ipo_loading_details")):
                    ipo_data = build_ipo_data(selected_record)
                    ipo = evaluate_ipo(ipo_data)

                st.subheader(f"{ipo_data['company_name']} ({ipo_data['code']})")
                st.caption(
                    f"{tr('ipo_listing_date')}: {ipo_data['listing_date']} | "
                    f"{tr('ipo_approval_date')}: {ipo_data['approval_date']} | "
                    f"{tr('ipo_market')}: {ipo_data['market']}"
                )
                if ipo_data["business"] != "-":
                    st.markdown(f"**{tr('ipo_business')}**: {ipo_data['business']}")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric(tr("ipo_total_score"), f"{ipo['score']:.0f}/100")
                m2.metric(tr("ipo_decision"), tr(ipo["decision_key"]))
                m3.metric(tr("ipo_data_confidence"), f"{ipo['confidence']:.0f}%")
                m4.metric(tr("ipo_price_status"), tr(ipo_data["price_status"]))

                n1, n2, n3, n4 = st.columns(4)
                n1.metric(
                    tr("ipo_offer_price"),
                    f"{ipo_data['effective_price']:,.0f} JPY" if not pd.isna(ipo_data["effective_price"]) else "-",
                )
                n2.metric(tr("ipo_per"), f"{ipo['per']:.1f}x" if not pd.isna(ipo["per"]) else "-")
                n3.metric(
                    tr("ipo_offering_amount"),
                    f"{ipo_data['offering_amount_oku']:.1f}" if not pd.isna(ipo_data["offering_amount_oku"]) else "-",
                )
                n4.metric(
                    tr("ipo_absorption_ratio"),
                    f"{ipo['absorption_ratio']:.1f}%" if not pd.isna(ipo["absorption_ratio"]) else "-",
                )

                auto_metrics = pd.DataFrame({
                    tr("indicator"): [
                        tr("ipo_public_shares"), tr("ipo_secondary_shares"), tr("ipo_oa_shares"),
                        tr("ipo_shares_outstanding"), tr("ipo_revenue_growth"), tr("ipo_operating_margin"),
                        tr("ipo_eps"), tr("ipo_market_cap"), tr("ipo_secondary_ratio"),
                    ],
                    tr("value"): [
                        f"{ipo_data['public_thousands']:,.1f}" if not pd.isna(ipo_data["public_thousands"]) else "-",
                        f"{ipo_data['secondary_thousands']:,.1f}",
                        f"{ipo_data['oa_thousands']:,.1f}",
                        f"{ipo_data['shares_outstanding']:,.0f}" if not pd.isna(ipo_data["shares_outstanding"]) else "-",
                        f"{ipo_data['revenue_growth_pct']:.1f}%" if not pd.isna(ipo_data["revenue_growth_pct"]) else "-",
                        f"{ipo_data['ordinary_margin_pct']:.1f}%" if not pd.isna(ipo_data["ordinary_margin_pct"]) else "-",
                        f"{ipo_data['eps']:.2f}" if not pd.isna(ipo_data["eps"]) else "-",
                        f"{ipo_data['market_cap_oku']:.1f}" if not pd.isna(ipo_data["market_cap_oku"]) else "-",
                        f"{ipo_data['secondary_ratio_pct']:.1f}%" if not pd.isna(ipo_data["secondary_ratio_pct"]) else "-",
                    ],
                })
                st.dataframe(auto_metrics, use_container_width=True, hide_index=True)

                if ipo["confidence"] < 100:
                    st.warning(tr("ipo_missing_warning"))

                st.subheader(tr("ipo_components"))
                component_table = pd.DataFrame({
                    tr("item"): [tr(key) for key in ipo["components"].keys()],
                    tr("score"): [
                        f"{value:.1f}/{ipo['component_max'][key]}" if value is not None else "-"
                        for key, value in ipo["components"].items()
                    ],
                })
                st.dataframe(component_table, use_container_width=True, hide_index=True)

                ipo_left, ipo_right = st.columns(2)
                with ipo_left:
                    st.markdown(f"**{tr('strengths')}**")
                    if ipo["positive_flags"]:
                        for flag in ipo["positive_flags"]:
                            st.success(tr(flag))
                    else:
                        st.info(tr("no_strengths"))
                with ipo_right:
                    st.markdown(f"**{tr('risks')}**")
                    if ipo["risk_flags"]:
                        for flag in ipo["risk_flags"]:
                            st.warning(tr(flag))
                    else:
                        st.success(tr("no_risks"))

                st.markdown(f"**{tr('ipo_source_documents')}**")
                source_links = []
                if ipo_data["outline_url"]:
                    source_links.append(f"[{tr('ipo_outline')}]({ipo_data['outline_url']})")
                if ipo_data["report_url"]:
                    source_links.append(f"[{tr('ipo_report')}]({ipo_data['report_url']})")
                st.markdown(" | ".join(source_links) if source_links else "-")
            except Exception as error:
                st.error(f"{tr('ipo_fetch_failed')}: {localized_error(error)}")
    else:
        st.warning(tr("ipo_no_data"))

    st.warning(tr("ipo_disclaimer"))

st.divider()
st.caption(tr("footer"))
