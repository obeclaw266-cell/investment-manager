from flask import Flask, render_template_string, request, jsonify, send_file
import json, os, requests

app = Flask(__name__)
DATA_FILE = 'portfolio.json'
BACKUP_DIR = 'backups'

def get_price(code):
    for url in [f"https://query1.finance.yahoo.com/v8/finance/chart/{code}.TW", f"https://query1.finance.yahoo.com/v8/finance/chart/{code}"]:
        try:
            r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
            if r.status_code==200:
                d=r.json()
                if d.get('chart',{}).get('result'):
                    return d['chart']['result'][0]['meta'].get('regularMarketPrice')
        except: pass
    return None

def load_data():
    if os.path.exists(DATA_FILE):
        return json.load(open(DATA_FILE, encoding='utf-8'))
    return {"holdings":[],"transactions":[],"loans":[],"profile":{"name":"投資者","email":"","risk_level":"穩健型"},"settings":{"target_allocation":{"原型":70,"槓桿":15,"類現金":15},"loan_interest_rate":2.5,"loan_limit_percent":20,"new_funds":0}}

def save_data(d): 
    json.dump(d, open(DATA_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

HTML = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport"
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="投資系統"> content="width=device-width,initial-scale=1">
<title>投資管理系統</title>
<link rel="manifest" href="/static/manifest.json">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
h1 { font-size: 28px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
h2 { font-size: 20px; margin-bottom: 15px; color: #333; }
h3 { font-size: 16px; margin-bottom: 10px; color: #555; }
.nav { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; background: white; padding: 12px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav button { padding: 10px 16px; border: none; background: transparent; color: #666; cursor: pointer; border-radius: 6px; font-size: 14px; transition: all 0.2s; }
.nav button:hover { background: #f0f0f0; }
.nav button.active { background: #007bff; color: white; }
.nav button.refresh { background: #28a745; color: white; margin-left: auto; }
.card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
th { background: #f8f9fa; color: #666; font-weight: 600; }
.profit { color: #28a745; font-weight: 600; }
.loss { color: #dc3545; font-weight: 600; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #555; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
.btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }
.btn-primary { background: #007bff; color: white; }
.btn-primary:hover { background: #0056b3; }
.btn-danger { background: #dc3545; color: white; }
.btn-danger:hover { background: #c82333; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover { background: #5a6268; }
.btn-success { background: #28a745; color: white; }
.btn-success:hover { background: #218838; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }
.stat-box { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; }
.stat-box.green { background: linear-gradient(135deg, #11998e, #38ef7d); }
.stat-box.red { background: linear-gradient(135deg, #eb3349, #f45c43); }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-label { opacity: 0.9; font-size: 14px; margin-top: 5px; }
.modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
.modal.show { display: flex; align-items: center; justify-content: center; }
.modal-content { background: white; max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto; border-radius: 12px; padding: 25px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-close { background: none; border: none; font-size: 28px; cursor: pointer; color: #999; }
.tag { padding: 3px 8px; border-radius: 4px; font-size: 12px; color: white; }
.tag原型 { background: #667eea; }
.tag槓桿 { background: #f45c43; }
.tag類現金 { background: #38ef7d; color: #333; }
.tag買 { background: #28a745; }
.tag賣 { background: #dc3545; }
.tab-content { display: none; }
.tab-content.active { display: block; }
.user-bar { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; background: white; padding: 15px; border-radius: 10px; }
.user-avatar { width: 40px; height: 40px; background: #007bff; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; }
.user-info { flex: 1; }
.user-name { font-weight: 600; color: #333; }
.user-email { font-size: 12px; color: #999; }
.rebalance-mode { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.rebalance-mode button { padding: 12px 20px; border: 2px solid #007bff; background: white; color: #007bff; border-radius: 8px; font-size: 14px; cursor: pointer; transition: all 0.2s; }
.rebalance-mode button.active, .rebalance-mode button:hover { background: #007bff; color: white; }
.result-box { padding: 15px; border-radius: 8px; margin: 10px 0; background: #f8f9fa; }
.result-buy { background: #d4edda; border-left: 4px solid #28a745; }
.result-sell { background: #f8d7da; border-left: 4px solid #dc3545; }
.result-info { background: #d1ecf1; border-left: 4px solid #17a2b8; }
.result-amount { font-weight: bold; font-size: 16px; }
.result-detail { font-size: 13px; color: #666; margin-top: 5px; }
.last-update { font-size: 12px; color: #999; margin-left: auto; }
</style>
</head>
<body>
<div class="container">
<h1>💰 投資管理系統 <span class="last-update" id="last-update"></span></h1>

<div class="user-bar">
  <div class="user-avatar" id="ua">?</div>
  <div class="user-info">
    <div class="user-name" id="un">載入中</div>
    <div class="user-email" id="ue"></div>
  </div>
  <button class="btn btn-primary" onclick="showPage('profile')">👤 個人資料</button>
  <button class="btn btn-secondary" onclick="showPage('manual')">📖 說明</button>
</div>

<div class="nav">
  <button onclick="showPage('inventory')" id="btn-inventory">📊 庫存</button>
  <button onclick="showPage('transactions')" id="btn-transactions">📝 交易</button>
  <button onclick="showPage('allocation')" id="btn-allocation">🥧 配置</button>
  <button onclick="showPage('rebalance')" id="btn-rebalance">⚖️ 平衡</button>
  <button onclick="showPage('loans')" id="btn-loans">📋 質押</button>
  <button onclick="showPage('settings')" id="btn-settings">⚙️ 設定</button>
  <button class="refresh" onclick="updatePrices()" id="btn-refresh">🔄 更新股價</button>
</div>

<div id="page-inventory" class="tab-content active">
  <div class="card">
    <div style="display:flex;justify-content:space-between;margin-bottom:15px">
      <h2>📊 股票庫存</h2>
      <button class="btn btn-primary" onclick="showAddForm()">+ 新增交易</button>
    </div>
    <div class="stats">
      <div class="stat-box"><div class="stat-value" id="total-value">$0</div><div class="stat-label">總市值</div></div>
      <div class="stat-box green"><div class="stat-value" id="total-cost">$0</div><div class="stat-label">總成本</div></div>
      <div class="stat-box" id="total-pl-box"><div class="stat-value" id="total-pl">$0</div><div class="stat-label">總損益</div></div>
    </div>
    <table>
      <thead><tr><th>代號</th><th>名稱</th><th>屬性</th><th>股數</th><th>均價</th><th>成本</th><th>現價</th><th>市值</th><th>佔比</th><th>損益</th><th>操作</th></tr></thead>
      <tbody id="holdings-table"></tbody>
    </table>
  </div>
</div>

<div id="page-transactions" class="tab-content">
  <div class="card">
    <div style="display:flex;justify-content:space-between;margin-bottom:15px">
      <h2>📝 交易記錄</h2>
      <button class="btn btn-primary" onclick="showAddForm()">+ 新增交易</button>
    </div>
    <table>
      <thead><tr><th>日期</th><th>代號</th><th>名稱</th><th>買/賣</th><th>股數</th><th>價格</th><th>金額</th><th>操作</th></tr></thead>
      <tbody id="transactions-table"></tbody>
    </table>
  </div>
</div>

<div id="page-allocation" class="tab-content">
  <div class="card">
    <h2>🥧 資產配置</h2>
    <div style="display:flex;gap:40px;flex-wrap:wrap">
      <div style="flex:1;min-width:300px"><canvas id="allocation-chart"></canvas></div>
      <div style="flex:1;min-width:300px"><table id="allocation-table"></table></div>
    </div>
  </div>
</div>

<div id="page-rebalance" class="tab-content">
  <div class="card">
    <h2>⚖️ 再平衡試算</h2>
    <div class="rebalance-mode">
      <button onclick="setRebalanceMode('A')" id="mode-A" class="active">A. 比率再平衡 (Ratio)</button>
      <button onclick="setRebalanceMode('B')" id="mode-B">B. 聰明再平衡 (Smart)</button>
      <button onclick="setRebalanceMode('C')" id="mode-C">C. 無腦再平衡 (Brainless)</button>
    </div>
    <div class="form-group">
      <label>💵 新資金投入 (動態再平衡)</label>
      <div style="display:flex;gap:10px;margin-top:10px">
        <input type="number" id="new-funds" placeholder="輸入金額" value="0" style="max-width:200px">
        <button class="btn btn-primary" onclick="calculateRebalance()">D. 執行計算</button>
      </div>
    </div>
    <div id="rebalance-results"></div>
  </div>
</div>

<div id="page-loans" class="tab-content">
  <div class="card">
    <div style="display:flex;justify-content:space-between;margin-bottom:15px">
      <h2>📋 質押管理</h2>
      <button class="btn btn-primary" onclick="showLoanForm()">+ 新增質押</button>
    </div>
    <div class="stats">
      <div class="stat-box"><div class="stat-value" id="loan-total">$0</div><div class="stat-label">質押總額</div></div>
      <div class="stat-box green"><div class="stat-value" id="loan-available">$0</div><div class="stat-label">可用額度</div></div>
      <div class="stat-box" id="loan-usage-box"><div class="stat-value" id="loan-usage">0%</div><div class="stat-label">使用率</div></div>
    </div>
    <table>
      <thead><tr><th>股票</th><th>股數</th><th>市值</th><th>可質押</th><th>借款</th><th>利率</th><th>操作</th></tr></thead>
      <tbody id="loans-table"></tbody>
    </table>
  </div>
</div>

<div id="page-profile" class="tab-content">
  <div class="card">
    <h2>👤 個人資料</h2>
    <div class="form-group"><label>姓名</label><input type="text" id="profile-name"></div>
    <div class="form-group"><label>Email</label><input type="email" id="profile-email"></div>
    <div class="form-group"><label>風險承受度</label>
      <select id="profile-risk">
        <option value="保守型">保守型</option>
        <option value="穩健型">穩健型</option>
        <option value="積極型">積極型</option>
      </select>
    </div>
    <button class="btn btn-primary" onclick="saveProfile()">💾 儲存</button>
  </div>
</div>

<div id="page-manual" class="tab-content">
  <div class="card">
    <h2>📖 使用說明</h2>
    <p style="color:#666;margin:10px 0"><b>A. 比率再平衡:</b> 根據目前市值計算，賣出漲多的，買入漲少的，回到目標比例</p>
    <p style="color:#666;margin:10px 0"><b>B. 聰明再平衡:</b> 會計算具體股數（以千股為單位），顯示買入/賣出金額</p>
    <p style="color:#666;margin:10px 0"><b>C. 無腦再平衡:</b> 只買入，不賣出（若持股比例已高於目標則不動作）</p>
    <p style="color:#666;margin:10px 0"><b>動態再平衡:</b> 輸入新資金金額後，納入計算（總市值 + 新資金）</p>
  </div>
</div>

<div id="page-settings" class="tab-content">
  <div class="card">
    <h2>⚙️ 設定</h2>
    <h3>目標配置(%)</h3>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:15px 0;max-width:400px">
      <div class="form-group"><label>原型</label><input type="number" id="target-prototype" value="70"></div>
      <div class="form-group"><label>槓桿</label><input type="number" id="target-leverage" value="15"></div>
      <div class="form-group"><label>類現金</label><input type="number" id="target-cash" value="15"></div>
    </div>
    <h3>質押設定</h3>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin:15px 0;max-width:300px">
      <div class="form-group"><label>利率(%)</label><input type="number" id="loan-interest" value="2.5"></div>
      <div class="form-group"><label>成數(%)</label><input type="number" id="loan-percent" value="60"></div>
    </div>
    <button class="btn btn-primary" onclick="saveSettings()" style="margin-bottom:20px">💾 儲存設定</button>
    <hr style="margin:20px 0">
    <h3>📁 資料管理</h3>
    <div style="display:flex;gap:10px;margin-top:15px;flex-wrap:wrap">
      <button class="btn btn-success" onclick="backupData()">💾 備份資料</button>
      <button class="btn btn-secondary" onclick="restoreData()">📥 匯入備份</button>
      <button class="btn btn-danger" onclick="clearData()">🗑 清除所有資料</button>
    </div>
  </div>
</div>
</div>

<div id="add-modal" class="modal">
  <div class="modal-content">
    <div class="modal-header"><h2>新增交易</h2><button class="modal-close" onclick="hideAddForm()">×</button></div>
    <div class="form-group"><label>股票代號 *</label><input type="text" id="trade-code" placeholder="例如: 00662"></div>
    <div class="form-group"><label>股票名稱</label><input type="text" id="trade-name" placeholder="例如: 富邦NASDAQ"></div>
    <div class="form-group"><label>屬性 *</label>
      <select id="trade-type">
        <option value="原型">原型</option>
        <option value="槓桿">槓桿</option>
        <option value="類現金">類現金</option>
      </select>
    </div>
    <div class="form-group"><label>買/賣 *</label>
      <select id="trade-action">
        <option value="買">📈 買</option>
        <option value="賣">📉 賣</option>
      </select>
    </div>
    <div class="form-group"><label>股數 *</label><input type="number" id="trade-shares" placeholder="例如: 1000"></div>
    <div class="form-group"><label>價格 *</label><input type="number" id="trade-price" step="0.01" placeholder="例如: 100"></div>
    <div class="form-group"><label>日期</label><input type="date" id="trade-date"></div>
    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:20px">
      <button class="btn btn-secondary" onclick="hideAddForm()">取消</button>
      <button class="btn btn-primary" onclick="addTransaction()">💾 儲存</button>
    </div>
  </div>
</div>

<div id="loan-modal" class="modal">
  <div class="modal-content">
    <div class="modal-header"><h2>新增質押</h2><button class="modal-close" onclick="hideLoanForm()">×</button></div>
    <div class="form-group"><label>股票代號 *</label><select id="loan-stock-select"></select></div>
    <div class="form-group"><label>質押股數 *</label><input type="number" id="loan-shares" placeholder="例如: 1000"></div>
    <div class="form-group"><label>借款金額 *</label><input type="number" id="loan-amount" placeholder="例如: 100000"></div>
    <div class="form-group"><label>利率(%)</label><input type="number" id="loan-rate" step="0.1" value="2.5"></div>
    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:20px">
      <button class="btn btn-secondary" onclick="hideLoanForm()">取消</button>
      <button class="btn btn-primary" onclick="addLoan()">💾 儲存</button>
    </div>
  </div>
</div>

<script>
let data = {{ data|tojson }};
let allocationChart = null;
let currentMode = 'A';

render();

function render() {
    renderProfile();
    renderHoldings();
    renderTransactions();
    renderLoans();
    renderAllocation();
    renderSettings();
    document.getElementById('last-update').textContent = '更新: ' + new Date().toLocaleString('zh-TW');
}

function renderProfile() {
    let p = data.profile || {};
    document.getElementById('un').textContent = p.name || '訪客';
    document.getElementById('ue').textContent = p.email || '';
    document.getElementById('ua').textContent = (p.name || '?')[0].toUpperCase();
    document.getElementById('profile-name').value = p.name || '';
    document.getElementById('profile-email').value = p.email || '';
    document.getElementById('profile-risk').value = p.risk_level || '穩健型';
}

function renderHoldings() {
    let tbody = document.getElementById('holdings-table');
    tbody.innerHTML = '';
    let totalValue = 0, totalCost = 0;
    
    data.holdings.forEach((h, i) => {
        let mv = h.shares * h.price;
        let pl = mv - h.cost;
        totalValue += mv;
        totalCost += h.cost;
        
        tbody.innerHTML += '<tr>' +
            '<td><strong>' + h.code + '</strong></td>' +
            '<td>' + (h.name || '-') + '</td>' +
            '<td><span class="tag tag' + h.type + '">' + h.type + '</span></td>' +
            '<td>' + h.shares.toLocaleString() + '</td>' +
            '<td>' + h.avgPrice.toFixed(2) + '</td>' +
            '<td>' + h.cost.toLocaleString() + '</td>' +
            '<td><strong>' + h.price.toFixed(2) + '</strong></td>' +
            '<td>' + mv.toLocaleString() + '</td>' +
            '<td>' + ((mv/(totalValue||1))*100).toFixed(1) + '%</td>' +
            '<td class="' + (pl>=0?'profit':'loss') + '"><strong>' + (pl>=0?'+':'') + pl.toLocaleString() + '</strong></td>' +
            '<td><button class="btn btn-danger" style="padding:5px 10px;font-size:12px" onclick="deleteHolding(' + i + ')">🗑</button></td>' +
        '</tr>';
    });
    
    document.getElementById('total-value').textContent = '$' + totalValue.toLocaleString();
    document.getElementById('total-cost').textContent = '$' + totalCost.toLocaleString();
    let totalPL = totalValue - totalCost;
    document.getElementById('total-pl').textContent = (totalPL>=0?'+':'') + '$' + totalPL.toLocaleString();
    document.getElementById('total-pl-box').className = 'stat-box ' + (totalPL>=0?'green':'red');
}

function renderTransactions() {
    let tbody = document.getElementById('transactions-table');
    tbody.innerHTML = '';
    
    data.transactions.slice().reverse().forEach((t, i) => {
        tbody.innerHTML += '<tr>' +
            '<td>' + t.date + '</td>' +
            '<td><strong>' + t.code + '</strong></td>' +
            '<td>' + (t.name || '-') + '</td>' +
            '<td><span class="tag tag' + t.action + '">' + t.action + '</span></td>' +
            '<td>' + t.shares.toLocaleString() + '</td>' +
            '<td>' + t.price.toFixed(2) + '</td>' +
            '<td>' + (t.shares * t.price).toLocaleString() + '</td>' +
            '<td><button class="btn btn-danger" style="padding:5px 10px;font-size:12px" onclick="deleteTransaction(' + (data.transactions.length-1-i) + ')">🗑</button></td>' +
        '</tr>';
    });
}

function renderLoans() {
    let tbody = document.getElementById('loans-table');
    tbody.innerHTML = '';
    data.loans = data.loans || [];
    
    let totalValue = data.holdings.reduce((s, h) => s + h.shares * h.price, 0);
    let loanPercent = data.settings?.loan_limit_percent || 20;
    let maxLoan = totalValue * loanPercent / 100;
    let totalLoan = 0;
    
    data.loans.forEach((l, i) => {
        let h = data.holdings.find(x => x.code === l.code);
        let mv = h ? h.shares * h.price : 0;
        let canLoan = mv * loanPercent / 100;
        totalLoan += l.amount;
        
        tbody.innerHTML += '<tr>' +
            '<td><strong>' + l.code + '</strong></td>' +
            '<td>' + l.shares.toLocaleString() + '</td>' +
            '<td>' + mv.toLocaleString() + '</td>' +
            '<td>' + canLoan.toLocaleString() + '</td>' +
            '<td>' + l.amount.toLocaleString() + '</td>' +
            '<td>' + l.rate + '%</td>' +
            '<td><button class="btn btn-danger" style="padding:5px 10px;font-size:12px" onclick="deleteLoan(' + i + ')">🗑</button></td>' +
        '</tr>';
    });
    
    let usagePercent = maxLoan > 0 ? (totalLoan / maxLoan * 100) : 0;
    document.getElementById('loan-total').textContent = '$' + totalLoan.toLocaleString();
    document.getElementById('loan-available').textContent = '$' + Math.max(0, maxLoan - totalLoan).toLocaleString();
    document.getElementById('loan-usage').textContent = usagePercent.toFixed(0) + '%';
    document.getElementById('loan-usage-box').className = 'stat-box ' + (usagePercent > 70 ? 'red' : 'green');
    
    let select = document.getElementById('loan-stock-select');
    select.innerHTML = data.holdings.map(h => '<option value="' + h.code + '">' + h.code + ' - ' + (h.name || h.type) + '</option>').join('');
}

function renderAllocation() {
    let tbody = document.getElementById('allocation-table');
    tbody.innerHTML = '';
    
    let stats = {};
    let total = 0;
    data.holdings.forEach(h => {
        let v = h.shares * h.price;
        stats[h.type] = (stats[h.type] || 0) + v;
        total += v;
    });
    
    let colors = {'原型': '#667eea', '槓桿': '#f45c43', '類現金': '#38ef7d'};
    
    for (let [t, v] of Object.entries(stats)) {
        tbody.innerHTML += '<tr><td style="color:' + colors[t] + '">● ' + t + '</td><td>' + v.toLocaleString() + '</td><td>' + ((v/(total||1))*100).toFixed(1) + '%</td></tr>';
    }
    
    let ctx = document.getElementById('allocation-chart');
    if (allocationChart) allocationChart.destroy();
    allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(stats),
            datasets: [{data: Object.values(stats), backgroundColor: Object.keys(stats).map(t => colors[t])}]
        },
        options: {responsive: true, plugins: {legend: {position: 'bottom'}}}
    });
}

function renderSettings() {
    let s = data.settings || {};
    document.getElementById('target-prototype').value = s.target_allocation?.原型 || 70;
    document.getElementById('target-leverage').value = s.target_allocation?.槓桿 || 15;
    document.getElementById('target-cash').value = s.target_allocation?.類現金 || 15;
    document.getElementById('loan-interest').value = s.loan_interest_rate || 2.5;
    document.getElementById('loan-percent').value = s.loan_limit_percent || 20;
    document.getElementById('new-funds').value = s.new_funds || 0;
}

function showPage(page) {
    document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    document.querySelectorAll('.nav button').forEach(x => x.classList.remove('active'));
    document.getElementById('btn-' + page).classList.add('active');
    
    if (page === 'rebalance') {
        calculateRebalance();
    }
}

function setRebalanceMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.rebalance-mode button').forEach(b => b.classList.remove('active'));
    document.getElementById('mode-' + mode).classList.add('active');
    calculateRebalance();
}

function calculateRebalance() {
    let nf = parseInt(document.getElementById('new-funds').value) || 0;
    let rs = document.getElementById('rebalance-results');
    let tv = data.holdings.reduce((s, h) => s + h.shares * h.price, 0);
    let tg = data.settings?.target_allocation || {原型: 70, 槓桿: 15, 類現金: 15};
    
    if (tv === 0) {
        rs.innerHTML = '<div class="result-box result-info">尚無持股資料</div>';
        return;
    }
    
    let mn = {'A': '比率再平衡 (Ratio)', 'B': '聰明再平衡 (Smart)', 'C': '無腦再平衡 (Brainless)'};
    let modeTitle = mn[currentMode];
    if (nf > 0) modeTitle += ' + 動態再平衡';
    
    rs.innerHTML = '<h3>' + modeTitle + '</h3>';
    
    let current = {};
    data.holdings.forEach(h => {
        let v = h.shares * h.price;
        current[h.type] = (current[h.type] || 0) + v;
    });
    
    let totalWithFunds = tv + nf;
    
    for (let [typeName, targetPct] of Object.entries(tg)) {
        let currentValue = current[typeName] || 0;
        let currentPct = tv > 0 ? currentValue / tv * 100 : 0;
        
        let targetValue;
        if (currentMode === 'C') {
            targetValue = totalWithFunds * targetPct / 100;
        } else {
            targetValue = (tv + nf) * targetPct / 100;
        }
        
        let diff = targetValue - currentValue;
        
        // C 模式邏輯：只買入不賣出，若持股比例已高於目標則不動作
        if (currentMode === 'C' && nf > 0 && diff < 0) {
            continue;
        }
        if (currentMode === 'C' && currentPct > targetPct) {
            continue;
        }
        
        if (Math.abs(diff) < 100) continue;
        
        let action = diff > 0 ? '買入' : '賣出';
        let resultClass = diff > 0 ? 'result-buy' : 'result-sell';
        
        let shares = 0;
        if (currentMode === 'B' && Math.abs(diff) > 0) {
            let typeHoldings = data.holdings.filter(h => h.type === typeName);
            let totalShares = typeHoldings.reduce((s, h) => s + h.shares, 0);
            let avgPrice = currentValue / (totalShares || 1);
            shares = Math.round(Math.abs(diff) / avgPrice / 1000) * 1000;
        }
        
        let amount = Math.abs(diff);
        
        let extra = '';
        if (currentMode === 'B' && shares > 0) {
            extra = '<div class="result-detail">約 ' + shares.toLocaleString() + ' 股</div>';
        }
        if (currentMode === 'C' && nf > 0) {
            extra = '<div class="result-detail">(使用新資金)</div>';
        }
        
        rs.innerHTML += '<div class="result-box ' + resultClass + '">' +
            '<b>' + typeName + '</b> (' + currentPct.toFixed(1) + '% → ' + targetPct + '%)<br>' +
            '<span class="result-amount">' + action + ' $' + amount.toLocaleString() + '</span>' +
            extra +
        '</div>';
    }
    
    if (nf > 0) {
        rs.innerHTML += '<div class="result-box result-info">💵 新資金投入: $' + nf.toLocaleString() + '</div>';
    }
}

function showAddForm() {
    document.getElementById('add-modal').classList.add('show');
    document.getElementById('trade-date').value = new Date().toISOString().split('T')[0];
}

function hideAddForm() {
    document.getElementById('add-modal').classList.remove('show');
}

function showLoanForm() {
    document.getElementById('loan-modal').classList.add('show');
}

function hideLoanForm() {
    document.getElementById('loan-modal').classList.remove('show');
}

function addTransaction() {
    let code = document.getElementById('trade-code').value.trim().toUpperCase();
    let name = document.getElementById('trade-name').value.trim();
    let type = document.getElementById('trade-type').value;
    let action = document.getElementById('trade-action').value;
    let shares = parseInt(document.getElementById('trade-shares').value);
    let price = parseFloat(document.getElementById('trade-price').value);
    let date = document.getElementById('trade-date').value;
    
    if (!code || !shares || !price) {
        alert('請填寫必填欄位');
        return;
    }
    
    data.transactions.push({code, name, type, action, shares, price, date});
    
    let h = data.holdings.find(x => x.code === code);
    if (action === '買') {
        if (h) {
            h.shares += shares;
            h.cost += shares * price;
            h.avgPrice = h.cost / h.shares;
            h.price = price;
        } else {
            data.holdings.push({code, name, type, shares, avgPrice: price, cost: shares * price, price});
        }
    } else if (h) {
        h.shares -= shares;
        h.cost = h.shares * h.avgPrice;
        h.price = price;
        if (h.shares <= 0) data.holdings = data.holdings.filter(x => x.code !== code);
    }
    
    saveData();
    hideAddForm();
}

function addLoan() {
    let code = document.getElementById('loan-stock-select').value;
    let shares = parseInt(document.getElementById('loan-shares').value);
    let amount = parseInt(document.getElementById('loan-amount').value);
    let rate = parseFloat(document.getElementById('loan-rate').value);
    
    if (!code || !shares || !amount) {
        alert('請填寫必填欄位');
        return;
    }
    
    data.loans = data.loans || [];
    data.loans.push({code, shares, amount, rate});
    
    saveData();
    hideLoanForm();
}

function deleteHolding(i) {
    if (confirm('確定刪除這筆持股？')) {
        data.holdings.splice(i, 1);
        saveData();
    }
}

function deleteTransaction(i) {
    if (confirm('確定刪除這筆交易？')) {
        data.transactions.splice(i, 1);
        saveData();
    }
}

function deleteLoan(i) {
    if (confirm('確定刪除這筆質押？')) {
        data.loans.splice(i, 1);
        saveData();
    }
}

function saveProfile() {
    data.profile = {
        name: document.getElementById('profile-name').value,
        email: document.getElementById('profile-email').value,
        risk_level: document.getElementById('profile-risk').value
    };
    saveData();
    alert('個人資料已儲存');
    render();
}

function saveSettings() {
    data.settings = data.settings || {};
    data.settings.target_allocation = {
        原型: parseInt(document.getElementById('target-prototype').value),
        槓桿: parseInt(document.getElementById('target-leverage').value),
        類現金: parseInt(document.getElementById('target-cash').value)
    };
    data.settings.loan_interest_rate = parseFloat(document.getElementById('loan-interest').value);
    data.settings.loan_limit_percent = parseInt(document.getElementById('loan-percent').value);
    data.settings.new_funds = parseInt(document.getElementById('new-funds').value) || 0;
    saveData();
    alert('設定已儲存');
    render();
}

function backupData() {
    fetch('/api/backup', {method: 'POST'})
        .then(r => r.blob())
        .then(blob => {
            let url = URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = 'portfolio_backup.json';
            a.click();
            alert('備份已下載');
        });
}

function restoreData() {
    let input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
        let file = e.target.files[0];
        let reader = new FileReader();
        reader.onload = e2 => {
            try {
                data = JSON.parse(e2.target.result);
                saveData();
                alert('資料已匯入');
                render();
            } catch(err) {
                alert('檔案格式錯誤');
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

function clearData() {
    if (confirm('確定要清除所有資料嗎？此動作無法復原！')) {
        if (confirm('再次確認：所有資料將被刪除')) {
            data = {
                holdings: [],
                transactions: [],
                loans: [],
                profile: {name: '', email: '', risk_level: '穩健型'},
                settings: {
                    target_allocation: {原型: 70, 槓桿: 15, 類現金: 15},
                    loan_interest_rate: 2.5,
                    loan_limit_percent: 20,
                    new_funds: 0
                }
            };
            saveData();
            alert('資料已清除');
            render();
        }
    }
}

function saveData() {
    fetch('/api/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(() => render());
}

function updatePrices() {
    let btn = document.getElementById('btn-refresh');
    btn.textContent = '🔄 更新中...';
    btn.disabled = true;
    
    fetch('/api/up', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data.holdings)
    })
    .then(r => r.json())
    .then(prices => {
        data.holdings.forEach(h => {
            if (prices[h.code]) {
                h.price = prices[h.code];
            }
        });
        saveData();
        btn.textContent = '🔄 更新股價';
        btn.disabled = false;
    })
    .catch(e => {
        alert('更新失敗');
        btn.textContent = '🔄 更新股價';
        btn.disabled = false;
    });
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, data=load_data())

@app.route('/api/save', methods=['POST'])
def save():
    save_data(request.json)
    return jsonify({'status': 'ok'})

@app.route('/api/backup', methods=['POST'])
def backup():
    d = load_data()
    import time
    os.makedirs(BACKUP_DIR, exist_ok=True)
    fn = f"{BACKUP_DIR}/portfolio_{time.strftime('%Y%m%d_%H%M%S')}.json"
    json.dump(d, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return send_file(fn, as_attachment=True, download_name='portfolio_backup.json')

@app.route('/api/up', methods=['POST'])
def up():
    holdings = request.json
    return jsonify({h.get('code'): get_price(h.get('code')) for h in holdings})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    return send_from_directory('static', filename)

@app.route('/manifest.json')
def manifest():
    from flask import jsonify
    import json
    return jsonify(json.load(open('static/manifest.json')))
