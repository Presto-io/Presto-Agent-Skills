#!/bin/sh
set -eu
umask 077

HELPER=/usr/local/libexec/presto-graduate-resume-typst-exec
DOMAIN=/usr/local/libexec
CC=/usr/bin/cc
SOURCE=${1:-}
EXPECTED=${2:-}

die() { printf '%s\n' 'TYPST_RUNTIME_INVALID: helper was not replaced.' >&2; exit 1; }
[ "$(/usr/bin/id -u)" -eq 0 ] || die
[ -n "$SOURCE" ] && [ -n "$EXPECTED" ] || die
[ "${#EXPECTED}" -eq 64 ] && printf '%s' "$EXPECTED" | /usr/bin/grep -Eq '^[0-9a-f]{64}$' || die
[ -f "$SOURCE" ] && [ ! -L "$SOURCE" ] || die
[ -x "$CC" ] && [ -x /usr/bin/codesign ] || die
/usr/bin/codesign -v "$CC" >/dev/null 2>&1 || die

STAGE=$(/usr/bin/mktemp -d /private/var/tmp/presto-typst-helper.XXXXXX) || die
BACKUP=$DOMAIN/.presto-graduate-resume-typst-exec.previous
NEW=$DOMAIN/.presto-graduate-resume-typst-exec.new
cleanup() {
  /bin/rm -rf "$STAGE"
  [ ! -e "$NEW" ] || /bin/rm -f "$NEW"
}
trap cleanup EXIT HUP INT TERM
/usr/sbin/chown root:wheel "$STAGE" && /bin/chmod 0700 "$STAGE" || die

# The reviewed source is consumed once from fd 3.  The working-tree name is
# never read after this point.
exec 3<"$SOURCE"
GOT=$(/bin/cat /dev/fd/3 | /usr/bin/tee "$STAGE/helper.c" | /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}') || die
[ "$GOT" = "$EXPECTED" ] || die
/usr/sbin/chown root:wheel "$STAGE/helper.c" && /bin/chmod 0400 "$STAGE/helper.c" || die

/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C "$CC" -Wall -Wextra -Werror -O2 \
  -o "$STAGE/helper" "$STAGE/helper.c" || die
/usr/sbin/chown root:wheel "$STAGE/helper" && /bin/chmod 4755 "$STAGE/helper" || die

# Preserve a previously working helper until the new, atomically installed
# executable proves its full root:wheel/mode/ACL domain through --probe.
[ ! -e "$BACKUP" ] || die
if [ -e "$HELPER" ]; then /bin/mv "$HELPER" "$BACKUP" || die; fi
if ! /bin/mv "$STAGE/helper" "$NEW" || ! /usr/sbin/chown root:wheel "$NEW" ||
  ! /bin/chmod 4755 "$NEW" || ! /bin/mv "$NEW" "$HELPER" || ! "$HELPER" --probe >/dev/null; then
  /bin/rm -f "$HELPER" "$NEW"
  [ ! -e "$BACKUP" ] || /bin/mv "$BACKUP" "$HELPER"
  die
fi
[ ! -e "$BACKUP" ] || /bin/rm -f "$BACKUP"
printf '%s\n' 'Installed presto graduate-resume Typst execution helper.'
