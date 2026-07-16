#!/usr/bin/env node
const assert = require('assert');
const crypto = require('crypto');
const childProcess = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { publishBundle } = require('./delivery-transaction.js');

const FAULTS = [
  'after_candidate_validation',
  'after_history_reservation',
  'after_archive_snapshot',
  'after_publish_file_1',
  'after_publish_middle_file',
  'before_post_publish_verify',
  'before_work_cleanup',
];

function model(prefix) {
  const modulePdfs = [
    { module_id: 'teaching-plan', public_pdf_suffix: '授课进度计划表', public_pdf_filename: `${prefix}授课进度计划表.pdf` },
    { module_id: 'teaching-design', public_pdf_suffix: '教学设计方案', public_pdf_filename: `${prefix}教学设计方案.pdf` },
  ];
  return {
    modules: { items: modulePdfs },
    public_delivery: {
      filename_prefix: prefix,
      public_markdown_filename: `${prefix}教学资料.md`,
      public_package_pdf_filename: `${prefix}教学资料.pdf`,
      module_pdfs: modulePdfs,
      expected_public_filenames: [
        `${prefix}教学资料.md`,
        `${prefix}教学资料.pdf`,
        ...modulePdfs.map((item) => item.public_pdf_filename),
      ],
    },
  };
}

function bytesFor(name, version) {
  if (name.endsWith('.md')) return Buffer.from(`# ${version}\n${name}\n`, 'utf8');
  return Buffer.from(`%PDF-1.4\n${version}:${name}\n%%EOF\n`, 'utf8');
}

function makeCandidate(root, runId, packageModel, version) {
  const candidateRoot = path.join(root, '.work', runId, 'candidate');
  fs.mkdirSync(candidateRoot, { recursive: true });
  for (const name of packageModel.public_delivery.expected_public_filenames) {
    fs.writeFileSync(path.join(candidateRoot, name), bytesFor(name, version));
  }
  return candidateRoot;
}

function snapshot(root, ignored = new Set(['.work'])) {
  const result = {};
  if (!fs.existsSync(root)) return result;
  const walk = (directory, relative = '') => {
    for (const entry of fs.readdirSync(directory).sort()) {
      if (!relative && ignored.has(entry)) continue;
      const absolute = path.join(directory, entry);
      const name = relative ? `${relative}/${entry}` : entry;
      const stat = fs.lstatSync(absolute);
      if (stat.isSymbolicLink()) result[name] = `symlink:${fs.readlinkSync(absolute)}`;
      else if (stat.isDirectory()) walk(absolute, name);
      else result[name] = crypto.createHash('sha256').update(fs.readFileSync(absolute)).digest('hex');
    }
  };
  walk(root);
  return result;
}

function publish(root, runId, packageModel, version, options = {}) {
  const candidateRoot = makeCandidate(root, runId, packageModel, version);
  return publishBundle({ root, runId, candidateRoot, packageModel, ...options });
}

function withRoot(callback) {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'tdpkg-delivery-'));
  const root = path.join(base, 'delivery');
  fs.mkdirSync(root);
  try {
    callback(root, base);
  } finally {
    fs.rmSync(base, { recursive: true, force: true });
  }
}

function testFirstSameChangeAndGap() {
  withRoot((root) => {
    const firstModel = model('工业机器人');
    assert.strictEqual(publish(root, 'first', firstModel, 'v1').status, 'published');
    const firstSnapshot = snapshot(root);
    const inodeBefore = fs.statSync(path.join(root, firstModel.public_delivery.public_markdown_filename)).ino;
    assert.strictEqual(publish(root, 'same', firstModel, 'v1').status, 'identical');
    assert.deepStrictEqual(snapshot(root), firstSnapshot);
    assert.strictEqual(fs.statSync(path.join(root, firstModel.public_delivery.public_markdown_filename)).ino, inodeBefore);

    fs.mkdirSync(path.join(root, 'history', '001'), { recursive: true });
    fs.writeFileSync(path.join(root, 'history', '001', 'sentinel'), 'one');
    fs.mkdirSync(path.join(root, 'history', '003'), { recursive: true });
    fs.writeFileSync(path.join(root, 'history', '003', 'sentinel'), 'three');
    const historyBefore = snapshot(path.join(root, 'history'));
    const changedModel = model('智能制造');
    const result = publish(root, 'changed', changedModel, 'v2');
    assert.strictEqual(result.status, 'published');
    assert.strictEqual(result.historySequence, '004');
    for (const name of firstModel.public_delivery.expected_public_filenames) {
      assert.deepStrictEqual(fs.readFileSync(path.join(root, 'history', '004', name)), bytesFor(name, 'v1'));
      assert.strictEqual(fs.existsSync(path.join(root, name)), false);
    }
    for (const name of changedModel.public_delivery.expected_public_filenames) {
      assert.deepStrictEqual(fs.readFileSync(path.join(root, name)), bytesFor(name, 'v2'));
    }
    assert.strictEqual(snapshot(path.join(root, 'history'))['001/sentinel'], historyBefore['001/sentinel']);
    assert.strictEqual(snapshot(path.join(root, 'history'))['003/sentinel'], historyBefore['003/sentinel']);
  });
}

