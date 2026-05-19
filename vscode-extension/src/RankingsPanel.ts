import * as vscode from 'vscode';
import { ArenaCli } from './ArenaCli';

export class RankingsPanel {
    static current: RankingsPanel | undefined;
    private panel: vscode.WebviewPanel;
    private cli: ArenaCli;
    private disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, cli: ArenaCli) {
        this.panel = panel;
        this.cli = cli;
        this.panel.webview.html = this.getHtml();
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
        this.panel.webview.onDidReceiveMessage(
            this.handleMessage.bind(this), null, this.disposables
        );
    }

    static createOrShow(extensionUri: vscode.Uri, cli: ArenaCli) {
        if (RankingsPanel.current) {
            RankingsPanel.current.panel.reveal();
            return;
        }
        const panel = vscode.window.createWebviewPanel(
            'llmArena', 'LLM Arena Rankings',
            vscode.ViewColumn.One,
            { enableScripts: true, retainContextWhenHidden: true }
        );
        RankingsPanel.current = new RankingsPanel(panel, cli);
    }

    private async handleMessage(msg: any) {
        if (msg.command === 'refresh') {
            try {
                const data = await this.cli.getRanking(msg.period || 'all');
                this.panel.webview.postMessage({ type: 'data', data });
            } catch (e: any) {
                this.panel.webview.postMessage({ type: 'error', message: e.message });
            }
        }
    }

    private getHtml(): string {
        return `<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM Arena Rankings</title>
<style>
  body {
    font-family: var(--vscode-font-family);
    color: var(--vscode-foreground);
    background: var(--vscode-editor-background);
    padding: 16px;
    font-size: var(--vscode-font-size);
  }
  h2 { margin: 0 0 16px 0; font-weight: 600; }
  table { border-collapse: collapse; width: 100%; margin-top: 12px; }
  th, td { padding: 6px 10px; border: 1px solid var(--vscode-panel-border); text-align: left; }
  th { background: var(--vscode-editor-inactiveSelectionBackground); font-weight: 600; position: sticky; top: 0; }
  tr:hover { background: var(--vscode-list-hoverBackground); }
  .controls { margin-bottom: 12px; display: flex; gap: 8px; align-items: center; }
  button {
    background: var(--vscode-button-background);
    color: var(--vscode-button-foreground);
    border: none; padding: 4px 12px; cursor: pointer;
  }
  button:hover { background: var(--vscode-button-hoverBackground); }
  select {
    background: var(--vscode-input-background);
    color: var(--vscode-input-foreground);
    border: 1px solid var(--vscode-input-border);
    padding: 4px 8px;
  }
  .rank-1 { color: #ffd700; font-weight: bold; }
  .rank-2 { color: #c0c0c0; font-weight: bold; }
  .rank-3 { color: #cd7f32; font-weight: bold; }
  .streak-win { color: var(--vscode-testing-passed-foreground); }
  .streak-loss { color: var(--vscode-testing-failed-foreground); }
  .bar { display: inline-block; height: 10px; background: var(--vscode-progressBar-background); border-radius: 2px; }
</style>
</head><body>
<h2>LLM Arena Rankings</h2>
<div class="controls">
  <select id="period">
    <option value="daily">Daily</option>
    <option value="weekly">Weekly</option>
    <option value="monthly">Monthly</option>
    <option value="all" selected>All Time</option>
  </select>
  <button id="refresh">Refresh</button>
</div>
<div id="content">Loading...</div>
<script>
  const vscode = acquireVsCodeApi();
  const el = id => document.getElementById(id);
  el('refresh').onclick = () => refresh();
  el('period').onchange = () => refresh();
  function refresh() {
    vscode.postMessage({ command: 'refresh', period: el('period').value });
  }
  window.addEventListener('message', e => {
    const msg = e.data;
    if (msg.type === 'data') render(msg.data);
    if (msg.type === 'error') el('content').textContent = 'Error: ' + msg.message;
  });
  function render(data) {
    if (!data || !data.length) { el('content').textContent = 'No data yet. Register models and record matches to begin.'; return; }
    const maxElo = Math.max(...data.map(r => r.elo || 1200));
    let html = '<table><tr><th>#</th><th>Mood</th><th>Model</th><th>Elo</th><th>Score</th><th>Quality</th><th>W-L</th><th>Trend</th></tr>';
    data.forEach((r, i) => {
      const rank = i + 1;
      const cls = rank <= 3 ? ' class="rank-' + rank + '"' : '';
      const medal = rank === 1 ? '\\u{1F947}' : rank === 2 ? '\\u{1F948}' : rank === 3 ? '\\u{1F949}' : rank;
      const mood = (r.mood && r.mood.emoji) || '\\u{1F610}';
      const elo = Math.round(r.elo || 0);
      const barW = Math.round((elo / maxElo) * 80);
      const bar = '<span class="bar" style="width:' + barW + 'px"></span>';
      const eff = (r.efficiency_score || 0).toFixed(3);
      const q = (r.avg_quality || 0).toFixed(1);
      const wl = (r.wins || 0) + '-' + (r.losses || 0);
      const streak = r.current_streak > 2
        ? '<span class="' + (r.streak_type === 'win' ? 'streak-win' : 'streak-loss') + '">' + (r.streak_type === 'win' ? '\\u{1F525}' : '\\u{1F494}') + r.current_streak + '</span>'
        : '';
      const trend = r.trend === 'up' ? '\\u{2B06}' : r.trend === 'down' ? '\\u{2B07}' : '\\u{27A1}';
      html += '<tr><td' + cls + '>' + medal + '</td><td>' + mood + '</td><td>' + (r.display_name || r.model_id) + '</td><td>' + elo + ' ' + bar + '</td><td>' + eff + '</td><td>' + q + '</td><td>' + wl + ' ' + streak + '</td><td>' + trend + '</td></tr>';
    });
    html += '</table>';
    el('content').innerHTML = html;
  }
  refresh();
</script>
</body></html>`;
    }

    dispose() {
        RankingsPanel.current = undefined;
        this.panel.dispose();
        this.disposables.forEach(d => d.dispose());
    }
}
