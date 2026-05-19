import * as vscode from 'vscode';
import { ArenaCli } from './ArenaCli';
import { ModelTreeProvider } from './ModelTreeProvider';
import { RankingsPanel } from './RankingsPanel';

let cli: ArenaCli;

export function activate(context: vscode.ExtensionContext) {
    cli = new ArenaCli();

    // Tree view
    const treeProvider = new ModelTreeProvider(cli);
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('llmArena.models', treeProvider)
    );

    // Commands
    context.subscriptions.push(
        vscode.commands.registerCommand('llmArena.showRankings', () => {
            RankingsPanel.createOrShow(context.extensionUri, cli);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('llmArena.showStatus', async () => {
            try {
                const output = await cli.showStatus();
                const doc = await vscode.workspace.openTextDocument({
                    content: output,
                    language: 'plaintext',
                });
                vscode.window.showTextDocument(doc, { preview: false });
            } catch (e: any) {
                vscode.window.showErrorMessage(`LLM Arena: ${e.message}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('llmArena.showModelDetail', async (modelId?: string) => {
            if (!modelId) {
                modelId = await vscode.window.showInputBox({
                    prompt: 'Model ID',
                    placeHolder: 'e.g., gpt-4o, claude-sonnet',
                });
            }
            if (!modelId) return;
            try {
                const output = await cli.showModelDetail(modelId);
                const doc = await vscode.workspace.openTextDocument({
                    content: output,
                    language: 'plaintext',
                });
                vscode.window.showTextDocument(doc, { preview: false });
            } catch (e: any) {
                vscode.window.showErrorMessage(`LLM Arena: ${e.message}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('llmArena.recordMatch', async () => {
            const modelId = await vscode.window.showInputBox({
                prompt: 'Model ID',
                placeHolder: 'e.g., gpt-4o',
            });
            if (!modelId) return;

            const tokens = await vscode.window.showInputBox({
                prompt: 'Token count',
                validateInput: v => isNaN(Number(v)) ? 'Must be a number' : null,
            });
            if (!tokens) return;

            const time = await vscode.window.showInputBox({
                prompt: 'Think time (seconds)',
                validateInput: v => isNaN(Number(v)) ? 'Must be a number' : null,
            });
            if (!time) return;

            const quality = await vscode.window.showInputBox({
                prompt: 'Quality (0-10)',
                validateInput: v => {
                    const n = Number(v);
                    return isNaN(n) || n < 0 || n > 10 ? 'Must be 0-10' : null;
                },
            });
            if (!quality) return;

            try {
                const output = await cli.recordMatch(modelId, Number(tokens), Number(time), Number(quality));
                vscode.window.showInformationMessage(output.trim());
                treeProvider.refresh();
            } catch (e: any) {
                vscode.window.showErrorMessage(`LLM Arena: ${e.message}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('llmArena.refreshTree', () => {
            treeProvider.refresh();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('llmArena.switchProvider', async () => {
            try {
                const providers = await cli.getProviders();
                const items = providers
                    .filter((p: any) => p.has_key)
                    .map((p: any) => ({
                        label: p.name || p.id,
                        description: p.active ? '(current)' : '',
                        id: p.id,
                    }));
                const selected = await vscode.window.showQuickPick(items, {
                    placeHolder: 'Select a provider',
                });
                if (selected) {
                    const result = await cli.switchProvider(selected.id);
                    vscode.window.showInformationMessage(`Switched to: ${result.provider || selected.label}`);
                    treeProvider.refresh();
                }
            } catch (e: any) {
                vscode.window.showErrorMessage(`LLM Arena: ${e.message}`);
            }
        })
    );

    // Status bar
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(symbol-enum) LLM Arena';
    statusBar.tooltip = 'LLM Arena - Click to show rankings';
    statusBar.command = 'llmArena.showRankings';
    statusBar.show();
    context.subscriptions.push(statusBar);
}

export function deactivate() {}