function testFaultRollbackMatrix() {
  for (const fault of FAULTS) {
    withRoot((root) => {
      const oldModel = model('旧课程');
      publish(root, 'seed', oldModel, 'old');
      fs.mkdirSync(path.join(root, 'sources'));
      fs.writeFileSync(path.join(root, 'sources', 'user.txt'), 'source');
      fs.mkdirSync(path.join(root, 'history', '001'), { recursive: true });
      fs.writeFileSync(path.join(root, 'history', '001', 'sentinel'), 'history');
      const before = snapshot(root);
      assert.throws(
        () => publish(root, `fault-${fault}`, model('新课程'), 'new', { fault }),
        new RegExp(fault),
      );
      assert.deepStrictEqual(snapshot(root), before, fault);
      assert.strictEqual(fs.existsSync(path.join(root, '.work', `fault-${fault}`)), false);
    });
  }
}

function testUnknownAmbiguousPartialSymlinkAndTraversal() {
  const cases = [
    ['unknown', (root) => fs.writeFileSync(path.join(root, 'notes.txt'), 'user')],
    ['hidden', (root) => fs.mkdirSync(path.join(root, '.teaching-design-package'))],
    ['media', (root) => fs.mkdirSync(path.join(root, 'media'))],
    ['symlink', (root, base) => fs.symlinkSync(path.join(base, 'outside'), path.join(root, 'mystery'))],
    ['partial', (root) => fs.writeFileSync(path.join(root, '残缺课程教学资料.md'), '# partial')],
    ['multiple', (root) => {
      for (const prefix of ['甲课程', '乙课程']) {
        for (const name of model(prefix).public_delivery.expected_public_filenames) {
          fs.writeFileSync(path.join(root, name), bytesFor(name, prefix));
        }
      }
    }],
  ];
  for (const [label, prepare] of cases) {
    withRoot((root, base) => {
      fs.writeFileSync(path.join(base, 'outside'), 'outside');
      prepare(root, base);
      const before = snapshot(root);
      assert.throws(() => publish(root, `reject-${label}`, model('候选课程'), 'new'), /fail.closed|ambiguous|unknown|partial|symlink/i);
      assert.deepStrictEqual(snapshot(root), before, label);
    });
  }
  withRoot((root) => {
    const unsafe = model('安全课程');
    unsafe.public_delivery.expected_public_filenames[0] = '../escape.md';
    assert.throws(() => publish(root, 'traversal', unsafe, 'new'), /relative|component|traversal/i);
  });
}

function testLockAndUnrelatedWorkPreserved() {
  withRoot((root) => {
    fs.mkdirSync(path.join(root, '.work', '.delivery-lock'), { recursive: true });
    fs.mkdirSync(path.join(root, '.work', 'stale-run'), { recursive: true });
    fs.writeFileSync(path.join(root, '.work', 'stale-run', 'evidence.txt'), 'keep');
    const before = snapshot(path.join(root, '.work'), new Set());
    assert.throws(() => publish(root, 'locked', model('课程'), 'new'), /lock/i);
    const after = snapshot(path.join(root, '.work'), new Set());
    assert.strictEqual(after['stale-run/evidence.txt'], before['stale-run/evidence.txt']);
  });
}

