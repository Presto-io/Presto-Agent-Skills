#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');

const SAFE_FS_HELPER = path.join(__dirname, 'delivery-safe-fs.py');

const SUPPORT_DIRECTORIES = new Set(['sources', 'assets', 'history', '.work']);
const HISTORY_NAME = /^[0-9]{3,}$/;
const SAFE_COMPONENT = /^[^/\\\u0000-\u001f\u007f]+$/u;

class DeliveryError extends Error {
  constructor(code, message) {
    super(`${code}: ${message}`);
    this.name = 'DeliveryError';
    this.code = code;
  }
}

function fail(code, message) {
  throw new DeliveryError(code, message);
}

function validateComponent(value, label) {
  if (typeof value !== 'string' || !value || value === '.' || value === '..' || !SAFE_COMPONENT.test(value) || value.includes('..')) {
    fail('unsafe_relative_component', `${label} is not a safe relative component: ${String(value)}`);
  }
  return value;
}

function validateExpectedNames(packageModel) {
  const delivery = packageModel && packageModel.public_delivery;
  const names = delivery && delivery.expected_public_filenames;
  if (!Array.isArray(names) || names.length < 3) fail('invalid_expected_public_filenames', 'model must provide a dynamic 1+1+N expected_public_filenames array');
  const validated = names.map((name, index) => validateComponent(name, `expected_public_filenames[${index}]`));
  if (new Set(validated).size !== validated.length) fail('invalid_expected_public_filenames', 'expected_public_filenames contains duplicates');
  if (!validated.includes(delivery.public_markdown_filename) || !validated.includes(delivery.public_package_pdf_filename)) {
    fail('invalid_expected_public_filenames', 'expected_public_filenames must contain the model Markdown and merged PDF');
  }
  const moduleNames = (delivery.module_pdfs || []).map((item) => item.public_pdf_filename);
  if (moduleNames.length < 1 || moduleNames.some((name) => !validated.includes(name))) {
    fail('invalid_expected_public_filenames', 'expected_public_filenames must contain every registry-derived module PDF');
  }
  return validated;
}

function assertRuntimeCapabilities() {
  if (typeof fs.constants.O_NOFOLLOW !== 'number' || typeof fs.constants.O_DIRECTORY !== 'number') {
    fail('runtime_capability_error', 'Node runtime lacks O_NOFOLLOW or O_DIRECTORY');
  }
  if (typeof fs.renameSync !== 'function' || typeof fs.fsyncSync !== 'function' || typeof fs.lstatSync !== 'function') {
    fail('runtime_capability_error', 'Node runtime lacks required no-follow inspection, replace, or fsync primitives');
  }
}

function lstatRequired(target, label) {
  let stat;
  try {
    stat = fs.lstatSync(target);
  } catch (error) {
    fail('path_identity_error', `${label} is unavailable: ${error.message}`);
  }
  if (stat.isSymbolicLink()) fail('symlink_fail_closed', `${label} must not be a symlink`);
  return stat;
}

function assertDirectory(target, label) {
  const stat = lstatRequired(target, label);
  if (!stat.isDirectory()) fail('path_type_error', `${label} must be a directory`);
  return stat;
}

function assertRegular(target, label, nonempty = true) {
  const stat = lstatRequired(target, label);
  if (!stat.isFile()) fail('path_type_error', `${label} must be a regular file`);
  if (nonempty && stat.size <= 0) fail('empty_candidate_artifact', `${label} must be non-empty`);
  return stat;
}

