import * as vscode from 'vscode';
import { ArenaCli } from './ArenaCli';

export class ModelTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly modelId: string,
        description: string,
        rank: number,
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.contextValue = 'model';
        this.tooltip = `${this.label} - ${description}`;

        const medals = ['🥇', '🥈', '🥉'];
        if (rank >= 1 && rank <= 3) {
            this.iconPath = new vscode.ThemeIcon(
                rank === 1 ? 'star-full' : rank === 2 ? 'star-half' : 'star-empty'
            );
            this.label = `${medals[rank - 1]} ${this.label}`;
        } else {
            this.iconPath = new vscode.ThemeIcon('symbol-misc');
        }

        this.command = {
            command: 'llmArena.showModelDetail',
            title: 'Show Details',
            arguments: [this.modelId],
        };
    }
}

export class ModelTreeProvider implements vscode.TreeDataProvider<ModelTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ModelTreeItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(private cli: ArenaCli) {}

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: ModelTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(): Promise<ModelTreeItem[]> {
        try {
            const ranking = await this.cli.getRanking('all');
            return ranking.map((r: any, i: number) => {
                const rank = i + 1;
                const mood = r.mood?.emoji || '😐';
                const elo = Math.round(r.elo || 0);
                const eff = (r.efficiency_score || 0).toFixed(2);
                const streak = r.current_streak > 2
                    ? (r.streak_type === 'win' ? ` 🔥${r.current_streak}` : ` 💔${r.current_streak}`)
                    : '';
                return new ModelTreeItem(
                    `${mood} ${r.display_name || r.model_id}`,
                    r.model_id,
                    `Elo:${elo} Eff:${eff}${streak}`,
                    rank,
                );
            });
        } catch (e: any) {
            vscode.window.showErrorMessage(`LLM Arena: ${e.message}`);
            return [];
        }
    }
}