function testHandledSignalsRestoreCurrent() {
  for (const signal of ['SIGINT', 'SIGTERM']) {
    withRoot((root) => {
      const oldModel = model('信号旧课程');
      publish(root, `seed-${signal}`, oldModel, 'old');
      const before = snapshot(root);
      const nextModel = model('信号新课程');
      const runId = `signal-${signal.toLowerCase()}`;
      const candidateRoot = makeCandidate(root, runId, nextModel, 'new');
      const modelPath = path.join(root, '.work', runId, 'evidence-model.json');
      fs.writeFileSync(modelPath, JSON.stringify(nextModel));
      const result = childProcess.spawnSync(
        process.execPath,
        [require.resolve('./delivery-transaction.js'), 'publish', root, runId, candidateRoot, modelPath],
        {
          encoding: 'utf8',
          env: {
            ...process.env,
            TDPKG_DELIVERY_SELF_SIGNAL_AT: 'after_publish_file_1',
            TDPKG_DELIVERY_SELF_SIGNAL: signal,
          },
        },
      );
      assert.notStrictEqual(result.status, 0, signal);
      assert.deepStrictEqual(snapshot(root), before, signal);
      assert.strictEqual(fs.existsSync(path.join(root, '.work', runId)), false);
    });
  }
}

function testMutationGuards() {
  const source = fs.readFileSync(require.resolve('./delivery-transaction.js'), 'utf8');
  assert.match(source, /expected_public_filenames/);
  assert.match(source, /pathSetEqual/);
  assert.match(source, /nextHistorySequence/);
  assert.doesNotMatch(source, /Markdown-only|current group\s*=\s*\[/i);
  assert.doesNotMatch(source, /find\s+-delete|rmSync\(root\s*,\s*\{\s*recursive:\s*true/);
}

function testRealRenderPackageCandidateIsolation() {
  withRoot((root, base) => {
    const bin = path.join(base, 'bin');
    fs.mkdirSync(bin);
    const typst = path.join(bin, 'typst');
    fs.writeFileSync(typst, `#!/usr/bin/env bash\nset -euo pipefail\ninput="$2"\noutput="$3"\nprintf '%%PDF-1.4\\n' >"$output"\nshasum -a 256 "$input" >>"$output"\nprintf '%%%%EOF\\n' >>"$output"\n`);
    fs.chmodSync(typst, 0o755);
    const pdfunite = path.join(bin, 'pdfunite');
    fs.writeFileSync(pdfunite, `#!/usr/bin/env bash\nset -euo pipefail\noutput="${'${!#}'}"\nprintf '%%PDF-1.4\\nmerged\\n%%%%EOF\\n' >"$output"\n`);
    fs.chmodSync(pdfunite, 0o755);
    const input = path.join(base, 'package.md');
    fs.copyFileSync(path.join(__dirname, '..', 'templates', 'teaching-design-package-full.md'), input);
    const cli = path.join(__dirname, 'teaching-design-package.sh');
    const env = { ...process.env, PATH: `${bin}:${process.env.PATH}` };
    const run = (extraEnv = {}) => childProcess.spawnSync('bash', [cli, 'render-package', '--pdf', '--input', input, '--out-dir', root], {
      encoding: 'utf8', env: { ...env, ...extraEnv },
    });
    const first = run();
    assert.strictEqual(first.status, 0, first.stderr);
    assert.strictEqual(fs.existsSync(path.join(root, '.teaching-design-package')), false);
    assert.strictEqual(fs.existsSync(path.join(root, '.work')), false);
    const before = snapshot(root);
    fs.appendFileSync(input, '\n<!-- candidate change -->\n');
    for (const failureEnv of [
      { TDPKG_FORCE_MODULE_PDF_MISSING: 'teaching-plan' },
      { TDPKG_FORCE_MODULE_PDF_EMPTY: 'teaching-design' },
      { TDPKG_FORCE_MERGE_FAILURE: 'failed' },
    ]) {
      const failed = run(failureEnv);
      assert.notStrictEqual(failed.status, 0);
      assert.deepStrictEqual(snapshot(root), before);
      assert.strictEqual(fs.existsSync(path.join(root, '.teaching-design-package')), false);
      assert.strictEqual(fs.existsSync(path.join(root, '.work')), false);
    }
  });
}

const tests = [
  testFirstSameChangeAndGap,
  testFaultRollbackMatrix,
  testUnknownAmbiguousPartialSymlinkAndTraversal,
  testLockAndUnrelatedWorkPreserved,
  testHandledSignalsRestoreCurrent,
  testMutationGuards,
  testRealRenderPackageCandidateIsolation,
];

let passed = 0;
for (const test of tests) {
  test();
  passed += 1;
  process.stdout.write(`PASS ${test.name}\n`);
}
process.stdout.write(`PASS ${passed}/${tests.length} delivery transaction groups; faults=${FAULTS.length}\n`);
