/*
 * Root-owned Darwin execution backend for graduate-resume Typst snapshots.
 * Installed only by install_typst_exec_helper.sh; this program never accepts
 * caller-controlled credentials or executable paths.
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
  for (int index = 0; index < CC_SHA256_DIGEST_LENGTH; ++index)
    if (hex[2 * index] != alphabet[digest[index] >> 4] ||
        hex[2 * index + 1] != alphabet[digest[index] & 15]) return 0;
  return 1;
}

/* Darwin reports a missing extended ACL as ENOENT. Any present, unreadable, or
 * unrecognised ACL fails closed rather than guessing its effective permissions. */
static int secure_node(const char *path, int helper) {
  struct stat st;
  if (lstat(path, &st) != 0 || (!S_ISREG(st.st_mode) && !S_ISDIR(st.st_mode))) return 0;
  if (st.st_uid != 0 || st.st_gid != 0 || (st.st_mode & 022) != 0) return 0;
  if (helper && (st.st_mode & 07777) != 04755) return 0;
  errno = 0;
  acl_t acl = acl_get_file(path, ACL_TYPE_EXTENDED);
  if (acl == NULL) return errno == ENOENT;
  acl_entry_t entry;
  int entry_id = ACL_FIRST_ENTRY;
  if (acl_get_entry(acl, entry_id, &entry) == 0) { acl_free(acl); return 0; }
  acl_free(acl);
  return 1;
}

static int secure_domain(void) {
  return secure_node("/usr", 0) && secure_node("/usr/local", 0) &&
         secure_node("/usr/local/libexec", 0) &&
         secure_node("/usr/local/libexec/presto-graduate-resume-typst-exec", 1);
}

static int copy_verified(int source, const char *expected, char output[PATH_MAX]) {
  struct stat st;
  if (fstat(source, &st) != 0 || !S_ISREG(st.st_mode) || st.st_size <= 0 || st.st_size > MAX_BYTES) return 0;
  if (lseek(source, 0, SEEK_SET) < 0 || snprintf(output, PATH_MAX, "%s", COPY_NAME) >= PATH_MAX) return 0;
  int output_fd = mkstemp(output);
  if (output_fd < 0 || fchmod(output_fd, 0555) != 0 || fchown(output_fd, 0, 0) != 0) {
    if (output_fd >= 0) close(output_fd); unlink(output); return 0;
  }
  CC_SHA256_CTX context;
  CC_SHA256_Init(&context);
  unsigned char buffer[65536];
  ssize_t count;
  size_t total = 0;
  while ((count = read(source, buffer, sizeof buffer)) > 0) {
    total += (size_t)count;
    if (total > MAX_BYTES || write(output_fd, buffer, (size_t)count) != count) {
      close(output_fd); unlink(output); return 0;
    }
    CC_SHA256_Update(&context, buffer, (CC_LONG)count);
  }
  unsigned char digest[CC_SHA256_DIGEST_LENGTH];
  CC_SHA256_Final(digest, &context);
  if (count < 0 || !hex_digest(digest, expected) || fsync(output_fd) != 0 || close(output_fd) != 0) {
    unlink(output); return 0;
  }
  return 1;
}

int main(int argc, char **argv) {
  if (argc == 2 && strcmp(argv[1], "--probe") == 0) {
    if (!secure_domain()) return fail();
    fputs("PRESTO_TYPST_HELPER_V1\n", stdout);
    return 0;
  }
  if (argc < 9 || strcmp(argv[1], "--fd") != 0 || strcmp(argv[3], "--sha256") != 0 ||
      strcmp(argv[5], "--proof") != 0 || strcmp(argv[7], "--") != 0 || argc - 8 > MAX_ARGS ||
      strlen(argv[2]) > 10 || strlen(argv[4]) != 64 || strlen(argv[6]) != 64) return fail();
  for (int index = 8, bytes = 0; index < argc; ++index) {
    bytes += (int)strlen(argv[index]); if (bytes > MAX_ARG_BYTES) return fail();
  }
  if (!secure_domain()) return fail();
  char *end = NULL;
  long descriptor = strtol(argv[2], &end, 10);
  if (end == NULL || *end != '\0' || descriptor < 3 || descriptor > INT_MAX) return fail();
  uid_t real_uid = getuid();
  gid_t real_gid = getgid();
  if (real_uid == 0 || real_gid == 0) return fail();
  char copy[PATH_MAX];
  if (!copy_verified((int)descriptor, argv[4], copy)) return fail();
  pid_t child = fork();
  if (child < 0) { unlink(copy); return fail(); }
  if (child == 0) {
    if (setgroups(0, NULL) != 0 || setgid(real_gid) != 0 || setuid(real_uid) != 0 ||
        geteuid() != real_uid || getegid() != real_gid) _exit(125);
    dprintf(STDERR_FILENO, "PRESTO_TYPST_HELPER_BACKEND:%s\n", argv[6]);
    char *exec_argv[MAX_ARGS + 2];
    exec_argv[0] = copy;
    for (int index = 8; index < argc; ++index) exec_argv[index - 7] = argv[index];
    exec_argv[argc - 7] = NULL;
    execv(copy, exec_argv);
    _exit(125);
  }
  int status = 125;
  if (waitpid(child, &status, 0) < 0 || unlink(copy) != 0) return fail();
  if (WIFEXITED(status)) return WEXITSTATUS(status);
  return fail();
}
