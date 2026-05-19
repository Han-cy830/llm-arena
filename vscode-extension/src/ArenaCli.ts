import { exec } from 'child_process';
import * as path from 'path';
import * as os from 'os';
import * as vscode from 'vscode';

export class ArenaCli {
    private cliPath: string;
    private pythonPath: string;
    private cwd: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('llmArena');
        this.pythonPath = config.get<string>('pythonPath', 'python');
        this.cwd = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();

        const configCliPath = config.get<string>('cliPath', '');
        if (configCliPath) {
            this.cliPath = configCliPath;
        } else {
            const workspaceCli = path.join(this.cwd, 'src', 'cli.py');
            const globalCli = path.join(os.homedir(), '.agents', 'skills', 'llm-arena', 'src', 'cli.py');
            this.cliPath = workspaceCli;
            // Fallback: store path for runtime check
            this._fallbackPaths = [workspaceCli, globalCli];
        }
    }

    private _fallbackPaths: string[] = [];

    private findCli(): string {
        if (this._fallbackPaths.length === 0) {
            return this.cliPath;
        }
        const fs = require('fs');
        for (const p of this._fallbackPaths) {
            if (fs.existsSync(p)) {
                return p;
            }
        }
        return this._fallbackPaths[0];
    }

    execute(...args: string[]): Promise<string> {
        return new Promise((resolve, reject) => {
            const cli = this.findCli();
            const cmd = `"${this.pythonPath}" "${cli}" ${args.join(' ')}`;
            exec(cmd, {
                cwd: this.cwd,
                timeout: 30000,
                maxBuffer: 10 * 1024 * 1024,
                env: { ...process.env, PYTHONUTF8: '1' },
            }, (error, stdout, stderr) => {
                if (error) {
                    reject(new Error(stderr || error.message));
                } else {
                    resolve(stdout);
                }
            });
        });
    }

    async executeJson(...args: string[]): Promise<any> {
        const raw = await this.execute(...args, '--json');
        return JSON.parse(raw);
    }

    async getRanking(period: string = 'all'): Promise<any[]> {
        return this.executeJson('rank', 'json', period);
    }

    async getProviders(): Promise<any[]> {
        return this.executeJson('provider', 'list');
    }

    async getActiveConfig(): Promise<any> {
        return this.executeJson('provider', 'active');
    }

    async switchProvider(providerId: string, modelId?: string): Promise<any> {
        const args = ['provider', 'switch', providerId];
        if (modelId) {
            args.push(modelId);
        }
        return this.executeJson(...args);
    }

    async showStatus(): Promise<string> {
        return this.execute('status');
    }

    async showModelDetail(modelId: string): Promise<string> {
        return this.execute('rank', 'detail', modelId);
    }

    async recordMatch(modelId: string, tokens: number, thinkTime: number, quality: number): Promise<string> {
        return this.execute('arena', 'record', modelId, String(tokens), String(thinkTime), String(quality));
    }
}
