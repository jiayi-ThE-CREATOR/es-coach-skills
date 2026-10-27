// 就活サイトの会員限定ページを、専用のブラウザプロファイル（ログイン状態を保存）で読む。
// プロファイルはリポジトリの外：~/.config/shukatsu-skills/browser-profile（本人の決定で常設・2026-10-27）
//
//   node member_fetch.mjs login <site>                 画面付きの窓を開く。本人がログインして窓を閉じる
//   node member_fetch.mjs check <site>                 ログインが生きているか（exit 0=生きている / 3=要ログイン）
//   node member_fetch.mjs fetch <outdir> <url> [...]   本文テキストとリンクを JSON で保存（数秒間隔）
//
// ボット拒否のサイト（Glassdoor 等。Playwright 起動のブラウザは Cloudflare に弾かれる）は、
// 本物の Chrome を普通に起動し、デバッグポート経由で読む（自動化の印が付かないので通る。2026-10-27 実測）：
//   node member_fetch.mjs chrome-open [url]                  専用プロファイルで Chrome を開く（ログインが要るなら本人がこの窓で）
//   node member_fetch.mjs chrome-fetch <outdir> <url> [...]  開いている Chrome から本文を読む（Chrome は閉じない）
//
// パスワードはこのツールにも会話にも渡さない。本人が窓の中で入力する。
import { chromium } from 'playwright';
import fs from 'fs';

const PROFILE = process.env.SHUKATSU_BROWSER_PROFILE || `${process.env.HOME}/.config/shukatsu-skills/browser-profile`;
const SITES = {
  // probe：会員限定の本文があるページ。locked：未ログイン時に出る文言
  gaishishukatsu: { login: 'https://gaishishukatsu.com/login', probe: 'https://gaishishukatsu.com/selection_reports/36339', locked: /会員登録して|ログインして|続きを読む/ },
  onecareer: { login: 'https://id.onecareer.jp/users/sign_in', probe: 'https://www.onecareer.jp/experiences/companies/9/middle_categories/interview', locked: /まずは新規会員登録/ },
  syukatsukaigi: { login: 'https://syukatsu-kaigi.jp/login', probe: 'https://syukatsu-kaigi.jp/companies/70013/experiences', locked: /会員登録してコンテンツ/ },
  // サイトを足すときは、ログイン URL と未ログイン時の文言を実物で確かめてから（上の3件は 2026-10-27 に確認。locked はログイン後の check で再確認する）
};
const LOCKED_ANY = /会員登録して|ログインして続き|続きを読むには|会員限定|まずは新規会員登録|Sign in to see more/;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const CHROME_PROFILE = `${process.env.HOME}/.config/shukatsu-skills/chrome-profile`;
const CDP = 'http://127.0.0.1:9333';
const WAIT_MS = 3000;

const [cmd, ...args] = process.argv.slice(2);
const site = (name) => SITES[name] || (console.error(`unknown site: ${name}（${Object.keys(SITES).join(' / ')}）`), process.exit(2));
fs.mkdirSync(PROFILE, { recursive: true });

async function open(headless) {
  try {
    return await chromium.launchPersistentContext(PROFILE, { headless, viewport: { width: 1200, height: 860 } });
  } catch (e) {
    if (/ProcessSingleton|in use|lock/i.test(e.message)) { console.error('プロファイル使用中：ログイン用の窓が開いていれば閉じてから再実行'); process.exit(4); }
    throw e;
  }
}
async function read(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(2500);
  return page.evaluate(() => ({
    title: document.title,
    text: document.body.innerText,
    links: [...document.querySelectorAll('a[href]')].map((a) => [a.innerText.trim().replace(/\s+/g, ' ').slice(0, 120), a.href]),
  }));
}

if (cmd === 'login') {
  const ctx = await open(false);
  const page = ctx.pages()[0] || (await ctx.newPage());
  await page.goto(site(args[0]).login);
  console.log('窓の中でログインし、終わったら窓を閉じてください');
  await new Promise((r) => ctx.on('close', r));
  console.log('closed');
} else if (cmd === 'check') {
  const s = site(args[0]);
  const ctx = await open(true);
  const d = await read(await ctx.newPage(), s.probe);
  await ctx.close();
  const ok = !s.locked.test(d.text);
  console.log(ok ? `ok: ${args[0]} ログイン有効` : `要ログイン: ${args[0]}（node member_fetch.mjs login ${args[0]}）`);
  process.exit(ok ? 0 : 3);
} else if (cmd === 'fetch') {
  const [outdir, ...urls] = args;
  fs.mkdirSync(outdir, { recursive: true });
  const ctx = await open(true);
  const page = await ctx.newPage();
  for (const [i, url] of urls.entries()) {
    try {
      const d = await read(page, url);
      const name = url.replace(/^https?:\/\//, '').replace(/[^\w.-]+/g, '_').slice(0, 120);
      fs.writeFileSync(`${outdir}/${name}.json`, JSON.stringify({ url, ...d }, null, 1));
      console.log(`${i + 1}/${urls.length} ${LOCKED_ANY.test(d.text) ? 'LOCKED?' : 'ok'} ${d.text.length}字 ${url}`);
    } catch (e) {
      console.log(`${i + 1}/${urls.length} ERR ${url} ${e.message.slice(0, 80)}`);
    }
    await page.waitForTimeout(WAIT_MS);
  }
  await ctx.close();
} else if (cmd === 'chrome-open') {
  const { spawn } = await import('child_process');
  fs.mkdirSync(CHROME_PROFILE, { recursive: true });
  spawn(CHROME, ['--remote-debugging-port=9333', `--user-data-dir=${CHROME_PROFILE}`, '--no-first-run', '--no-default-browser-check', ...(args[0] ? [args[0]] : [])], { detached: true, stdio: 'ignore' }).unref();
  console.log('Chrome を開きました（デバッグポート 9333）。ログインが要るなら本人がこの窓で');
} else if (cmd === 'chrome-fetch') {
  const [outdir, ...urls] = args;
  fs.mkdirSync(outdir, { recursive: true });
  let b;
  try { b = await chromium.connectOverCDP(CDP); } catch { console.error('Chrome が開いていない：先に chrome-open'); process.exit(4); }
  const page = await b.contexts()[0].newPage();
  for (const [i, url] of urls.entries()) {
    try {
      const d = await read(page, url);
      const name = url.replace(/^https?:\/\//, '').replace(/[^\w.-]+/g, '_').slice(0, 120);
      fs.writeFileSync(`${outdir}/${name}.json`, JSON.stringify({ url, ...d }, null, 1));
      const blocked = /Humans only|Just a moment/.test(d.text);
      console.log(`${i + 1}/${urls.length} ${blocked ? 'BLOCKED' : LOCKED_ANY.test(d.text) ? 'LOCKED?' : 'ok'} ${d.text.length}字 ${url}`);
    } catch (e) {
      console.log(`${i + 1}/${urls.length} ERR ${url} ${e.message.slice(0, 80)}`);
    }
    await page.waitForTimeout(WAIT_MS + 2000);
  }
  await page.close();
  await b.close(); // CDP 接続を切るだけ。Chrome 本体は開いたまま
  process.exit(0);
} else {
  console.log('usage: login <site> | check <site> | fetch <outdir> <url...> | chrome-open [url] | chrome-fetch <outdir> <url...>');
  process.exit(2);
}
