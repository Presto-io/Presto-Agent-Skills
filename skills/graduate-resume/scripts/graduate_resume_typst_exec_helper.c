/*
 * Root-owned Darwin execution backend for graduate-resume Typst snapshots.
 *
 * Installed setuid root only by install_typst_exec_helper.sh.  The protocol is
 * intentionally small: --probe, or --fd N --sha256 <64 hex> --proof <nonce>
 * -- <typst argv>.  Caller uid/gid switches are never accepted.
 */
#include <CommonCrypto/CommonDigest.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/acl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#define MAX_BYTES (128U * 1024U * 1024U)
#define MAX_ARGS 64
#define MAX_ARG_BYTES 16384
#define COPY_NAME "/usr/local/libexec/.presto-typst-copy.XXXXXX"

static int fail(void) { fputs("TYPST_RUNTIME_INVALID\n", stderr); return 125; }

static int hex_digest(const unsigned char digest[CC_SHA256_DIGEST_LENGTH], const char *hex) {
  static const char alphabet[] = "0123456789abcdef";
  if (strlen(hex) != 64) return 0;
  for (int i = 0; i < CC_SHA256_DIGEST_LENGTH; ++i)
    if (hex[2*i] != alphabet[digest[i] >> 4] || hex[2*i+1] != alphabet[digest[i] & 15]) return 0;
  return 1;
}

/* A non-trivial extended ACL is deliberately rejected.  This is stricter than
 * mode bits and avoids guessing ACL semantics from a privileged effective uid. */
static int secure_node(const char *path) {
  struct stat st;
  if (lstat(path, &st) != 0 || (!S_ISREG(st.st_mode) && !S_ISDIR(st.st_mode))) return 0;
  if (st.st_uid != 0 || st.st_gid != 0 || (st.st_mode & 022) != 0) return 0;
  acl_t acl = acl_get_file(path, ACL_TYPE_EXTENDED);
  if (acl == NULL) return 0;
  acl_entry_t entry; int id = ACL_FIRST_ENTRY, count = 0;
  while (acl_get_entry(acl, id, &entry) == 0) { ++count; id = ACL_NEXT_ENTRY; }
  acl_free(acl);
  return count == 0;
}

static int secure_domain(void) {
  return secure_node("/usr") && secure_node("/usr/local") &&
         secure_node("/usr/local/libexec") &&
         secure_node("/usr/local/libexec/presto-graduate-resume-typst-exec");
}

static int copy_verified(int source, const char *expected, char output[PATH_MAX]) {
  struct stat st;
  if (fstat(source, &st) || !S_ISREG(st.st_mode) || st.st_size <= 0 || st.st_size > MAX_BYTES) return 0;
  if (snprintf(output, PATH_MAX, "%s", COPY_NAME) >= PATH_MAX) return 0;
  int out = mkstemp(output);
  if (out < 0 || fchmod(out, 0500) || fchown(out, 0, 0)) { if (out >= 0) close(out); unlink(output); return 0; }
  CC_SHA256_CTX ctx; CC_SHA256_Init(&ctx); unsigned char buffer[65536]; ssize_t n; size_t total = 0;
  while ((n = read(source, buffer, sizeof buffer)) > 0) {
    total += (size_t)n; if (total > MAX_BYTES || write(out, buffer, (size_t)n) != n) { close(out); unlink(output); return 0; }
    CC_SHA256_Update(&ctx, buffer, (CC_LONG)n);
  }
  unsigned char digest[CC_SHA256_DIGEST_LENGTH]; CC_SHA256_Final(digest, &ctx);
  if (n < 0 || !hex_digest(digest, expected) || fsync(out) || close(out)) { unlink(output); return 0; }
  return 1;
}

int main(int argc, char **argv) {
  if (argc == 2 && strcmp(argv[1], "--probe") == 0) {
    if (!secure_domain()) return fail();
    fputs("PRESTO_TYPST_HELPER_V1\n", stdout); return 0;
  }
  if (argc < 9 || strcmp(argv[1], "--fd") || strcmp(argv[3], "--sha256") ||
      strcmp(argv[5], "--proof") || strcmp(argv[7], "--") || argc - 8 > MAX_ARGS ||
      strlen(argv[2]) > 10 || strlen(argv[4]) != 64 || strlen(argv[6]) != 64) return fail();
  for (int i = 8, bytes = 0; i < argc; ++i) { bytes += (int)strlen(argv[i]); if (bytes > MAX_ARG_BYTES) return fail(); }
  if (!secure_domain()) return fail();
  char *end = NULL; long value = strtol(argv[2], &end, 10);
  if (!end || *end || value < 3 || value > INT_MAX) return fail();
  uid_t real_uid = getuid(); gid_t real_gid = getgid();
  if (real_uid == 0 || real_gid == 0) return fail();
  char copy[PATH_MAX]; if (!copy_verified((int)value, argv[4], copy)) return fail();
  pid_t child = fork(); if (child < 0) { unlink(copy); return fail(); }
  if (child == 0) {
    if (setgroups(0, NULL) || setgid(real_gid) || setuid(real_uid) || geteuid() != real_uid || getegid() != real_gid) _exit(125);
    dprintf(STDERR_FILENO, "PRESTO_TYPST_HELPER_BACKEND:%s\n", argv[6]);
    execv(copy, &argv[8]); _exit(125);
  }
  int status = 125; if (waitpid(child, &status, 0) < 0 || unlink(copy)) return fail();
  if (WIFEXITED(status)) return WEXITSTATUS(status);
  return fail();
}
