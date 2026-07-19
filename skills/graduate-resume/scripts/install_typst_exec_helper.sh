#!/bin/sh
# Explicit administrator-only installer.  It never invokes sudo itself.
set -eu
umask 077

HELPER=/usr/local/libexec/presto-graduate-resume-typst-exec
DOMAIN=/usr/local/libexec
CC=/usr/bin/cc
SOURCE=${1:-}
EXPECTED=${2:-}

die() { printf '%s\n' 'TYPST_RUNTIME_INVALID: helper was not replaced.' >&2; exit 1; }
[ "$(id -u)" -eq 0 ] || die
[ -n "$SOURCE" ] && [ -n "$EXPECTED" ] || die
[ "${#EXPECTED}" -eq 64 ] || die
[ -f "$SOURCE" ] && [ ! -L "$SOURCE" ] || die
[ -x "$CC" ] && [ -x /usr/bin/codesign ] || die
/usr/bin/codesign -v "$CC" >/dev/null 2>&1 || die

# The source is opened once, hashed from that descriptor, then copied from the
# same descriptor into a root-only staging directory.  No later operation reads
# the working-tree path again.
STAGE=$(/usr/bin/mktemp -d /private/var/tmp/presto-typst-helper.XXXXXX) || die
cleanup() { /bin/rm -rf "$STAGE"; }
trap cleanup EXIT HUP INT TERM
/usr/sbin/chown root:wheel "$STAGE" && /bin/chmod 0700 "$STAGE" || die
exec 3<"$SOURCE"
# tee and shasum consume the single inherited descriptor stream together: the
# staged bytes and reviewed digest are therefore one frozen source snapshot.
GOT=$(/bin/cat /dev/fd/3 | /usr/bin/tee "$STAGE/helper.c" | /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}') || die
[ "$GOT" = "$EXPECTED" ] || die
/usr/sbin/chown root:wheel "$STAGE/helper.c" && /bin/chmod 0400 "$STAGE/helper.c" || die

# No caller compiler flags, PATH, loader settings, or locale are inherited.
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C "$CC" -Wall -Wextra -Werror -O2 \
  -o "$STAGE/helper" "$STAGE/helper.c" || die
/usr/sbin/chown root:wheel "$STAGE/helper" && /bin/chmod 4755 "$STAGE/helper" || die
[ ! -e "$HELPER" ] || /usr/bin/cmp -s "$STAGE/helper" "$HELPER" || true

# The installed helper's native --probe checks root:wheel, non-writable modes,
# every parent and Darwin extended ACL semantics using the real calling uid.
# Install into a root-owned staging name then atomically rename; failures above
# leave a pre-existing helper untouched.
/bin/mv "$STAGE/helper" "$DOMAIN/.presto-graduate-resume-typst-exec.new" || die
/usr/sbin/chown root:wheel "$DOMAIN/.presto-graduate-resume-typst-exec.new" || die
/bin/chmod 4755 "$DOMAIN/.presto-graduate-resume-typst-exec.new" || die
/bin/mv -f "$DOMAIN/.presto-graduate-resume-typst-exec.new" "$HELPER" || die
[ "$(/usr/bin/stat -f %OLp "$HELPER")" = 4755 ] || die
"$HELPER" --probe >/dev/null || die
printf '%s\n' 'Installed presto graduate-resume Typst execution helper.'
