#!/usr/bin/env node

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

const GITHUB_REPO = "Han-cy830/llm-arena";
const BRANCH = "master";
const SKILL_NAME = "llm-arena";

const COLORS = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
};

function log(msg) {
  console.log(msg);
}

function info(msg) {
  console.log(`${COLORS.cyan}${msg}${COLORS.reset}`);
}

function success(msg) {
  console.log(`${COLORS.green}${msg}${COLORS.reset}`);
}

function warn(msg) {
  console.log(`${COLORS.yellow}${msg}${COLORS.reset}`);
}

function error(msg) {
  console.error(`${COLORS.red}${msg}${COLORS.reset}`);
}

function banner() {
  log("");
  log(`${COLORS.bold}${COLORS.cyan}╔══════════════════════════════════════════════════╗${COLORS.reset}`);
  log(`${COLORS.bold}${COLORS.cyan}║       🏆 LLM Arena - Skill Installer           ║${COLORS.reset}`);
  log(`${COLORS.bold}${COLORS.cyan}╚══════════════════════════════════════════════════╝${COLORS.reset}`);
  log("");
}

function getClaudeSkillsDir() {
  const home = os.homedir();
  const platform = os.platform();

  if (platform === "win32") {
    return path.join(process.env.APPDATA || path.join(home, "AppData", "Roaming"), "claude", "skills");
  }
  return path.join(home, ".claude", "skills");
}

function getAgentsSkillsDir() {
  const home = os.homedir();
  return path.join(home, ".agents", "skills");
}

function run(cmd, opts = {}) {
  try {
    return execSync(cmd, { encoding: "utf-8", stdio: "pipe", ...opts });
  } catch (e) {
    return null;
  }
}

function checkGit() {
  return run("git --version") !== null;
}

function checkPython() {
  const py = run("python --version") || run("python3 --version");
  if (py && py.includes("3.")) {
    const match = py.match(/3\.(\d+)/);
    if (match && parseInt(match[1]) >= 10) return true;
  }
  return false;
}

function checkNode() {
  const v = run("node --version");
  if (v) {
    const match = v.match(/v(\d+)/);
    return match && parseInt(match[1]) >= 16;
  }
  return false;
}

