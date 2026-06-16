from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'logistics-secret-2026')

# PyInstaller EXE: EXE 위치 기준 / 스크립트: 상위 폴더(데이터 파일 위치) 기준
def _base_dir():
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # 스크립트는 LogisticsWeb/LogisticsWeb/ 안에 있고 데이터는 한 단계 위에 있음
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_BASE = _base_dir()

DATA_PATH   = os.environ.get('DATA_PATH',   os.path.join(_BASE, 'data.json'))
CMD_PATH    = os.environ.get('CMD_PATH',    os.path.join(_BASE, 'commands.txt'))
ORDERS_PATH = os.environ.get('ORDERS_PATH', os.path.join(_BASE, 'orders.json'))
USERS_PATH  = os.environ.get('USERS_PATH',  os.path.join(_BASE, 'users.json'))

INTRO_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>물류창고 자동화 시스템</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;}
    :root{
      --bg:#0f172a;--card:#162032;--border:rgba(255,255,255,.07);
      --text:#e2e8f0;--muted:#64748b;--accent:#38bdf8;
      --green:#22c55e;--orange:#f97316;--purple:#a78bfa;
    }
    body{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;overflow-x:hidden;}

    /* ── NAV ── */
    nav{
      position:fixed;top:0;left:0;right:0;z-index:100;
      display:flex;align-items:center;justify-content:space-between;
      padding:.9rem 3rem;background:rgba(15,23,42,.85);
      backdrop-filter:blur(12px);border-bottom:1px solid var(--border);
    }
    .nav-logo{font-size:1.05rem;font-weight:800;color:var(--accent);}
    .nav-login{
      padding:.45rem 1.2rem;border-radius:8px;background:#2563eb;
      color:#fff;font-size:.85rem;font-weight:600;text-decoration:none;
      transition:background .15s;
    }
    .nav-login:hover{background:#1d4ed8;}

    /* ── HERO ── */
    .hero{
      min-height:100vh;display:flex;flex-direction:column;
      align-items:center;justify-content:center;text-align:center;
      padding:6rem 2rem 4rem;position:relative;overflow:hidden;
    }
    .hero::before{
      content:'';position:absolute;inset:0;
      background:radial-gradient(ellipse 80% 60% at 50% 30%, rgba(56,189,248,.08) 0%, transparent 70%);
      pointer-events:none;
    }
    .hero-badge{
      display:inline-flex;align-items:center;gap:.4rem;
      background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.2);
      color:var(--accent);padding:.35rem .9rem;border-radius:999px;
      font-size:.78rem;font-weight:600;margin-bottom:1.5rem;
    }
    .hero h1{
      font-size:clamp(2.2rem,5vw,3.8rem);font-weight:900;
      line-height:1.15;margin-bottom:1.2rem;
      background:linear-gradient(135deg,#e2e8f0 0%,#38bdf8 100%);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    }
    .hero p{
      font-size:1.1rem;color:var(--muted);max-width:560px;
      line-height:1.7;margin-bottom:2.5rem;
    }
    .hero-btns{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;}
    .btn-primary{
      padding:.75rem 2rem;border-radius:10px;background:#2563eb;
      color:#fff;font-size:.95rem;font-weight:700;text-decoration:none;
      transition:all .15s;border:none;cursor:pointer;
    }
    .btn-primary:hover{background:#1d4ed8;transform:translateY(-1px);}
    .btn-ghost{
      padding:.75rem 2rem;border-radius:10px;
      border:1px solid var(--border);color:var(--muted);
      font-size:.95rem;font-weight:600;text-decoration:none;
      transition:all .15s;
    }
    .btn-ghost:hover{border-color:var(--accent);color:var(--accent);}

    /* ── STATS BAR ── */
    .stats-bar{
      display:flex;justify-content:center;gap:3rem;flex-wrap:wrap;
      padding:2rem;border-top:1px solid var(--border);border-bottom:1px solid var(--border);
      background:rgba(22,32,50,.6);
    }
    .stat-item{text-align:center;}
    .stat-item .val{font-size:1.8rem;font-weight:800;color:var(--accent);}
    .stat-item .lbl{font-size:.78rem;color:var(--muted);margin-top:.2rem;}

    /* ── FEATURES ── */
    .section{padding:5rem 2rem;max-width:1100px;margin:0 auto;}
    .section-label{
      font-size:.78rem;font-weight:700;color:var(--accent);
      text-transform:uppercase;letter-spacing:.1em;margin-bottom:.8rem;
    }
    .section h2{font-size:2rem;font-weight:800;margin-bottom:.8rem;}
    .section .sub{font-size:1rem;color:var(--muted);margin-bottom:3rem;max-width:500px;}
    .features{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.2rem;}
    .feat-card{
      background:var(--card);border:1px solid var(--border);
      border-radius:14px;padding:1.6rem;
      transition:border-color .2s,transform .2s;
    }
    .feat-card:hover{border-color:rgba(56,189,248,.3);transform:translateY(-3px);}
    .feat-icon{font-size:1.8rem;margin-bottom:.8rem;}
    .feat-card h3{font-size:1rem;font-weight:700;margin-bottom:.5rem;}
    .feat-card p{font-size:.85rem;color:var(--muted);line-height:1.6;}
    .feat-tag{
      display:inline-block;margin-top:.8rem;padding:.2rem .6rem;
      border-radius:999px;font-size:.7rem;font-weight:600;
    }
    .tag-blue{background:rgba(56,189,248,.12);color:var(--accent);}
    .tag-green{background:rgba(34,197,94,.12);color:var(--green);}
    .tag-orange{background:rgba(249,115,22,.12);color:var(--orange);}
    .tag-purple{background:rgba(167,139,250,.12);color:var(--purple);}

    /* ── FLOW ── */
    .flow-wrap{background:rgba(22,32,50,.5);border-radius:16px;padding:2.5rem;border:1px solid var(--border);}
    .flow{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;justify-content:center;margin-top:1.5rem;}
    .flow-step{
      text-align:center;background:var(--card);border:1px solid var(--border);
      border-radius:12px;padding:1.2rem 1.5rem;min-width:130px;
    }
    .flow-step .step-icon{font-size:1.6rem;margin-bottom:.4rem;}
    .flow-step .step-name{font-size:.82rem;font-weight:600;}
    .flow-step .step-sub{font-size:.72rem;color:var(--muted);margin-top:.2rem;}
    .flow-arrow{color:var(--muted);font-size:1.2rem;}

    /* ── CTA ── */
    .cta{
      text-align:center;padding:5rem 2rem;
      background:linear-gradient(180deg,transparent,rgba(37,99,235,.06));
    }
    .cta h2{font-size:2rem;font-weight:800;margin-bottom:.8rem;}
    .cta p{color:var(--muted);margin-bottom:2rem;font-size:1rem;}

    /* ── FOOTER ── */
    footer{
      text-align:center;padding:1.5rem;border-top:1px solid var(--border);
      font-size:.78rem;color:var(--muted);
    }

    /* ── CODE SECTION ── */
    .code-tab{
      padding:.5rem 1.1rem;border-radius:8px 8px 0 0;border:1px solid var(--border);
      border-bottom:none;background:rgba(255,255,255,.03);color:var(--muted);
      font-size:.82rem;font-weight:600;cursor:pointer;transition:all .15s;
    }
    .code-tab.active{background:var(--card);color:var(--accent);border-color:rgba(56,189,248,.3);}
    .code-tab:hover:not(.active){color:var(--text);background:rgba(255,255,255,.06);}
    .code-panel{
      background:var(--card);border:1px solid rgba(56,189,248,.2);
      border-radius:0 12px 12px 12px;overflow:hidden;
    }
    .code-pane{display:none;grid-template-columns:1fr 1.3fr;gap:0;}
    .code-pane.active{display:grid;}
    .code-desc{
      padding:1.8rem;border-right:1px solid var(--border);
    }
    .code-desc h3{font-size:1rem;font-weight:700;margin-bottom:.7rem;color:var(--text);}
    .code-desc p{font-size:.84rem;color:var(--muted);line-height:1.7;margin-bottom:1rem;}
    .code-desc ul{padding-left:1.1rem;font-size:.82rem;color:var(--muted);line-height:2;}
    .code-desc code{
      background:rgba(56,189,248,.1);color:var(--accent);
      padding:.1rem .4rem;border-radius:4px;font-size:.78rem;
    }
    .code-block{padding:0;overflow:auto;background:#0d1117;}
    .code-header{
      display:flex;align-items:center;gap:.4rem;
      padding:.6rem 1rem;background:#161b22;border-bottom:1px solid var(--border);
    }
    .dot-r,.dot-y,.dot-g{width:10px;height:10px;border-radius:50%;}
    .dot-r{background:#ff5f56;} .dot-y{background:#ffbd2e;} .dot-g{background:#27c93f;}
    .code-filename{font-size:.75rem;color:#8b949e;margin-left:.3rem;}
    pre{
      margin:0;padding:1.2rem;font-size:.8rem;line-height:1.7;
      font-family:'Consolas','Fira Code',monospace;overflow-x:auto;color:#c9d1d9;
    }
    .kw{color:#ff7b72;}   /* keyword / key */
    .fn{color:#d2a8ff;}   /* function name */
    .st{color:#a5d6ff;}   /* string */
    .nm{color:#f0883e;}   /* number */
    .cm{color:#8b949e;}   /* comment */
    .c {color:#79c0ff;}   /* decorator / annotation */
    .hl-green{color:var(--green);font-weight:600;}
    .hl-blue{color:var(--accent);font-weight:600;}
    .hl-orange{color:var(--orange);font-weight:600;}
    .hl-red{color:#ef4444;font-weight:600;}

    @media(max-width:700px){
      .code-pane.active{grid-template-columns:1fr;}
      .code-desc{border-right:none;border-bottom:1px solid var(--border);}
    }
  </style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="nav-logo">📦 물류창고 자동화 시스템</div>
  <a href="/login" class="nav-login">로그인 →</a>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-badge">🚀 Logistics Automation v2.0</div>
  <h1>스마트 물류창고<br>관리 시스템</h1>
  <p>실시간 재고 추적, 주문 관리, 입출고 자동화까지.<br>물류창고 운영의 모든 것을 하나의 대시보드에서.</p>
  <div class="hero-btns">
    <a href="/login" class="btn-primary">시스템 시작하기</a>
    <a href="#features" class="btn-ghost">기능 살펴보기</a>
  </div>
</section>

<!-- STATS BAR -->
<div class="stats-bar">
  <div class="stat-item"><div class="val">실시간</div><div class="lbl">재고 현황 갱신</div></div>
  <div class="stat-item"><div class="val">A·B·C</div><div class="lbl">구역별 재고 관리</div></div>
  <div class="stat-item"><div class="val">5초</div><div class="lbl">자동 데이터 동기화</div></div>
  <div class="stat-item"><div class="val">2가지</div><div class="lbl">권한 역할 관리</div></div>
</div>

<!-- FEATURES -->
<div class="section" id="features">
  <div class="section-label">Core Features</div>
  <h2>주요 기능</h2>
  <p class="sub">물류창고 운영에 필요한 기능을 모두 제공합니다.</p>
  <div class="features">
    <div class="feat-card">
      <div class="feat-icon">📊</div>
      <h3>실시간 대시보드</h3>
      <p>전체 재고 현황, 주문 통계, 처리 명령 수를 한눈에 파악할 수 있는 통합 대시보드.</p>
      <span class="feat-tag tag-blue">실시간 갱신</span>
    </div>
    <div class="feat-card">
      <div class="feat-icon">📋</div>
      <h3>재고 현황 관리</h3>
      <p>바코드 기반 재고 조회, 수량 증감 제어, 품목 삭제까지 직관적인 인터페이스로 관리.</p>
      <span class="feat-tag tag-green">바코드 지원</span>
    </div>
    <div class="feat-card">
      <div class="feat-icon">📥</div>
      <h3>신규 입고 등록</h3>
      <p>바코드, 상품명, 수량, 보관 구역을 입력해 즉시 재고에 반영. 창고 구역 자동 배정.</p>
      <span class="feat-tag tag-orange">즉시 반영</span>
    </div>
    <div class="feat-card">
      <div class="feat-icon">📦</div>
      <h3>주문 관리</h3>
      <p>출고·발주 주문 등록부터 대기 → 처리 → 완료까지 상태 흐름을 한 화면에서 관리.</p>
      <span class="feat-tag tag-blue">상태 추적</span>
    </div>
    <div class="feat-card">
      <div class="feat-icon">🗺️</div>
      <h3>창고 구역 시각화</h3>
      <p>A·B·C 구역별 재고 현황을 시각적으로 확인. 구역 내 품목 목록 및 재고량 표시.</p>
      <span class="feat-tag tag-green">구역별 현황</span>
    </div>
    <div class="feat-card">
      <div class="feat-icon">👤</div>
      <h3>계정 및 권한 관리</h3>
      <p>Admin과 Operator 역할 구분. 계정 추가·삭제·비밀번호 변경을 관리자가 직접 제어.</p>
      <span class="feat-tag tag-purple">역할 기반</span>
    </div>
  </div>
</div>

<!-- FLOW -->
<div style="max-width:1100px;margin:0 auto;padding:0 2rem 5rem;">
  <div class="flow-wrap">
    <div class="section-label">System Flow</div>
    <h2 style="font-size:1.4rem;font-weight:800;">처리 흐름</h2>
    <div class="flow">
      <div class="flow-step">
        <div class="step-icon">📥</div>
        <div class="step-name">입고 등록</div>
        <div class="step-sub">바코드 스캔</div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-step">
        <div class="step-icon">🗄️</div>
        <div class="step-name">재고 반영</div>
        <div class="step-sub">data.json 저장</div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-step">
        <div class="step-icon">📦</div>
        <div class="step-name">주문 생성</div>
        <div class="step-sub">출고·발주</div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-step">
        <div class="step-icon">⚙️</div>
        <div class="step-name">상태 처리</div>
        <div class="step-sub">대기→완료</div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-step">
        <div class="step-icon">📊</div>
        <div class="step-name">대시보드</div>
        <div class="step-sub">실시간 확인</div>
      </div>
    </div>
  </div>
</div>

<!-- CODE SECTION -->
<div style="max-width:1100px;margin:0 auto;padding:0 2rem 5rem;">
  <div class="section-label">Code Walkthrough</div>
  <h2 style="font-size:2rem;font-weight:800;margin-bottom:.6rem;">코드로 보는 시스템</h2>
  <p style="color:var(--muted);margin-bottom:2rem;font-size:1rem;">핵심 로직을 코드와 함께 살펴보세요.</p>

  <!-- 탭 -->
  <div style="display:flex;gap:.5rem;margin-bottom:0;flex-wrap:wrap;">
    <button class="code-tab active" onclick="switchTab('api')">📡 API 엔드포인트</button>
    <button class="code-tab" onclick="switchTab('ipc')">🔗 파일 기반 IPC</button>
    <button class="code-tab" onclick="switchTab('data')">🗄️ 데이터 구조</button>
    <button class="code-tab" onclick="switchTab('order')">📦 주문 처리</button>
  </div>

  <!-- 코드 패널 -->
  <div class="code-panel">

    <!-- API -->
    <div class="code-pane active" id="pane-api">
      <div class="code-desc">
        <h3>재고 API 엔드포인트</h3>
        <p>Flask로 구현된 RESTful API입니다. <code>/api/inventory</code>는 재고 데이터를 반환하고, <code>/api/update</code>는 수량 변경 및 신규 입고 명령을 처리합니다. 모든 엔드포인트는 세션 기반 로그인 인증이 필요합니다.</p>
        <ul>
          <li><span class="hl-green">GET</span> <code>/api/inventory</code> — data.json 전체 반환</li>
          <li><span class="hl-blue">POST</span> <code>/api/update</code> — 수량 변경 / 신규 입고</li>
          <li><span class="hl-red">DELETE</span> <code>/api/inventory/&lt;barcode&gt;</code> — 품목 삭제</li>
        </ul>
      </div>
      <div class="code-block">
        <div class="code-header"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><span class="code-filename">LogisticsWeb.py</span></div>
        <pre><span class="c">@app.route('/api/update', methods=['POST'])</span>
<span class="c">@login_required</span>
<span class="kw">def</span> <span class="fn">update_inventory</span>():
    data = request.get_json()
    cmd_type = data.get(<span class="st">'type'</span>)

    <span class="cm"># commands.txt 에 명령 기록 (C++ 백엔드 연동)</span>
    <span class="kw">with</span> open(CMD_PATH, <span class="st">'a'</span>) <span class="kw">as</span> f:
        <span class="kw">if</span> cmd_type == <span class="st">'QTY'</span>:
            f.write(<span class="st">f"QTY,{data['barcode']},{data['change']}\n"</span>)
        <span class="kw">elif</span> cmd_type == <span class="st">'NEW'</span>:
            f.write(<span class="st">f"NEW,{data['barcode']},{data['name']},"</span>
                    <span class="st">f"{data['qty']},{data['zone']},"</span>
                    <span class="st">f"{data['sec']},{data['shelf']}\n"</span>)

    <span class="cm"># data.json 에 즉시 반영</span>
    inventory = load_data()
    <span class="kw">if</span> cmd_type == <span class="st">'QTY'</span>:
        bc = data.get(<span class="st">'barcode'</span>)
        inventory[bc][<span class="st">'quantity'</span>] = max(<span class="nm">0</span>,
            inventory[bc][<span class="st">'quantity'</span>] + int(data[<span class="st">'change'</span>]))
    <span class="kw">elif</span> cmd_type == <span class="st">'NEW'</span>:
        inventory[data[<span class="st">'barcode'</span>]] = {
            <span class="st">'name'</span>: data[<span class="st">'name'</span>],
            <span class="st">'quantity'</span>: int(data[<span class="st">'qty'</span>]),
            <span class="st">'location'</span>: <span class="st">f"{data['zone']}-{data['sec']}-{data['shelf']}"</span>
        }
    save_data(inventory)
    <span class="kw">return</span> jsonify({<span class="st">'status'</span>: <span class="st">'success'</span>})</pre>
      </div>
    </div>

    <!-- IPC -->
    <div class="code-pane" id="pane-ipc">
      <div class="code-desc">
        <h3>파일 기반 IPC (프로세스 간 통신)</h3>
        <p>Python Flask 서버와 C++ 백엔드는 파일을 통해 통신합니다. Flask가 <code>commands.txt</code>에 명령을 append하면, C++ 백엔드가 이를 읽어 처리하고 <code>data.json</code>을 갱신합니다.</p>
        <ul>
          <li><code>commands.txt</code> — Flask → C++ 방향 명령 전달</li>
          <li><code>data.json</code> — C++ → Flask 방향 재고 데이터 공유</li>
        </ul>
      </div>
      <div class="code-block">
        <div class="code-header"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><span class="code-filename">commands.txt  (명령 프로토콜)</span></div>
        <pre><span class="cm"># 수량 변경: QTY,&lt;바코드&gt;,&lt;증감량&gt;</span>
<span class="st">QTY,A100,10</span>       <span class="cm"># A100 바코드 재고 10개 증가</span>
<span class="st">QTY,B200,-5</span>       <span class="cm"># B200 바코드 재고 5개 감소</span>

<span class="cm"># 신규 입고: NEW,&lt;바코드&gt;,&lt;상품명&gt;,&lt;수량&gt;,&lt;구역&gt;,&lt;섹션&gt;,&lt;선반&gt;</span>
<span class="st">NEW,C300,노트북,50,A,1,1</span>
<span class="st">NEW,D400,마우스,200,B,2,3</span></pre>
        <div class="code-header" style="margin-top:1rem;border-top:1px solid var(--border);"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><span class="code-filename">data.json  (공유 재고 데이터)</span></div>
        <pre>{
  <span class="kw">"A100"</span>: {
    <span class="kw">"name"</span>:     <span class="st">"노트북"</span>,
    <span class="kw">"quantity"</span>: <span class="nm">50</span>,
    <span class="kw">"location"</span>: <span class="st">"A-1-1"</span>
  },
  <span class="kw">"B200"</span>: {
    <span class="kw">"name"</span>:     <span class="st">"마우스"</span>,
    <span class="kw">"quantity"</span>: <span class="nm">200</span>,
    <span class="kw">"location"</span>: <span class="st">"B-2-3"</span>
  }
}</pre>
      </div>
    </div>

    <!-- DATA -->
    <div class="code-pane" id="pane-data">
      <div class="code-desc">
        <h3>핵심 데이터 구조</h3>
        <p>C++ 백엔드의 <code>Common.h</code>에 정의된 데이터 모델과 Python의 JSON 구조가 대응됩니다. 사용자 인증은 SHA-256 해시로 비밀번호를 저장하며, 주문은 상태 흐름을 포함한 구조로 관리됩니다.</p>
        <ul>
          <li><code>users.json</code> — 계정·역할·해시 비밀번호</li>
          <li><code>orders.json</code> — 주문 목록 및 상태</li>
        </ul>
      </div>
      <div class="code-block">
        <div class="code-header"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><span class="code-filename">users.json</span></div>
        <pre>[
  {
    <span class="kw">"username"</span>: <span class="st">"admin"</span>,
    <span class="kw">"password"</span>: <span class="st">"03ac674216f3e15c..."</span>,  <span class="cm">// SHA-256</span>
    <span class="kw">"role"</span>:     <span class="st">"Admin"</span>               <span class="cm">// Admin | Operator</span>
  }
]</pre>
        <div class="code-header" style="margin-top:1rem;border-top:1px solid var(--border);"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><span class="code-filename">orders.json</span></div>
        <pre>[
  {
    <span class="kw">"id"</span>:         <span class="st">"ORD0001"</span>,
    <span class="kw">"barcode"</span>:    <span class="st">"A100"</span>,
    <span class="kw">"name"</span>:       <span class="st">"노트북"</span>,
    <span class="kw">"qty"</span>:        <span class="nm">10</span>,
    <span class="kw">"type"</span>:       <span class="st">"출고"</span>,       <span class="cm">// 출고 | 발주(재입고)</span>
    <span class="kw">"status"</span>:     <span class="st">"대기중"</span>,    <span class="cm">// 대기중→처리중→완료|취소</span>
    <span class="kw">"note"</span>:       <span class="st">""</span>,
    <span class="kw">"created_at"</span>: <span class="st">"2026-06-02 14:30"</span>
  }
]</pre>
      </div>
    </div>

    <!-- ORDER -->
    <div class="code-pane" id="pane-order">
      <div class="code-desc">
        <h3>주문 생성 및 재고 자동 반영</h3>
        <p>주문 등록 시 유형에 따라 재고가 즉시 변경됩니다. <span class="hl-orange">출고</span> 주문은 재고를 차감하고, <span class="hl-blue">발주</span> 주문은 재고를 증가시킵니다. 주문 상태는 대기중 → 처리중 → 완료 흐름으로 관리됩니다.</p>
        <ul>
          <li>출고 주문 → 재고 <span class="hl-red">차감</span> (0 이하 불가)</li>
          <li>발주 주문 → 재고 <span class="hl-green">증가</span></li>
        </ul>
      </div>
      <div class="code-block">
        <div class="code-header"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span><span class="code-filename">LogisticsWeb.py — create_order()</span></div>
        <pre><span class="c">@app.route('/api/orders', methods=['POST'])</span>
<span class="c">@login_required</span>
<span class="kw">def</span> <span class="fn">create_order</span>():
    data       = request.get_json()
    barcode    = data.get(<span class="st">'barcode'</span>)
    qty        = int(data.get(<span class="st">'qty'</span>, <span class="nm">1</span>))
    order_type = data.get(<span class="st">'type'</span>, <span class="st">'출고'</span>)

    inventory = load_data()
    <span class="kw">if</span> barcode <span class="kw">in</span> inventory:
        <span class="kw">if</span> order_type == <span class="st">'출고'</span>:
            <span class="cm"># 재고 차감 (0 미만 방지)</span>
            inventory[barcode][<span class="st">'quantity'</span>] = max(
                <span class="nm">0</span>, inventory[barcode][<span class="st">'quantity'</span>] - qty)
        <span class="kw">elif</span> order_type == <span class="st">'발주(재입고)'</span>:
            <span class="cm"># 재고 증가</span>
            inventory[barcode][<span class="st">'quantity'</span>] += qty
        save_data(inventory)

    <span class="cm"># 주문 저장</span>
    orders = load_orders()
    orders.append({
        <span class="st">'id'</span>:     <span class="st">f"ORD{len(orders)+1:04d}"</span>,
        <span class="st">'status'</span>: <span class="st">'대기중'</span>,
        <span class="cm">...  # barcode, name, qty, type, note, created_at</span>
    })
    save_orders(orders)
    <span class="kw">return</span> jsonify({<span class="st">'status'</span>: <span class="st">'success'</span>})</pre>
      </div>
    </div>

  </div><!-- /code-panel -->
</div>

<!-- CTA -->
<div class="cta">
  <h2>지금 바로 시작하세요</h2>
  <p>로그인 후 물류창고 관리 시스템을 이용할 수 있습니다.</p>
  <a href="/login" class="btn-primary">로그인하기 →</a>
</div>

<footer>© 2026 물류창고 자동화 시스템 · Logistics Automation v2.0</footer>

<script>
function switchTab(name) {
  document.querySelectorAll('.code-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.code-pane').forEach(p => p.classList.remove('active'));
  event.currentTarget.classList.add('active');
  document.getElementById('pane-' + name).classList.add('active');
}
</script>
</body>
</html>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>물류창고 관리 — 로그인</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;}
    body{
      background:#0f172a;color:#e2e8f0;font-family:'Segoe UI',sans-serif;
      display:flex;align-items:center;justify-content:center;min-height:100vh;
    }
    .login-wrap{
      background:#162032;border:1px solid rgba(255,255,255,.07);
      border-radius:16px;padding:2.5rem 2rem;width:100%;max-width:380px;
    }
    .logo{text-align:center;margin-bottom:2rem;}
    .logo h1{font-size:1.4rem;font-weight:800;color:#38bdf8;}
    .logo p{font-size:.8rem;color:#64748b;margin-top:.3rem;}
    label{display:block;font-size:.78rem;color:#64748b;margin-bottom:.3rem;}
    input{
      width:100%;padding:.65rem .9rem;border-radius:8px;font-size:.9rem;
      background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
      color:#e2e8f0;outline:none;margin-bottom:1rem;
    }
    input:focus{border-color:#38bdf8;}
    .btn-login{
      width:100%;padding:.75rem;border-radius:8px;border:none;cursor:pointer;
      background:#2563eb;color:#fff;font-size:.95rem;font-weight:700;
      transition:background .15s;margin-top:.3rem;
    }
    .btn-login:hover{background:#1d4ed8;}
    .error{
      background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.3);
      color:#ef4444;border-radius:8px;padding:.6rem .9rem;font-size:.82rem;
      margin-bottom:1rem;text-align:center;
    }
    .role-info{
      margin-top:1.5rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.07);
      font-size:.75rem;color:#475569;text-align:center;line-height:1.7;
    }
    .badge{
      display:inline-block;padding:.1rem .5rem;border-radius:999px;font-size:.7rem;font-weight:600;
    }
    .badge-admin{background:rgba(249,115,22,.15);color:#f97316;}
    .badge-op{background:rgba(56,189,248,.15);color:#38bdf8;}
  </style>
</head>
<body>
  <div class="login-wrap">
    <div class="logo">
      <h1>📦 물류창고 관리</h1>
      <p>Logistics Automation v2.0</p>
    </div>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <form method="POST" action="/login">
      <label>아이디</label>
      <input type="text" name="username" placeholder="아이디를 입력하세요" autofocus required/>
      <label>비밀번호</label>
      <input type="password" name="password" placeholder="비밀번호를 입력하세요" required/>
      <button type="submit" class="btn-login">로그인</button>
    </form>
    <div class="role-info">
      <span class="badge badge-admin">Admin</span> 모든 기능 사용 가능 &nbsp;|&nbsp;
      <span class="badge badge-op">Operator</span> 재고 조회·수량 변경
    </div>
  </div>
</body>
</html>
"""

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>물류창고 자동화 대시보드</title>
  <style>
    :root {
      --bg:      #0f172a;
      --side:    #0d1b2e;
      --card:    #162032;
      --border:  rgba(255,255,255,.07);
      --text:    #e2e8f0;
      --muted:   #64748b;
      --accent:  #38bdf8;
      --blue:    #2563eb;
      --green:   #22c55e;
      --red:     #ef4444;
      --orange:  #f97316;
      --yellow:  #eab308;
      --purple:  #a78bfa;
    }
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:'Segoe UI','Malgun Gothic',sans-serif;background:var(--bg);color:var(--text);display:flex;min-height:100vh;}

    /* ─── SIDEBAR ─── */
    .sidebar{
      width:240px;min-width:240px;background:var(--side);
      border-right:1px solid var(--border);
      display:flex;flex-direction:column;padding:1.5rem 0;
      position:fixed;top:0;left:0;bottom:0;z-index:50;
    }
    .logo{padding:0 1.4rem 1.6rem;border-bottom:1px solid var(--border);}
    .logo h1{font-size:1rem;font-weight:700;color:var(--accent);}
    .logo p{font-size:.72rem;color:var(--muted);margin-top:.2rem;}
    .nav{padding:1rem 0;flex:1;}
    .nav-item{
      display:flex;align-items:center;gap:.7rem;padding:.65rem 1.4rem;
      color:var(--muted);font-size:.875rem;cursor:pointer;
      border-left:3px solid transparent;transition:all .15s;
    }
    .nav-item:hover{color:var(--text);background:rgba(255,255,255,.04);}
    .nav-item.active{color:var(--accent);background:rgba(56,189,248,.08);border-left-color:var(--accent);}
    .nav-item .icon{font-size:1rem;width:20px;text-align:center;}
    .sidebar-footer{padding:1rem 1.4rem;border-top:1px solid var(--border);}
    .status-dot{
      display:flex;align-items:center;gap:.5rem;font-size:.75rem;color:var(--muted);
    }
    .dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s infinite;}
    @keyframes pulse{0%,100%{opacity:1;}50%{opacity:.4;}}

    /* ─── MAIN ─── */
    .main{margin-left:240px;flex:1;display:flex;flex-direction:column;min-height:100vh;}

    /* ─── TOPBAR ─── */
    .topbar{
      height:56px;background:rgba(15,23,42,.8);backdrop-filter:blur(10px);
      border-bottom:1px solid var(--border);
      display:flex;align-items:center;justify-content:space-between;
      padding:0 2rem;position:sticky;top:0;z-index:40;
    }
    .topbar-left{font-size:.95rem;font-weight:600;}
    .topbar-right{display:flex;align-items:center;gap:1rem;}
    .auto-badge{
      font-size:.72rem;padding:.25rem .7rem;border-radius:999px;
      background:rgba(34,197,94,.15);color:var(--green);border:1px solid rgba(34,197,94,.25);
    }
    .refresh-btn{
      padding:.4rem .9rem;border-radius:6px;border:1px solid var(--border);
      background:transparent;color:var(--text);font-size:.8rem;cursor:pointer;transition:all .15s;
    }
    .refresh-btn:hover{background:rgba(255,255,255,.06);}

    /* ─── CONTENT ─── */
    .content{padding:2rem;flex:1;}

    /* ─── STAT CARDS ─── */
    .stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-bottom:2rem;}
    .stat-card{
      background:var(--card);border:1px solid var(--border);
      border-radius:12px;padding:1.2rem 1.4rem;
    }
    .stat-card .label{font-size:.75rem;color:var(--muted);margin-bottom:.4rem;}
    .stat-card .value{font-size:1.8rem;font-weight:800;}
    .stat-card .sub{font-size:.72rem;color:var(--muted);margin-top:.3rem;}
    .c-blue{color:var(--accent);}
    .c-green{color:var(--green);}
    .c-orange{color:var(--orange);}
    .c-purple{color:var(--purple);}
    .c-yellow{color:var(--yellow);}

    /* ─── SECTION ─── */
    .section{display:none;}
    .section.active{display:block;}
    .section-header{
      display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem;
    }
    .section-title{font-size:1.05rem;font-weight:700;}
    .btn{
      padding:.5rem 1.1rem;border-radius:7px;font-size:.82rem;font-weight:600;
      cursor:pointer;border:none;transition:all .15s;
    }
    .btn-primary{background:var(--blue);color:#fff;}
    .btn-primary:hover{background:#1d4ed8;}
    .btn-danger{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.2);}
    .btn-danger:hover{background:rgba(239,68,68,.25);}

    /* ─── TABLE ─── */
    .table-wrap{
      background:var(--card);border:1px solid var(--border);
      border-radius:12px;overflow:hidden;
    }
    table{width:100%;border-collapse:collapse;}
    thead th{
      background:rgba(255,255,255,.04);padding:.85rem 1.1rem;
      font-size:.78rem;color:var(--muted);font-weight:600;text-align:left;
      border-bottom:1px solid var(--border);
    }
    tbody tr{border-bottom:1px solid var(--border);transition:background .1s;}
    tbody tr:last-child{border-bottom:none;}
    tbody tr:hover{background:rgba(255,255,255,.025);}
    tbody td{padding:.8rem 1.1rem;font-size:.875rem;}
    .badge{
      display:inline-flex;align-items:center;gap:.3rem;
      padding:.2rem .65rem;border-radius:999px;font-size:.72rem;font-weight:600;
    }
    .badge-green{background:rgba(34,197,94,.15);color:var(--green);}
    .badge-yellow{background:rgba(234,179,8,.15);color:var(--yellow);}
    .badge-blue{background:rgba(56,189,248,.15);color:var(--accent);}
    .badge-orange{background:rgba(249,115,22,.15);color:var(--orange);}
    .badge-red{background:rgba(239,68,68,.15);color:var(--red);}

    .qty-ctrl{display:flex;align-items:center;gap:.6rem;}
    .qty-btn{
      width:28px;height:28px;border-radius:6px;border:none;cursor:pointer;
      font-size:1rem;font-weight:700;display:flex;align-items:center;justify-content:center;
      transition:all .15s;
    }
    .qty-minus{background:rgba(239,68,68,.15);color:var(--red);}
    .qty-minus:hover{background:rgba(239,68,68,.3);}
    .qty-plus{background:rgba(34,197,94,.15);color:var(--green);}
    .qty-plus:hover{background:rgba(34,197,94,.3);}
    .qty-val{min-width:50px;text-align:center;font-weight:600;font-size:.9rem;}
    .qty-step{
      width:48px;height:28px;border-radius:6px;text-align:center;font-size:.82rem;font-weight:600;
      background:rgba(255,255,255,.06);border:1px solid var(--border);color:var(--text);
    }
    .qty-step:focus{outline:none;border-color:var(--accent);}

    .zone-tag{
      display:inline-block;padding:.15rem .55rem;border-radius:5px;font-size:.75rem;font-weight:700;
    }
    .zone-A{background:rgba(56,189,248,.15);color:var(--accent);}
    .zone-B{background:rgba(167,139,250,.15);color:var(--purple);}
    .zone-C{background:rgba(249,115,22,.15);color:var(--orange);}
    .zone-D{background:rgba(34,197,94,.15);color:var(--green);}

    /* ─── MODAL ─── */
    .modal-backdrop{
      position:fixed;inset:0;background:rgba(0,0,0,.65);
      display:none;align-items:center;justify-content:center;z-index:200;
    }
    .modal-backdrop.open{display:flex;}
    .modal{
      background:#162032;border:1px solid var(--border);
      border-radius:16px;padding:2rem;width:480px;max-width:95vw;
    }
    .modal h2{font-size:1.05rem;font-weight:700;margin-bottom:1.4rem;color:var(--accent);}
    .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;}
    .form-grid.full{grid-template-columns:1fr;}
    .field{display:flex;flex-direction:column;gap:.4rem;}
    .field label{font-size:.75rem;color:var(--muted);font-weight:600;}
    .field input,.field select{
      background:var(--bg);border:1px solid var(--border);
      border-radius:7px;padding:.6rem .8rem;color:var(--text);font-size:.875rem;
      outline:none;transition:border-color .15s;
    }
    .field input:focus,.field select:focus{border-color:var(--accent);}
    .modal-actions{display:flex;gap:.8rem;justify-content:flex-end;margin-top:1.5rem;}

    /* ─── EMPTY STATE ─── */
    .empty{
      padding:4rem;text-align:center;color:var(--muted);
    }
    .empty .icon{font-size:3rem;margin-bottom:1rem;}
    .empty p{font-size:.9rem;}

    /* ─── TOAST ─── */
    #toast-container{
      position:fixed;bottom:2rem;right:2rem;z-index:999;
      display:flex;flex-direction:column;gap:.6rem;
    }
    .toast{
      padding:.8rem 1.2rem;border-radius:8px;font-size:.85rem;
      backdrop-filter:blur(10px);border:1px solid;
      animation:slide-in .25s ease;min-width:220px;
    }
    .toast.success{background:rgba(34,197,94,.15);border-color:rgba(34,197,94,.3);color:var(--green);}
    .toast.error{background:rgba(239,68,68,.15);border-color:rgba(239,68,68,.3);color:var(--red);}
    .toast.info{background:rgba(56,189,248,.12);border-color:rgba(56,189,248,.25);color:var(--accent);}
    @keyframes slide-in{from{transform:translateX(60px);opacity:0;}to{transform:none;opacity:1;}}

    /* ─── ZONE MAP ─── */
    .zone-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-top:1rem;}
    .zone-card{
      background:var(--card);border:1px solid var(--border);
      border-radius:12px;padding:1.2rem;
    }
    .zone-card h3{font-size:.9rem;font-weight:700;margin-bottom:.8rem;}
    .zone-stat{display:flex;justify-content:space-between;font-size:.82rem;color:var(--muted);margin-top:.4rem;}
    .zone-bar{height:4px;background:rgba(255,255,255,.07);border-radius:2px;margin-top:.6rem;}
    .zone-fill{height:100%;border-radius:2px;transition:width .4s;}

    /* ─── LOG ─── */
    .log-list{
      background:var(--card);border:1px solid var(--border);
      border-radius:12px;padding:.5rem 0;max-height:360px;overflow-y:auto;
    }
    .log-item{
      padding:.6rem 1.2rem;font-size:.8rem;border-bottom:1px solid var(--border);
      display:flex;align-items:center;gap:.8rem;
    }
    .log-item:last-child{border-bottom:none;}
    .log-time{color:var(--muted);font-family:monospace;min-width:85px;}
    .log-msg{flex:1;}
    .log-tag{font-size:.7rem;padding:.1rem .5rem;border-radius:4px;}

    /* ─── SCROLLBAR ─── */
    ::-webkit-scrollbar{width:5px;height:5px;}
    ::-webkit-scrollbar-track{background:transparent;}
    ::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:3px;}
  </style>
</head>
<body>

<!-- ───────── SIDEBAR ───────── -->
<aside class="sidebar">
  <div class="logo">
    <h1>📦 물류창고 관리</h1>
    <p>Logistics Automation v2.0</p>
  </div>
  <nav class="nav">
    <div class="nav-item active" onclick="showSection('dashboard')">
      <span class="icon">📊</span> 대시보드
    </div>
    <div class="nav-item" onclick="showSection('inventory')">
      <span class="icon">📋</span> 재고 현황
    </div>
    <div class="nav-item" onclick="showSection('inbound')">
      <span class="icon">📥</span> 입고 등록
    </div>
    <div class="nav-item" onclick="showSection('orders')">
      <span class="icon">📦</span> 주문 관리
    </div>
    <div class="nav-item" onclick="showSection('zones')">
      <span class="icon">🗺️</span> 창고 구역
    </div>
    <div class="nav-item" onclick="showSection('log')">
      <span class="icon">📝</span> 명령 로그
    </div>
    {% if session.role == 'Admin' %}
    <div class="nav-item" onclick="showSection('accounts')">
      <span class="icon">👤</span> 계정 관리
    </div>
    {% endif %}
  </nav>
  <div class="sidebar-footer">
    <div style="margin-bottom:.8rem;">
      <div style="font-size:.78rem;color:var(--text);font-weight:600;">{{ session.username }}</div>
      <div style="font-size:.7rem;color:var(--muted);margin-top:.15rem;">
        {% if session.role == 'Admin' %}
        <span style="color:#f97316;">● Admin</span>
        {% else %}
        <span style="color:#38bdf8;">● Operator</span>
        {% endif %}
      </div>
    </div>
    <div class="status-dot">
      <div class="dot"></div>
      <span>서버 연결됨</span>
    </div>
    <div style="font-size:.7rem;color:var(--muted);margin-top:.5rem;">5초마다 자동 갱신</div>
    <a href="/logout" style="display:block;margin-top:.8rem;font-size:.75rem;color:var(--muted);text-decoration:none;padding:.3rem 0;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#64748b'">⎋ 로그아웃</a>
  </div>
</aside>

<!-- ───────── MAIN ───────── -->
<main class="main">
  <div class="topbar">
    <div class="topbar-left" id="topbar-title">대시보드</div>
    <div class="topbar-right">
      <span class="auto-badge" id="auto-status">● 자동 갱신</span>
      <button class="refresh-btn" onclick="loadInventory()">🔄 새로고침</button>
      <button class="btn btn-primary" onclick="openModal()">+ 신규 입고</button>
    </div>
  </div>

  <div class="content">

    <!-- ── 대시보드 ── -->
    <div id="sec-dashboard" class="section active">
      <div class="stats" id="stat-cards">
        <div class="stat-card"><div class="label">전체 품목 수</div><div class="value c-blue" id="st-total">—</div><div class="sub">등록된 바코드</div></div>
        <div class="stat-card"><div class="label">총 재고 수량</div><div class="value c-green" id="st-qty">—</div><div class="sub">개</div></div>
        <div class="stat-card"><div class="label">구역 수</div><div class="value c-orange" id="st-zones">—</div><div class="sub">활성 Zone</div></div>
        <div class="stat-card"><div class="label">부족 재고</div><div class="value c-red" id="st-low" style="color:var(--red)">—</div><div class="sub">10개 미만</div></div>
        <div class="stat-card"><div class="label">오늘 처리 명령</div><div class="value c-purple" id="st-cmd">—</div><div class="sub">건</div></div>
        <div class="stat-card"><div class="label">대기중 주문</div><div class="value" id="st-ord-wait" style="color:var(--yellow)">—</div><div class="sub">처리 대기</div></div>
        <div class="stat-card"><div class="label">처리중 주문</div><div class="value" id="st-ord-proc" style="color:var(--accent)">—</div><div class="sub">진행 중</div></div>
        <div class="stat-card"><div class="label">완료 주문</div><div class="value c-green" id="st-ord-done">—</div><div class="sub">처리 완료</div></div>
      </div>

      <div class="section-header">
        <div class="section-title">최근 재고 현황</div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>바코드</th><th>상품명</th><th>재고 수량</th><th>보관 위치</th><th>상태</th>
            </tr>
          </thead>
          <tbody id="dash-table"><tr><td colspan="5"><div class="empty"><div class="icon">⏳</div><p>데이터 로드 중...</p></div></td></tr></tbody>
        </table>
      </div>

      <div class="section-header" style="margin-top:1.5rem;">
        <div class="section-title">최근 주문 현황</div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>주문번호</th><th>품목명</th><th>수량</th><th>유형</th><th>상태</th><th>등록일시</th>
            </tr>
          </thead>
          <tbody id="dash-order-table"><tr><td colspan="6"><div class="empty"><div class="icon">📦</div><p>주문 내역이 없습니다.</p></div></td></tr></tbody>
        </table>
      </div>
    </div>

    <!-- ── 재고 현황 ── -->
    <div id="sec-inventory" class="section">
      <div class="section-header">
        <div class="section-title">전체 재고 목록</div>
        <div style="display:flex;gap:.6rem;align-items:center;">
          <input id="search-box" type="text" placeholder="바코드 / 상품명 검색..."
            style="background:var(--card);border:1px solid var(--border);border-radius:7px;padding:.45rem .8rem;color:var(--text);font-size:.82rem;outline:none;width:200px;"
            oninput="filterTable()"/>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>바코드</th><th>상품명</th><th>재고 제어</th><th>Zone</th><th>위치</th><th>상태</th><th>삭제</th>
            </tr>
          </thead>
          <tbody id="inv-table"><tr><td colspan="6"><div class="empty"><div class="icon">📭</div><p>재고 데이터가 없습니다. C++ 백엔드에서 데이터를 입력하거나 입고 등록을 사용하세요.</p></div></td></tr></tbody>
        </table>
      </div>
    </div>

    <!-- ── 입고 등록 ── -->
    <div id="sec-inbound" class="section">
      <div class="section-header">
        <div class="section-title">신규 입고 등록</div>
      </div>
      <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:2rem;max-width:560px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
          <div class="field" style="grid-column:1/-1;">
            <label>바코드 *</label>
            <input type="text" id="f-barcode" placeholder="예) B200"/>
          </div>
          <div class="field" style="grid-column:1/-1;">
            <label>상품명 *</label>
            <input type="text" id="f-name" placeholder="예) 사과"/>
          </div>
          <div class="field">
            <label>수량 *</label>
            <input type="number" id="f-qty" placeholder="0" min="1"/>
          </div>
          <div class="field">
            <label>구역 (Zone) *</label>
            <select id="f-zone">
              <option value="">선택</option>
              <option value="A">A구역</option>
              <option value="B">B구역</option>
              <option value="C">C구역</option>
              <option value="D">D구역</option>
            </select>
          </div>
          <div class="field">
            <label>섹션 (Section) *</label>
            <input type="number" id="f-sec" placeholder="1" min="1"/>
          </div>
          <div class="field">
            <label>선반 (Shelf) *</label>
            <input type="number" id="f-shelf" placeholder="1" min="1"/>
          </div>
        </div>
        <div style="display:flex;gap:.8rem;margin-top:1.5rem;">
          <button class="btn btn-primary" onclick="submitInbound()" style="flex:1;padding:.7rem;">📥 입고 등록</button>
          <button class="btn" onclick="clearInboundForm()"
            style="background:rgba(255,255,255,.06);color:var(--muted);border:1px solid var(--border);">초기화</button>
        </div>
        <p style="font-size:.75rem;color:var(--muted);margin-top:1rem;">
          * 입고 명령은 <code style="color:var(--accent)">commands.txt</code>에 기록되어 C++ 백엔드가 처리합니다.
        </p>
      </div>
    </div>

    <!-- ── 주문 관리 ── -->
    <div id="sec-orders" class="section">
      <div class="section-header">
        <div class="section-title">주문 관리</div>
        <button class="btn btn-primary" onclick="toggleOrderForm()">+ 새 주문</button>
      </div>

      <!-- 주문 생성 폼 -->
      <div id="order-form-wrap" style="display:none;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin-bottom:1.2rem;max-width:600px;">
        <div style="font-weight:600;margin-bottom:1rem;color:var(--accent);">신규 주문 등록</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;">
          <div class="field" style="grid-column:1/-1;">
            <label>품목 선택 *</label>
            <select id="o-barcode" style="width:100%;padding:.55rem .8rem;border-radius:7px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:var(--text);font-size:.875rem;">
              <option value="">-- 재고에서 선택 --</option>
            </select>
          </div>
          <div class="field">
            <label>주문 수량 *</label>
            <input type="number" id="o-qty" min="1" value="1" placeholder="수량"/>
          </div>
          <div class="field">
            <label>주문 유형</label>
            <select id="o-type" style="width:100%;padding:.55rem .8rem;border-radius:7px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:var(--text);font-size:.875rem;">
              <option value="출고">출고</option>
              <option value="발주">발주(재입고)</option>
            </select>
          </div>
          <div class="field" style="grid-column:1/-1;">
            <label>메모</label>
            <input type="text" id="o-note" placeholder="비고 사항 (선택)"/>
          </div>
        </div>
        <div style="display:flex;gap:.6rem;margin-top:1rem;">
          <button class="btn btn-primary" onclick="submitOrder()" style="flex:1;">주문 등록</button>
          <button class="btn" onclick="toggleOrderForm()" style="background:rgba(255,255,255,.06);color:var(--muted);border:1px solid var(--border);">취소</button>
        </div>
      </div>

      <!-- 주문 목록 -->
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>주문번호</th><th>품목명</th><th>바코드</th><th>수량</th><th>유형</th><th>상태</th><th>등록일시</th><th>메모</th><th>처리</th>
            </tr>
          </thead>
          <tbody id="order-table"><tr><td colspan="9"><div class="empty"><div class="icon">📦</div><p>주문 내역이 없습니다.</p></div></td></tr></tbody>
        </table>
      </div>
    </div>

    <!-- ── 창고 구역 ── -->
    <div id="sec-zones" class="section">
      <div class="section-header">
        <div class="section-title">창고 구역 현황</div>
      </div>
      <div class="zone-grid" id="zone-grid">
        <div class="empty"><p>재고 데이터 로드 중...</p></div>
      </div>
    </div>

    <!-- ── 명령 로그 ── -->
    <div id="sec-log" class="section">
      <div class="section-header">
        <div class="section-title">명령 로그</div>
        <button class="btn btn-danger" onclick="clearLog()">로그 초기화</button>
      </div>
      <div class="log-list" id="log-list">
        <div class="log-item"><span class="log-time">--:--:--</span><span class="log-msg" style="color:var(--muted);">명령 로그가 없습니다.</span></div>
      </div>
    </div>

    <!-- ── 계정 관리 ── -->
    <div id="sec-accounts" class="section">
      <div class="section-header">
        <div class="section-title">계정 관리</div>
        <button class="btn btn-primary" onclick="toggleAccForm()">+ 계정 추가</button>
      </div>

      <!-- 계정 추가 폼 -->
      <div id="acc-form-wrap" style="display:none;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin-bottom:1.2rem;max-width:480px;">
        <div style="font-weight:600;margin-bottom:1rem;color:var(--accent);">신규 계정 등록</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;">
          <div class="field">
            <label>아이디 *</label>
            <input type="text" id="acc-id" placeholder="아이디"/>
          </div>
          <div class="field">
            <label>역할</label>
            <select id="acc-role" style="width:100%;padding:.55rem .8rem;border-radius:7px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:var(--text);font-size:.875rem;">
              <option value="Operator">Operator</option>
              <option value="Admin">Admin</option>
            </select>
          </div>
          <div class="field">
            <label>비밀번호 *</label>
            <input type="password" id="acc-pw" placeholder="비밀번호"/>
          </div>
          <div class="field">
            <label>비밀번호 확인 *</label>
            <input type="password" id="acc-pw2" placeholder="비밀번호 확인"/>
          </div>
        </div>
        <div style="display:flex;gap:.6rem;margin-top:1rem;">
          <button class="btn btn-primary" onclick="submitAddAccount()" style="flex:1;">계정 추가</button>
          <button class="btn" onclick="toggleAccForm()" style="background:rgba(255,255,255,.06);color:var(--muted);border:1px solid var(--border);">취소</button>
        </div>
      </div>

      <!-- 계정 목록 -->
      <div class="table-wrap" style="margin-bottom:1.5rem;">
        <table>
          <thead><tr><th>아이디</th><th>역할</th><th>비밀번호 변경</th><th>삭제</th></tr></thead>
          <tbody id="acc-table"><tr><td colspan="4"><div class="empty"><div class="icon">👤</div><p>로딩 중...</p></div></td></tr></tbody>
        </table>
      </div>
    </div>

  </div><!-- /content -->
</main>

<!-- ───────── MODAL (빠른 입고) ───────── -->
<div class="modal-backdrop" id="modal">
  <div class="modal">
    <h2>📥 신규 입고 등록</h2>
    <div class="form-grid">
      <div class="field" style="grid-column:1/-1;">
        <label>바코드 *</label>
        <input type="text" id="m-barcode" placeholder="예) B200"/>
      </div>
      <div class="field" style="grid-column:1/-1;">
        <label>상품명 *</label>
        <input type="text" id="m-name" placeholder="예) 사과"/>
      </div>
      <div class="field">
        <label>수량 *</label>
        <input type="number" id="m-qty" placeholder="0" min="1"/>
      </div>
      <div class="field">
        <label>구역 (Zone) *</label>
        <select id="m-zone">
          <option value="">선택</option>
          <option value="A">A구역</option>
          <option value="B">B구역</option>
          <option value="C">C구역</option>
          <option value="D">D구역</option>
        </select>
      </div>
      <div class="field">
        <label>섹션 *</label>
        <input type="number" id="m-sec" placeholder="1" min="1"/>
      </div>
      <div class="field">
        <label>선반 *</label>
        <input type="number" id="m-shelf" placeholder="1" min="1"/>
      </div>
    </div>
    <div class="modal-actions">
      <button class="btn" onclick="closeModal()"
        style="background:rgba(255,255,255,.06);color:var(--muted);border:1px solid var(--border);">취소</button>
      <button class="btn btn-primary" onclick="submitModal()">등록</button>
    </div>
  </div>
</div>

<!-- ───────── TOAST ───────── -->
<div id="toast-container"></div>

<script>
// ── 전역 상태 ──────────────────────────────────
let inventory = {};
let cmdCount  = 0;
let logEntries = [];

// ── 섹션 전환 ─────────────────────────────────
const sectionTitles = {
  dashboard: '대시보드', inventory: '재고 현황',
  inbound:   '입고 등록', orders: '주문 관리', zones: '창고 구역', log: '명령 로그', accounts: '계정 관리'
};
function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  event.currentTarget.classList.add('active');
  document.getElementById('topbar-title').textContent = sectionTitles[name];
  if (name === 'accounts') loadAccounts();
}

// ── 재고 로드 ─────────────────────────────────
function loadInventory() {
  fetch('/api/inventory?t=' + Date.now())
    .then(r => r.json())
    .then(data => {
      inventory = data;
      renderDashTable();
      renderInvTable();
      renderZones();
      updateStats();
    })
    .catch(() => toast('서버 연결 실패', 'error'));
}

// ── 통계 카드 ─────────────────────────────────
function updateStats() {
  const items = Object.entries(inventory);
  const totalQty  = items.reduce((s,[,v]) => s + (v.quantity||0), 0);
  const zones     = new Set(items.map(([,v]) => (v.location||'').split('-')[0])).size;
  const lowStock  = items.filter(([,v]) => (v.quantity||0) < 10).length;
  document.getElementById('st-total').textContent = items.length;
  document.getElementById('st-qty').textContent   = totalQty.toLocaleString();
  document.getElementById('st-zones').textContent = zones;
  document.getElementById('st-low').textContent   = lowStock;
  document.getElementById('st-cmd').textContent   = cmdCount;
  document.getElementById('st-ord-wait').textContent = orders.filter(o => o.status === '대기중').length;
  document.getElementById('st-ord-proc').textContent = orders.filter(o => o.status === '처리중').length;
  document.getElementById('st-ord-done').textContent = orders.filter(o => o.status === '완료').length;
}

// ── 대시보드 테이블 ───────────────────────────
function renderDashTable() {
  const tbody = document.getElementById('dash-table');
  const items = Object.entries(inventory);
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty"><div class="icon">📭</div><p>C++ 백엔드가 data.json을 아직 작성하지 않았거나<br>입고 등록을 먼저 진행해주세요.</p></div></td></tr>`;
    return;
  }
  tbody.innerHTML = items.slice(0,10).map(([bc, item]) => {
    const qty = item.quantity ?? 0;
    const st  = qty <= 0 ? `<span class="badge badge-red">재고없음</span>`
               : qty < 10 ? `<span class="badge badge-yellow">부족</span>`
               : `<span class="badge badge-green">정상</span>`;
    const zoneKey = (item.location || '').split('-')[0] || '?';
    return `<tr>
      <td><code style="color:var(--accent);font-size:.82rem;">${bc}</code></td>
      <td>${item.name || '-'}</td>
      <td><strong>${qty.toLocaleString()}</strong> 개</td>
      <td>${locationBadge(item.location)}</td>
      <td>${st}</td>
    </tr>`;
  }).join('');
}

// ── 재고 현황 테이블 ──────────────────────────
function renderInvTable(filter = '') {
  const tbody = document.getElementById('inv-table');
  const items = Object.entries(inventory).filter(([bc, item]) =>
    !filter || bc.includes(filter) || (item.name||'').includes(filter)
  );
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty"><div class="icon">📭</div><p>표시할 재고가 없습니다.</p></div></td></tr>`;
    return;
  }
  tbody.innerHTML = items.map(([bc, item]) => {
    const qty = item.quantity ?? 0;
    const zoneKey = (item.location || '').split('-')[0] || '';
    const st = qty <= 0 ? `<span class="badge badge-red">재고없음</span>`
             : qty < 10 ? `<span class="badge badge-yellow">부족</span>`
             : `<span class="badge badge-green">정상</span>`;
    return `<tr>
      <td><code style="color:var(--accent);font-size:.82rem;">${bc}</code></td>
      <td>${item.name || '-'}</td>
      <td>
        <div class="qty-ctrl">
          <button class="qty-btn qty-minus" onclick="updateQtyStep('${bc}',-1)">−</button>
          <span class="qty-val">${qty.toLocaleString()}<small style="font-weight:400;font-size:.7rem;color:var(--muted);"> 개</small></span>
          <button class="qty-btn qty-plus"  onclick="updateQtyStep('${bc}', 1)">＋</button>
          <input type="number" class="qty-step" id="step-${bc}" value="1" min="1" title="변경 수량"/>
        </div>
      </td>
      <td>${zoneKey ? `<span class="zone-tag zone-${zoneKey}">${zoneKey}</span>` : '-'}</td>
      <td>${item.location || '-'}</td>
      <td>${st}</td>
      <td><button class="btn btn-danger" style="padding:.3rem .7rem;font-size:.78rem;" onclick="deleteItem('${bc}','${item.name||bc}')">삭제</button></td>
    </tr>`;
  }).join('');
}

function filterTable() {
  renderInvTable(document.getElementById('search-box').value.trim());
}

function deleteItem(barcode, name) {
  if (!confirm(`[${name}] 재고를 삭제할까요?`)) return;
  fetch(`/api/inventory/${barcode}`, { method: 'DELETE' })
    .then(r => r.json())
    .then(res => {
      if (res.status === 'success') {
        toast(`${name} 재고 삭제 완료`, 'success');
        loadInventory();
      } else {
        toast(res.message || '삭제 실패', 'error');
      }
    });
}

// ── 구역 시각화 ───────────────────────────────
function renderZones() {
  const zones = {};
  Object.entries(inventory).forEach(([bc, item]) => {
    const z = (item.location || '').split('-')[0] || '미분류';
    if (!zones[z]) zones[z] = { count:0, qty:0 };
    zones[z].count++;
    zones[z].qty += item.quantity || 0;
  });
  const maxQty = Math.max(...Object.values(zones).map(z=>z.qty), 1);
  const colors = { A:'#38bdf8', B:'#a78bfa', C:'#f97316', D:'#22c55e', '미분류':'#64748b' };
  const grid = document.getElementById('zone-grid');
  if (!Object.keys(zones).length) {
    grid.innerHTML = `<div class="empty"><div class="icon">🗺️</div><p>구역 데이터가 없습니다.</p></div>`;
    return;
  }
  grid.innerHTML = Object.entries(zones).map(([z, info]) => {
    const pct = Math.round((info.qty / maxQty) * 100);
    const color = colors[z] || '#64748b';
    return `<div class="zone-card">
      <h3><span class="zone-tag zone-${z}">${z}구역</span></h3>
      <div class="zone-stat"><span>품목 수</span><span style="color:var(--text)">${info.count}종</span></div>
      <div class="zone-stat"><span>총 재고</span><span style="color:var(--text)">${info.qty.toLocaleString()}개</span></div>
      <div class="zone-bar"><div class="zone-fill" style="width:${pct}%;background:${color}"></div></div>
    </div>`;
  }).join('');
}

// ── 수량 제어 ─────────────────────────────────
function updateQtyStep(barcode, dir) {
  const input = document.getElementById('step-' + barcode);
  const step = Math.max(1, parseInt(input ? input.value : 1) || 1);
  updateQty(barcode, dir * step);
}

function updateQty(barcode, change) {
  fetch('/api/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type:'QTY', barcode, change })
  })
  .then(r => r.json())
  .then(() => {
    cmdCount++;
    addLog(`수량 ${change > 0 ? '+' : ''}${change}`, barcode, 'QTY');
    toast(`${barcode} 수량 ${change > 0 ? '+' : ''}${change} 완료`, 'success');
    loadInventory();
  })
  .catch(() => toast('명령 전송 실패', 'error'));
}

// ── 입고 제출 (사이드바 폼) ───────────────────
function submitInbound() {
  const data = {
    type: 'NEW',
    barcode: document.getElementById('f-barcode').value.trim(),
    name:    document.getElementById('f-name').value.trim(),
    qty:     document.getElementById('f-qty').value,
    zone:    document.getElementById('f-zone').value,
    sec:     document.getElementById('f-sec').value,
    shelf:   document.getElementById('f-shelf').value,
  };
  if (!data.barcode||!data.name||!data.qty||!data.zone||!data.sec||!data.shelf) {
    toast('모든 항목을 입력해주세요.', 'error'); return;
  }
  sendNew(data, clearInboundForm);
}
function clearInboundForm() {
  ['f-barcode','f-name','f-qty','f-sec','f-shelf'].forEach(id => document.getElementById(id).value='');
  document.getElementById('f-zone').value='';
}

// ── 입고 제출 (모달) ─────────────────────────
function submitModal() {
  const data = {
    type: 'NEW',
    barcode: document.getElementById('m-barcode').value.trim(),
    name:    document.getElementById('m-name').value.trim(),
    qty:     document.getElementById('m-qty').value,
    zone:    document.getElementById('m-zone').value,
    sec:     document.getElementById('m-sec').value,
    shelf:   document.getElementById('m-shelf').value,
  };
  if (!data.barcode||!data.name||!data.qty||!data.zone||!data.sec||!data.shelf) {
    toast('모든 항목을 입력해주세요.', 'error'); return;
  }
  sendNew(data, () => {
    ['m-barcode','m-name','m-qty','m-sec','m-shelf'].forEach(id => document.getElementById(id).value='');
    document.getElementById('m-zone').value='';
    closeModal();
  });
}

function sendNew(data, cb) {
  fetch('/api/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(r => r.json())
  .then(() => {
    cmdCount++;
    addLog(`신규 입고: ${data.name} ${data.qty}개`, data.barcode, 'NEW');
    toast(`${data.name} 입고 등록 완료 (${data.zone}-${data.sec}-${data.shelf})`, 'success');
    loadInventory();
    cb && cb();
  })
  .catch(() => toast('입고 등록 실패', 'error'));
}

// ── 모달 ─────────────────────────────────────
function openModal()  { document.getElementById('modal').classList.add('open'); }
function closeModal() { document.getElementById('modal').classList.remove('open'); }
document.getElementById('modal').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeModal();
});

// ── 로그 ─────────────────────────────────────
function addLog(msg, barcode, type) {
  const now = new Date();
  const t = now.toTimeString().slice(0,8);
  logEntries.unshift({ t, msg, barcode, type });
  renderLog();
}
function renderLog() {
  const el = document.getElementById('log-list');
  if (!logEntries.length) {
    el.innerHTML = `<div class="log-item"><span class="log-time">--:--:--</span><span class="log-msg" style="color:var(--muted);">명령 로그가 없습니다.</span></div>`;
    return;
  }
  el.innerHTML = logEntries.map(e => {
    const tagColor = e.type==='NEW'?'badge-blue':e.type==='ORDER'?'badge-orange':'badge-green';
    return `<div class="log-item">
      <span class="log-time">${e.t}</span>
      <span class="log-msg">${e.msg} &nbsp;<code style="color:var(--muted);font-size:.75rem;">${e.barcode}</code></span>
      <span class="badge ${tagColor} log-tag">${e.type}</span>
    </div>`;
  }).join('');
}
// ── 주문 관리 ──────────────────────────────────
let orders = [];

function loadOrders() {
  fetch('/api/orders')
    .then(r => r.json())
    .then(data => { orders = data; renderOrders(); renderDashOrders(); populateOrderSelect(); updateStats(); });
}

function renderDashOrders() {
  const tbody = document.getElementById('dash-order-table');
  if (!tbody) return;
  if (!orders.length) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty"><div class="icon">📦</div><p>주문 내역이 없습니다.</p></div></td></tr>`;
    return;
  }
  const statusBadge = { '대기중':'badge-yellow', '처리중':'badge-blue', '완료':'badge-green', '취소':'badge-red' };
  tbody.innerHTML = [...orders].reverse().slice(0, 5).map(o => `<tr>
    <td><code style="color:var(--accent);font-size:.8rem;">${o.id}</code></td>
    <td>${o.name}</td>
    <td style="text-align:center;">${o.qty.toLocaleString()}</td>
    <td>${o.type}</td>
    <td><span class="badge ${statusBadge[o.status]||'badge-yellow'}">${o.status}</span></td>
    <td style="font-size:.78rem;color:var(--muted);">${o.created_at}</td>
  </tr>`).join('');
}

function populateOrderSelect() {
  const sel = document.getElementById('o-barcode');
  if (!sel) return;
  const cur = sel.value;
  sel.innerHTML = '<option value="">-- 재고에서 선택 --</option>';
  Object.entries(inventory).forEach(([bc, item]) => {
    const opt = document.createElement('option');
    opt.value = bc;
    opt.textContent = `${item.name} (${bc}) — 재고 ${item.quantity}개`;
    sel.appendChild(opt);
  });
  sel.value = cur;
}

function toggleOrderForm() {
  const wrap = document.getElementById('order-form-wrap');
  wrap.style.display = wrap.style.display === 'none' ? 'block' : 'none';
  if (wrap.style.display === 'block') populateOrderSelect();
}

function submitOrder() {
  const barcode = document.getElementById('o-barcode').value;
  const qty     = parseInt(document.getElementById('o-qty').value) || 0;
  const type    = document.getElementById('o-type').value;
  const note    = document.getElementById('o-note').value.trim();
  if (!barcode) { toast('품목을 선택해주세요.', 'error'); return; }
  if (qty < 1)  { toast('수량을 1 이상 입력해주세요.', 'error'); return; }
  fetch('/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ barcode, qty, type, note })
  })
  .then(r => r.json())
  .then(res => {
    cmdCount++;
    const itemName = inventory[barcode] ? inventory[barcode].name : barcode;
    addLog(`${type} 주문: ${itemName} ${qty}개`, barcode, 'ORDER');
    toast(`주문 등록 완료 (${res.id})`, 'success');
    document.getElementById('o-qty').value = 1;
    document.getElementById('o-note').value = '';
    document.getElementById('o-barcode').value = '';
    toggleOrderForm();
    loadOrders();
    loadInventory();
  });
}

function updateOrderStatus(id, status) {
  fetch(`/api/orders/${id}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  })
  .then(r => r.json())
  .then(() => { loadOrders(); });
}

function renderOrders() {
  const tbody = document.getElementById('order-table');
  if (!tbody) return;
  if (!orders.length) {
    tbody.innerHTML = `<tr><td colspan="9"><div class="empty"><div class="icon">📦</div><p>주문 내역이 없습니다.</p></div></td></tr>`;
    return;
  }
  const statusBadge = {
    '대기중':  'badge-yellow',
    '처리중':  'badge-blue',
    '완료':    'badge-green',
    '취소':    'badge-red'
  };
  const nextActions = {
    '대기중': [['처리중','처리 시작','badge-blue'],['취소','취소','badge-red']],
    '처리중': [['완료','완료 처리','badge-green'],['취소','취소','badge-red']],
    '완료':   [],
    '취소':   []
  };
  tbody.innerHTML = [...orders].reverse().map(o => {
    const bc = statusBadge[o.status] || 'badge-yellow';
    const actions = (nextActions[o.status] || []).map(([s, label, cls]) =>
      `<button class="btn badge ${cls}" style="cursor:pointer;padding:.2rem .6rem;font-size:.72rem;" onclick="updateOrderStatus('${o.id}','${s}')">${label}</button>`
    ).join(' ');
    return `<tr>
      <td><code style="color:var(--accent);font-size:.8rem;">${o.id}</code></td>
      <td>${o.name}</td>
      <td><code style="color:var(--muted);font-size:.78rem;">${o.barcode}</code></td>
      <td style="text-align:center;">${o.qty.toLocaleString()}</td>
      <td>${o.type}</td>
      <td><span class="badge ${bc}">${o.status}</span></td>
      <td style="font-size:.78rem;color:var(--muted);">${o.created_at}</td>
      <td style="font-size:.8rem;color:var(--muted);">${o.note || '-'}</td>
      <td>${actions || '<span style="color:var(--muted);font-size:.78rem;">-</span>'}</td>
    </tr>`;
  }).join('');
}

// ── 계정 관리 ──────────────────────────────────
function toggleAccForm() {
  const w = document.getElementById('acc-form-wrap');
  w.style.display = w.style.display === 'none' ? 'block' : 'none';
}

function loadAccounts() {
  fetch('/api/users')
    .then(r => r.json())
    .then(users => renderAccounts(users));
}

function renderAccounts(users) {
  const tbody = document.getElementById('acc-table');
  if (!tbody) return;
  const roleColor = r => r === 'Admin' ? 'badge-orange' : 'badge-blue';
  tbody.innerHTML = users.map(u => `<tr>
    <td><code style="color:var(--accent);">${u.username}</code></td>
    <td><span class="badge ${roleColor(u.role)}">${u.role}</span></td>
    <td>
      <div style="display:flex;gap:.4rem;align-items:center;">
        <input type="password" id="pw-${u.username}" placeholder="새 비밀번호" style="width:140px;padding:.35rem .6rem;border-radius:6px;background:rgba(255,255,255,.06);border:1px solid var(--border);color:var(--text);font-size:.8rem;"/>
        <button class="btn btn-primary" style="padding:.3rem .7rem;font-size:.78rem;" onclick="changePassword('${u.username}')">변경</button>
      </div>
    </td>
    <td>
      <button class="btn btn-danger" style="padding:.3rem .7rem;font-size:.78rem;" onclick="deleteAccount('${u.username}')">삭제</button>
    </td>
  </tr>`).join('');
}

function submitAddAccount() {
  const username = document.getElementById('acc-id').value.trim();
  const role     = document.getElementById('acc-role').value;
  const pw       = document.getElementById('acc-pw').value;
  const pw2      = document.getElementById('acc-pw2').value;
  if (!username) { toast('아이디를 입력해주세요.', 'error'); return; }
  if (!pw)       { toast('비밀번호를 입력해주세요.', 'error'); return; }
  if (pw !== pw2){ toast('비밀번호가 일치하지 않습니다.', 'error'); return; }
  fetch('/api/users', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ username, password: pw, role })
  })
  .then(r => r.json())
  .then(res => {
    if (res.status === 'success') {
      toast(`계정 [${username}] 추가 완료`, 'success');
      document.getElementById('acc-id').value = '';
      document.getElementById('acc-pw').value = '';
      document.getElementById('acc-pw2').value = '';
      toggleAccForm();
      loadAccounts();
    } else {
      toast(res.message || '계정 추가 실패', 'error');
    }
  });
}

function changePassword(username) {
  const pw = document.getElementById('pw-' + username).value;
  if (!pw) { toast('새 비밀번호를 입력해주세요.', 'error'); return; }
  fetch(`/api/users/${username}/password`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ password: pw })
  })
  .then(r => r.json())
  .then(res => {
    if (res.status === 'success') {
      toast(`[${username}] 비밀번호 변경 완료`, 'success');
      document.getElementById('pw-' + username).value = '';
    } else {
      toast(res.message || '변경 실패', 'error');
    }
  });
}

function deleteAccount(username) {
  if (!confirm(`[${username}] 계정을 삭제할까요?`)) return;
  fetch(`/api/users/${username}`, { method: 'DELETE' })
  .then(r => r.json())
  .then(res => {
    if (res.status === 'success') {
      toast(`[${username}] 계정 삭제 완료`, 'success');
      loadAccounts();
    } else {
      toast(res.message || '삭제 실패', 'error');
    }
  });
}

function clearLog() {
  logEntries = [];
  renderLog();
  toast('로그를 초기화했습니다.', 'info');
}

// ── 위치 배지 ─────────────────────────────────
function locationBadge(loc) {
  if (!loc) return '-';
  const z = loc.split('-')[0];
  return `<span class="zone-tag zone-${z}">${z}</span> <span style="color:var(--muted);font-size:.78rem;">${loc}</span>`;
}

// ── 토스트 ────────────────────────────────────
function toast(msg, type='info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// ── 시작 ─────────────────────────────────────
window.onload = () => {
  loadInventory();
  loadOrders();
  setInterval(loadInventory, 5000);
  setInterval(loadOrders, 5000);
};
</script>
</body>
</html>
"""

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_PATH):
        default = [
            {'username': 'admin',    'password': hash_pw('admin123'), 'role': 'Admin'},
            {'username': 'operator', 'password': hash_pw('op123'),    'role': 'Operator'},
        ]
        with open(USERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(USERS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = load_users()
        user = next((u for u in users if u['username'] == username and u['password'] == hash_pw(password)), None)
        if user:
            session['username'] = user['username']
            session['role']     = user['role']
            return redirect(url_for('dashboard'))
        return render_template_string(LOGIN_PAGE, error='아이디 또는 비밀번호가 올바르지 않습니다.')
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def intro():
    return render_template_string(INTRO_PAGE)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(HTML_PAGE)

@app.route('/api/inventory')
@login_required
def get_inventory():
    if not os.path.exists(DATA_PATH):
        return jsonify({})
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        try:
            return jsonify(json.load(f))
        except Exception:
            return jsonify({})

def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_data(inventory):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

@app.route('/api/update', methods=['POST'])
@login_required
def update_inventory():
    data = request.get_json()
    cmd_type = data.get('type')

    with open(CMD_PATH, 'a', encoding='utf-8') as f:
        if cmd_type == 'QTY':
            f.write(f"QTY,{data.get('barcode')},{data.get('change')}\n")
        elif cmd_type == 'NEW':
            f.write(f"NEW,{data.get('barcode')},{data.get('name')},"
                    f"{data.get('qty')},{data.get('zone')},"
                    f"{data.get('sec')},{data.get('shelf')}\n")

    inventory = load_data()
    if cmd_type == 'QTY':
        barcode = data.get('barcode')
        change = int(data.get('change', 0))
        if barcode in inventory:
            inventory[barcode]['quantity'] = max(0, inventory[barcode]['quantity'] + change)
    elif cmd_type == 'NEW':
        barcode = data.get('barcode')
        zone = data.get('zone', '')
        sec = data.get('sec', '')
        shelf = data.get('shelf', '')
        inventory[barcode] = {
            'name': data.get('name', ''),
            'quantity': int(data.get('qty', 0)),
            'location': f"{zone}-{sec}-{shelf}"
        }
    save_data(inventory)

    return jsonify({'status': 'success'})

def load_orders():
    if not os.path.exists(ORDERS_PATH):
        return []
    with open(ORDERS_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_orders(orders):
    with open(ORDERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

@app.route('/api/inventory/<barcode>', methods=['DELETE'])
@login_required
def delete_item(barcode):
    inventory = load_data()
    if barcode not in inventory:
        return jsonify({'status': 'error', 'message': '존재하지 않는 바코드입니다.'})
    del inventory[barcode]
    save_data(inventory)
    return jsonify({'status': 'success'})

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    return jsonify(load_orders())

@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    from datetime import datetime
    data = request.get_json()
    barcode = data.get('barcode', '')
    qty = int(data.get('qty', 1))
    order_type = data.get('type', '출고')
    inventory = load_data()
    name = inventory.get(barcode, {}).get('name', barcode)

    if barcode in inventory:
        if order_type == '출고':
            inventory[barcode]['quantity'] = max(0, inventory[barcode]['quantity'] - qty)
        elif order_type == '발주(재입고)':
            inventory[barcode]['quantity'] += qty
        save_data(inventory)

    orders = load_orders()
    order_id = f"ORD{len(orders)+1:04d}"
    orders.append({
        'id':         order_id,
        'barcode':    barcode,
        'name':       name,
        'qty':        qty,
        'type':       order_type,
        'status':     '대기중',
        'note':       data.get('note', ''),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    save_orders(orders)
    return jsonify({'status': 'success', 'id': order_id})

@app.route('/api/orders/<order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    orders = load_orders()
    for o in orders:
        if o['id'] == order_id:
            o['status'] = new_status
            break
    save_orders(orders)
    return jsonify({'status': 'success'})

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': '권한이 없습니다.'}), 403
    users = load_users()
    return jsonify([{'username': u['username'], 'role': u['role']} for u in users])

@app.route('/api/users', methods=['POST'])
@login_required
def add_user():
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': '권한이 없습니다.'}), 403
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    role     = data.get('role', 'Operator')
    if not username or not password:
        return jsonify({'status': 'error', 'message': '아이디와 비밀번호를 입력하세요.'})
    users = load_users()
    if any(u['username'] == username for u in users):
        return jsonify({'status': 'error', 'message': '이미 존재하는 아이디입니다.'})
    users.append({'username': username, 'password': hash_pw(password), 'role': role})
    save_users(users)
    return jsonify({'status': 'success'})

@app.route('/api/users/<username>/password', methods=['POST'])
@login_required
def change_password(username):
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': '권한이 없습니다.'}), 403
    data = request.get_json()
    new_pw = data.get('password', '')
    if not new_pw:
        return jsonify({'status': 'error', 'message': '새 비밀번호를 입력하세요.'})
    users = load_users()
    for u in users:
        if u['username'] == username:
            u['password'] = hash_pw(new_pw)
            break
    else:
        return jsonify({'status': 'error', 'message': '존재하지 않는 계정입니다.'})
    save_users(users)
    return jsonify({'status': 'success'})

@app.route('/api/users/<username>', methods=['DELETE'])
@login_required
def delete_user(username):
    if session.get('role') != 'Admin':
        return jsonify({'status': 'error', 'message': '권한이 없습니다.'}), 403
    if username == session.get('username'):
        return jsonify({'status': 'error', 'message': '자신의 계정은 삭제할 수 없습니다.'})
    users = load_users()
    new_users = [u for u in users if u['username'] != username]
    if len(new_users) == len(users):
        return jsonify({'status': 'error', 'message': '존재하지 않는 계정입니다.'})
    save_users(new_users)
    return jsonify({'status': 'success'})

def save_users(users):
    with open(USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import sys, io, threading, webbrowser, socket
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    _debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    _port  = int(os.environ.get('PORT', 5000))
    _host  = os.environ.get('HOST', '0.0.0.0')

    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"[SERVER] 내 컴퓨터: http://127.0.0.1:{_port}")
    print(f"[SERVER] 네트워크: http://{local_ip}:{_port}")
    print(f"[SERVER] 데이터 경로: {_BASE}")
    if not _debug and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.5, lambda: webbrowser.open(f'http://127.0.0.1:{_port}/login')).start()
    app.run(host=_host, debug=_debug, port=_port)