function openHeldDirectory(target, label) {
  const before = assertDirectory(target, label);
  let descriptor;
  try {
    descriptor = fs.openSync(target, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
  } catch (error) {
    fail('runtime_capability_error', `cannot hold ${label} without following links: ${error.message}`);
  }
  const held = fs.fstatSync(descriptor);
  if (held.dev !== before.dev || held.ino !== before.ino) {
    fs.closeSync(descriptor);
    fail('path_identity_error', `${label} changed while it was opened`);
  }
  return { descriptor, dev: held.dev, ino: held.ino, target, label };
}

function assertHeldDirectory(held) {
  const current = assertDirectory(held.target, held.label);
  const descriptorStat = fs.fstatSync(held.descriptor);
  if (current.dev !== held.dev || current.ino !== held.ino || descriptorStat.dev !== held.dev || descriptorStat.ino !== held.ino) {
    fail('path_identity_error', `${held.label} identity changed during publication`);
  }
}

function fsyncFile(target) {
  const descriptor = fs.openSync(target, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
  try {
    fs.fsyncSync(descriptor);
  } finally {
    fs.closeSync(descriptor);
  }
}

function fsyncDirectory(target) {
  const descriptor = fs.openSync(target, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
  try {
    fs.fsyncSync(descriptor);
  } finally {
    fs.closeSync(descriptor);
  }
}

function copyRegular(source, destination) {
  assertRegular(source, `copy source ${source}`);
  fs.copyFileSync(source, destination, fs.constants.COPYFILE_EXCL);
  assertRegular(destination, `copy destination ${destination}`);
  fsyncFile(destination);
  if (!filesEqual(source, destination)) fail('copy_verification_failed', `copy bytes differ: ${destination}`);
}

function filesEqual(left, right) {
  const leftStat = assertRegular(left, `comparison source ${left}`);
  const rightStat = assertRegular(right, `comparison source ${right}`);
  if (leftStat.size !== rightStat.size) return false;
  const leftDescriptor = fs.openSync(left, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
  const rightDescriptor = fs.openSync(right, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
  try {
    const blockSize = 64 * 1024;
    const leftBuffer = Buffer.allocUnsafe(blockSize);
    const rightBuffer = Buffer.allocUnsafe(blockSize);
    let position = 0;
    while (position < leftStat.size) {
      const length = Math.min(blockSize, leftStat.size - position);
      const leftRead = fs.readSync(leftDescriptor, leftBuffer, 0, length, position);
      const rightRead = fs.readSync(rightDescriptor, rightBuffer, 0, length, position);
      if (leftRead !== rightRead || !leftBuffer.subarray(0, leftRead).equals(rightBuffer.subarray(0, rightRead))) return false;
      position += leftRead;
    }
    return true;
  } finally {
    fs.closeSync(leftDescriptor);
    fs.closeSync(rightDescriptor);
  }
}

function pathSetEqual(left, right) {
  if (left.length !== right.length) return false;
  const sortedLeft = [...left].sort();
  const sortedRight = [...right].sort();
  return sortedLeft.every((name, index) => name === sortedRight[index]);
}

function validateCandidate(candidateRoot, expectedNames) {
  assertDirectory(candidateRoot, 'candidate root');
  const entries = fs.readdirSync(candidateRoot).sort();
  if (!pathSetEqual(entries, expectedNames)) fail('candidate_path_set_mismatch', 'candidate root must contain exactly expected_public_filenames');
  for (const name of expectedNames) {
    const target = path.join(candidateRoot, name);
    assertRegular(target, `candidate ${name}`);
    if (name.endsWith('.md')) fs.readFileSync(target, 'utf8');
    if (name.endsWith('.pdf')) {
      const descriptor = fs.openSync(target, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
      const header = Buffer.alloc(5);
      try {
        fs.readSync(descriptor, header, 0, 5, 0);
      } finally {
        fs.closeSync(descriptor);
      }
      if (header.toString('ascii') !== '%PDF-') fail('invalid_pdf_candidate', `${name} lacks a PDF header`);
    }
  }
}

function discoverySuffixes(packageModel) {
  const delivery = packageModel.public_delivery;
  const prefix = validateComponent(delivery.filename_prefix, 'filename prefix');
  const suffixes = validateExpectedNames(packageModel).map((name) => {
    if (!name.startsWith(prefix) || name.length === prefix.length) {
      fail('invalid_expected_public_filenames', `model filename does not start with filename_prefix: ${name}`);
    }
    return name.slice(prefix.length);
  });
  for (const suffix of suffixes) {
    if (suffixes.some((other) => other !== suffix && (suffix.endsWith(other) || other.endsWith(suffix)))) {
      fail('invalid_expected_public_filenames', `registry suffixes overlap: ${suffix}`);
    }
  }
  return suffixes;
}

function discoverCurrent(root, packageModel, ownRunId) {
  const suffixes = discoverySuffixes(packageModel);
  const delivery = packageModel.public_delivery;
  const modelPrefix = delivery.filename_prefix;
  const markdownSuffix = delivery.public_markdown_filename.slice(modelPrefix.length);
  const packageSuffix = delivery.public_package_pdf_filename.slice(modelPrefix.length);
  const publicFiles = [];
  for (const entry of fs.readdirSync(root).sort()) {
    const target = path.join(root, entry);
    const stat = fs.lstatSync(target);
    if (stat.isSymbolicLink()) fail('symlink_fail_closed', `root entry must not be a symlink: ${entry}`);
    if (SUPPORT_DIRECTORIES.has(entry)) {
      if (!stat.isDirectory()) fail('path_type_error', `support entry must be a directory: ${entry}`);
      if (entry === '.work') inspectWorkDirectory(target, ownRunId);
      if (entry === 'history') inspectHistoryDirectory(target);
      continue;
    }
    if (!stat.isFile()) fail('unknown_entry_fail_closed', `unknown non-file root entry: ${entry}`);
    publicFiles.push(entry);
  }
  if (!publicFiles.length) return [];
  const markdownNames = publicFiles.filter((name) => name.endsWith(markdownSuffix));
  if (markdownNames.length !== 1) fail('ambiguous_current_group', 'current must contain exactly one package Markdown anchor');
  const prefix = markdownNames[0].slice(0, -markdownSuffix.length);
  if (!prefix) fail('partial_group_fail_closed', 'public filename lacks a course prefix');
  const names = publicFiles.filter((name) => name.startsWith(prefix));
  if (names.length !== publicFiles.length) fail('ambiguous_current_group', 'multiple course-prefix groups found');
  const packageName = `${prefix}${packageSuffix}`;
  const moduleNames = names.filter((name) => name !== markdownNames[0] && name !== packageName);
  if (!names.includes(packageName) || moduleNames.length < 1 || moduleNames.some((name) => !name.endsWith('.pdf'))) {
    fail('partial_group_fail_closed', `current group for ${prefix} is incomplete`);
  }
  for (const name of names) assertRegular(path.join(root, name), `current ${name}`);
  return names.sort();
}

function safeFs(command, root, runId, name = '') {
  const args = [SAFE_FS_HELPER, command, root, runId];
  if (name) args.push(name);
  try {
    childProcess.execFileSync('python3', args, { stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (error) {
    fail('safe_fs_error', `${command} failed: ${(error.stderr || error.message).toString().trim()}`);
  }
}

function safeFsHeld(command, rootHeld, workHeld, runId, args = [], historyHeld = null) {
  const helperArgs = [SAFE_FS_HELPER, 'held', command, runId];
  const stdio = ['ignore', 'pipe', 'pipe', rootHeld.descriptor, workHeld.descriptor];
  if (historyHeld) {
    helperArgs.push('with-history');
    stdio.push(historyHeld.descriptor);
  } else {
    stdio.push('ignore');
  }
  helperArgs.push(...args);
  try {
    childProcess.execFileSync('python3', helperArgs, { stdio });
  } catch (error) {
    fail('safe_fs_error', `${command} failed: ${(error.stderr || error.message).toString().trim()}`);
  }
}

function inspectWorkDirectory(workRoot, ownRunId) {
  for (const entry of fs.readdirSync(workRoot).sort()) {
    const target = path.join(workRoot, entry);
    const stat = fs.lstatSync(target);
    if (stat.isSymbolicLink()) fail('symlink_fail_closed', `.work entry must not be a symlink: ${entry}`);
    if (!stat.isDirectory()) fail('unknown_entry_fail_closed', `.work entry must be a directory: ${entry}`);
    if (entry !== ownRunId && entry !== '.delivery-lock') {
      fail('stale_work_fail_closed', `unrelated stale work requires audit: ${entry}`);
    }
  }
}

function inspectHistoryDirectory(historyRoot) {
  for (const entry of fs.readdirSync(historyRoot).sort()) {
    const target = path.join(historyRoot, entry);
    const stat = fs.lstatSync(target);
    if (stat.isSymbolicLink() || !stat.isDirectory() || !HISTORY_NAME.test(entry)) {
      fail('history_fail_closed', `history entry is unsafe or unknown: ${entry}`);
    }
  }
}

function nextHistorySequence(root) {
  const historyRoot = path.join(root, 'history');
  if (!fs.existsSync(historyRoot)) return '001';
  inspectHistoryDirectory(historyRoot);
  const values = fs.readdirSync(historyRoot).map((name) => Number(name));
  const next = (values.length ? Math.max(...values) : 0) + 1;
  return String(next).padStart(3, '0');
}

function removeOwnedTree(target, boundary) {
  if (!fs.existsSync(target)) return;
  const relative = path.relative(boundary, target);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) fail('owned_cleanup_boundary_error', `refusing cleanup outside owned boundary: ${target}`);
  const stat = fs.lstatSync(target);
  if (stat.isSymbolicLink() || stat.isFile()) {
    fs.unlinkSync(target);
    return;
  }
  if (!stat.isDirectory()) fail('owned_cleanup_type_error', `refusing cleanup of special object: ${target}`);
  for (const entry of fs.readdirSync(target)) removeOwnedTree(path.join(target, entry), boundary);
  fs.rmdirSync(target);
}

function removeDirectoryIfEmpty(target) {
  if (!fs.existsSync(target)) return;
  const stat = fs.lstatSync(target);
  if (!stat.isDirectory() || stat.isSymbolicLink()) return;
  if (fs.readdirSync(target).length === 0) fs.rmdirSync(target);
}

function makeFaultHook(fault) {
  let fired = false;
  return (point) => {
    const abortFile = process.env.TDPKG_DELIVERY_ABORT_FILE || '';
    if (abortFile && fs.existsSync(abortFile)) fail('handled_signal', `publication cancelled at ${point}`);
    if (process.env.TDPKG_DELIVERY_PAUSE_AT === point) {
      const readyFile = process.env.TDPKG_DELIVERY_READY_FILE || '';
      if (readyFile) fs.writeFileSync(readyFile, point);
      const delay = Number(process.env.TDPKG_DELIVERY_PAUSE_MS || '500');
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, delay);
      if (abortFile && fs.existsSync(abortFile)) fail('handled_signal', `publication cancelled at ${point}`);
    }
    if (!fired && fault === point) {
      fired = true;
      fail('injected_fault', point);
    }
  };
}

function publishBundle({ root, runId, candidateRoot, packageModel, fault = '' }) {
  assertRuntimeCapabilities();
  validateComponent(runId, 'run id');
  const expectedNames = validateExpectedNames(packageModel);
  const absoluteRoot = path.resolve(root);
  const absoluteCandidate = path.resolve(candidateRoot);
  const expectedCandidate = path.join(absoluteRoot, '.work', runId, 'candidate');
  if (absoluteCandidate !== expectedCandidate) fail('candidate_boundary_error', 'candidate root must be .work/<run-id>/candidate under delivery root');
  const rootHeld = openHeldDirectory(absoluteRoot, 'delivery root');
  const workRoot = path.join(absoluteRoot, '.work');
  const runRoot = path.join(workRoot, runId);
  const rollbackRoot = path.join(runRoot, 'rollback');
  const lockRoot = path.join(workRoot, '.delivery-lock');
  const hook = makeFaultHook(fault);
  let candidateBytes;
  let lockHeld = false;
  let workHeld = null;
  let historyHeld = null;
  let historyRoot = '';
  let historySequence = '';
  let oldNames = [];
  let publicationStarted = false;
  let committed = false;

  const rollback = () => {
    if (!publicationStarted) return;
    safeFsHeld(
      'rollback',
      rootHeld,
      workHeld,
      runId,
      [JSON.stringify(expectedNames), JSON.stringify(oldNames), historySequence],
      historyHeld,
    );
  };

  try {
    validateCandidate(absoluteCandidate, expectedNames);
    candidateBytes = new Map(expectedNames.map((name) => [name, fs.readFileSync(path.join(absoluteCandidate, name))]));
    fs.mkdirSync(workRoot, { recursive: true });
    workHeld = openHeldDirectory(workRoot, 'delivery work root');
    hook('after_candidate_validation');
    try {
      safeFsHeld('acquire-lock', rootHeld, workHeld, runId);
      lockHeld = true;
    } catch (error) {
      if (error.code === 'EEXIST') fail('lock_conflict', 'another delivery transaction owns the same-root lock');
      throw error;
    }
    assertHeldDirectory(rootHeld);
    oldNames = discoverCurrent(absoluteRoot, packageModel, runId);
    const identical = pathSetEqual(oldNames, expectedNames)
      && expectedNames.every((name) => filesEqual(path.join(absoluteRoot, name), path.join(absoluteCandidate, name)));
    if (identical) {
      committed = true;
      return { status: 'identical', historySequence: null, expectedNames };
    }

    safeFsHeld('prepare-rollback', rootHeld, workHeld, runId);
    for (const name of oldNames) safeFsHeld('snapshot', rootHeld, workHeld, runId, [name]);
    publicationStarted = true;
    if (oldNames.length) {
      historySequence = nextHistorySequence(absoluteRoot);
      safeFsHeld('ensure-history', rootHeld, workHeld, runId);
      const parent = path.join(absoluteRoot, 'history');
      historyHeld = openHeldDirectory(parent, 'delivery history root');
      historyRoot = path.join(parent, historySequence);
      safeFsHeld('reserve-history', rootHeld, workHeld, runId, [historySequence], historyHeld);
      hook('after_history_reservation');
      for (const name of oldNames) safeFsHeld('archive', rootHeld, workHeld, runId, [historySequence, name], historyHeld);
      hook('after_archive_snapshot');
    }

    let publishedCount = 0;
    const middleIndex = Math.ceil(expectedNames.length / 2);
    for (const name of expectedNames) {
      assertHeldDirectory(rootHeld);
      const source = path.join(absoluteCandidate, name);
      const target = path.join(absoluteRoot, name);
      safeFsHeld('move', rootHeld, workHeld, runId, [name], historyHeld);
      publishedCount += 1;
      if (publishedCount === 1) hook('after_publish_file_1');
      if (publishedCount === middleIndex) hook('after_publish_middle_file');
    }
    for (const name of oldNames) {
      if (!expectedNames.includes(name)) safeFsHeld('unlink-root', rootHeld, workHeld, runId, [name], historyHeld);
    }
    fsyncDirectory(absoluteRoot);
    hook('before_post_publish_verify');
    const observed = discoverCurrent(absoluteRoot, packageModel, runId);
    if (!pathSetEqual(observed, expectedNames)) fail('post_publish_path_set_mismatch', 'published current set differs from expected_public_filenames');
    for (const name of expectedNames) {
      const rollbackCandidate = path.join(absoluteRoot, name);
      assertRegular(rollbackCandidate, `published ${name}`);
      if (!fs.readFileSync(rollbackCandidate).equals(candidateBytes.get(name))) {
        fail('post_publish_bytes_mismatch', `published bytes differ from validated candidate: ${name}`);
      }
    }
    hook('before_work_cleanup');
    committed = true;
    return { status: 'published', historySequence: historySequence || null, expectedNames };
  } catch (error) {
    if (!committed) rollback();
    throw error;
  } finally {
    try {
      if (workHeld) safeFsHeld('cleanup', rootHeld, workHeld, runId, [], historyHeld);
    } finally {
      if (historyHeld) fs.closeSync(historyHeld.descriptor);
      if (workHeld) fs.closeSync(workHeld.descriptor);
      fs.closeSync(rootHeld.descriptor);
    }
  }
}

function runInternal(root, runId, candidateRoot, modelPath) {
  const packageModel = JSON.parse(fs.readFileSync(modelPath, 'utf8'));
  try {
    const result = publishBundle({ root, runId, candidateRoot, packageModel, fault: process.env.TDPKG_DELIVERY_FAULT || '' });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    console.error(`teaching-design-package delivery: ${error.message}`);
    process.exitCode = 1;
  }
}

function supervisePublish(root, runId, candidateRoot, modelPath) {
  const abortFile = path.join(path.resolve(root), '.work', runId, '.delivery-abort');
  const child = childProcess.spawn(
    process.execPath,
    [__filename, 'publish-internal', root, runId, candidateRoot, modelPath],
    { stdio: 'inherit', env: { ...process.env, TDPKG_DELIVERY_ABORT_FILE: abortFile } },
  );
  let interrupted = '';
  const cancel = (signal) => {
    interrupted = interrupted || signal;
    try {
      fs.writeFileSync(abortFile, signal, { flag: 'wx' });
    } catch (error) {
      if (error.code !== 'EEXIST') child.kill(signal);
    }
  };
  process.on('SIGINT', () => cancel('SIGINT'));
  process.on('SIGTERM', () => cancel('SIGTERM'));
  child.on('error', (error) => {
    console.error(`teaching-design-package delivery: cannot start transaction worker: ${error.message}`);
    process.exitCode = 1;
  });
  child.on('close', (code) => {
    process.exitCode = interrupted === 'SIGINT' ? 130 : interrupted === 'SIGTERM' ? 143 : (code || 0);
  });
}

function main() {
  const [command, root, runId, candidateRoot, modelPath] = process.argv.slice(2);
  if (command === 'cleanup' && root && runId) {
    validateComponent(runId, 'run id');
    safeFs('cleanup', path.resolve(root), runId);
    return;
  }
  if (!['publish', 'publish-internal'].includes(command) || !root || !runId || !candidateRoot || !modelPath) {
    console.error('Usage: delivery-transaction.js publish <root> <run-id> <candidate-root> <model.json> | cleanup <root> <run-id>');
    process.exit(2);
  }
  if (command === 'publish-internal') runInternal(root, runId, candidateRoot, modelPath);
  else supervisePublish(root, runId, candidateRoot, modelPath);
}

module.exports = {
  DeliveryError,
  nextHistorySequence,
  pathSetEqual,
  publishBundle,
  validateExpectedNames,
};

if (require.main === module) main();