function downloadSkill(targetDir) {
  const tmpDir = path.join(os.tmpdir(), `llm-arena-${Date.now()}`);

  info(`  正在从 GitHub 下载 ${GITHUB_REPO}...`);

  const cloneResult = run(
    `git clone --depth 1 --branch ${BRANCH} https://github.com/${GITHUB_REPO}.git "${tmpDir}"`,
    { stdio: "pipe" }
  );

  if (cloneResult === null) {
    error("  ❌ 下载失败，请检查网络连接");
    error("  尝试手动克隆: git clone https://github.com/Han-cy830/llm-arena.git");
    process.exit(1);
  }

  // Copy skill files
  const skillSrc = path.join(tmpDir, "skill");
  const srcDir = path.join(tmpDir, "src");
  const dataDir = path.join(tmpDir, "data");

  if (!fs.existsSync(skillSrc)) {
    error("  ❌ 仓库中未找到 skill/ 目录");
    process.exit(1);
  }

  // Create target structure
  fs.mkdirSync(path.join(targetDir, "skill"), { recursive: true });
  fs.mkdirSync(path.join(targetDir, "src"), { recursive: true });
  fs.mkdirSync(path.join(targetDir, "data"), { recursive: true });

  // Copy files
  copyDir(skillSrc, path.join(targetDir, "skill"));
  if (fs.existsSync(srcDir)) copyDir(srcDir, path.join(targetDir, "src"));
  if (fs.existsSync(dataDir)) copyDir(dataDir, path.join(targetDir, "data"));

  // Copy README and LICENSE
  for (const f of ["README.md", "LICENSE"]) {
    const src = path.join(tmpDir, f);
    if (fs.existsSync(src)) fs.copyFileSync(src, path.join(targetDir, f));
  }

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true, force: true });

  return true;
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function installSkill() {
  banner();

  // Pre-checks
  const hasGit = checkGit();
  const hasPython = checkPython();
  const hasNode = checkNode();

  log(`  ${hasGit ? "✅" : "❌"} Git`);
  log(`  ${hasPython ? "✅" : "⚠️"} Python 3.10+ ${hasPython ? "" : "(可选，用于 CLI)"}`);
  log(`  ${hasNode ? "✅" : "❌"} Node.js 16+`);
  log("");

  if (!hasGit) {
    error("  需要安装 Git: https://git-scm.com/downloads");
    process.exit(1);
  }

  if (!hasNode) {
    error("  需要安装 Node.js 16+: https://nodejs.org");
    process.exit(1);
  }

  // Determine install location
  const claudeDir = getClaudeSkillsDir();
  const agentsDir = getAgentsSkillsDir();
  const targetDir = path.join(agentsDir, SKILL_NAME);
  const claudeLink = path.join(claudeDir, SKILL_NAME);

  log(`  📁 安装目录: ${targetDir}`);
  log(`  📁 Claude Code 链接: ${claudeLink}`);
  log("");

  // Download
  if (fs.existsSync(targetDir)) {
    warn(`  ⚠️  目标目录已存在，将更新...`);
    fs.rmSync(targetDir, { recursive: true, force: true });
  }

  downloadSkill(targetDir);
  success("  ✅ Skill 文件下载完成");

  // Create Claude Code symlink/junction
  fs.mkdirSync(claudeDir, { recursive: true });
  if (fs.existsSync(claudeLink)) {
    fs.rmSync(claudeLink, { recursive: true, force: true });
  }

  try {
    // Windows needs junction for directories
    if (os.platform() === "win32") {
      fs.symlinkSync(targetDir, claudeLink, "junction");
    } else {
      fs.symlinkSync(targetDir, claudeLink);
    }
    success("  ✅ Claude Code skill 链接创建成功");
  } catch (e) {
    warn(`  ⚠️  创建链接失败: ${e.message}`);
    warn(`  请手动创建: mklink /J "${claudeLink}" "${targetDir}"`);
  }

  // Summary
  log("");
  log(`${COLORS.bold}${COLORS.green}  ════════════════════════════════════════════════${COLORS.reset}`);
  log(`${COLORS.bold}${COLORS.green}  ✅ LLM Arena Skill 安装成功!${COLORS.reset}`);
  log(`${COLORS.bold}${COLORS.green}  ════════════════════════════════════════════════${COLORS.reset}`);
  log("");
  log("  📦 已安装内容:");
  log(`     - ${SKILL_NAME} skill (Claude Code)`);
  log(`     - 50+ 供应商配置`);
  log(`     - 竞技场排名系统`);
  log(`     - API 智能路由器`);
  log("");

  if (!hasPython) {
    warn("  ⚠️  未检测到 Python 3.10+");
    warn("  CLI 工具需要 Python，请安装:");
    warn("    winget install Python.Python.3.12");
    log("");
  }

  log("  🚀 快速开始:");
  log(`     1. 在 Claude Code 中使用 /llm-arena 触发 skill`);
  log(`     2. 或手动运行 CLI:`);
  log(`        cd ${targetDir}`);
  log(`        python src/cli.py provider list`);
  log(`        python src/cli.py rank`);
  log("");
  log("  📖 文档: https://github.com/Han-cy830/llm-arena");
  log("");
}

function uninstallSkill() {
  banner();
  info("  正在卸载 LLM Arena Skill...");
  log("");

  const agentsDir = getAgentsSkillsDir();
  const targetDir = path.join(agentsDir, SKILL_NAME);
  const claudeDir = getClaudeSkillsDir();
  const claudeLink = path.join(claudeDir, SKILL_NAME);

  let removed = false;

  if (fs.existsSync(claudeLink)) {
    fs.rmSync(claudeLink, { recursive: true, force: true });
    success("  ✅ 已移除 Claude Code skill 链接");
    removed = true;
  }

  if (fs.existsSync(targetDir)) {
    fs.rmSync(targetDir, { recursive: true, force: true });
    success("  ✅ 已移除 skill 文件");
    removed = true;
  }

  if (!removed) {
    warn("  未找到已安装的 LLM Arena Skill");
  } else {
    log("");
    success("  ✅ 卸载完成");
  }
}

// Main
const args = process.argv.slice(2);
const cmd = args[0] || "install";

switch (cmd) {
  case "install":
    installSkill();
    break;
  case "uninstall":
  case "remove":
    uninstallSkill();
    break;
  case "--help":
  case "-h":
    banner();
    log("  用法: npx llm-arena [command]");
    log("");
    log("  命令:");
    log("    install    安装 skill (默认)");
    log("    uninstall  卸载 skill");
    log("    --help     显示帮助");
    log("");
    break;
  default:
    error(`  未知命令: ${cmd}`);
    log("  运行 npx llm-arena --help 查看帮助");
    process.exit(1);
}
