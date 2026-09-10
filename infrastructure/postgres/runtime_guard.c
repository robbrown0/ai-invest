/* Fixed image preload: enforce protections before PostgreSQL/Python read keys.
 * No key access, environment-selected paths, diagnostics or secret output.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>
#ifdef GUARD_PROBE
#include <signal.h>
#include <sys/wait.h>
#endif

static void refuse(void) { _exit(78); }
static void contents(const char *path, char *buffer, size_t length) {
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) refuse();
    ssize_t n = read(fd, buffer, length - 1);
    if (n <= 0 || (size_t)n == length - 1) refuse();
    buffer[n] = 0;
    close(fd);
}
static uint64_t parse(char **cursor) {
    char *p = *cursor;
    uint64_t value = 0;
    if (*p < '0' || *p > '9') refuse();
    while (*p >= '0' && *p <= '9') {
        unsigned digit = (unsigned)(*p++ - '0');
        if (value > (UINT64_MAX - digit) / 10) refuse();
        value = value * 10 + digit;
    }
    *cursor = p;
    return value;
}
static uint64_t number(const char *path) {
    char b[80], *end = b;
    contents(path, b, sizeof(b));
    uint64_t value = parse(&end);
    if (strcmp(end, "\n") != 0) refuse();
    return value;
}
int ai_guard_status(void) {
    struct rlimit core;
    return prctl(PR_GET_DUMPABLE) == 0 && getrlimit(RLIMIT_CORE, &core) == 0
        && core.rlim_cur == 0 && core.rlim_max == 0;
}
__attribute__((constructor)) static void protect(void) {
    struct rlimit core = {0, 0};
    char cpu[80], *cursor = cpu;
    uid_t uid = getuid();
    if (uid != geteuid() || (uid != 26 && uid != 10001 && uid != 10002)) refuse();
    if (setrlimit(RLIMIT_CORE, &core) != 0 || prctl(PR_SET_DUMPABLE, 0) != 0
        || prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0 || !ai_guard_status()) refuse();
    uint64_t memory = number("/sys/fs/cgroup/memory.max");
    uint64_t pids = number("/sys/fs/cgroup/pids.max");
    if (memory == 0 || memory > UINT64_C(2147483648) || pids == 0 || pids > 64
        || number("/sys/fs/cgroup/memory.swap.max") != 0
        || number("/sys/fs/cgroup/memory.swap.current") != 0) refuse();
    contents("/sys/fs/cgroup/cpu.max", cpu, sizeof(cpu));
    uint64_t quota = parse(&cursor);
    if (*cursor++ != ' ') refuse();
    uint64_t period = parse(&cursor);
    if (strcmp(cursor, "\n") != 0 || !quota || !period || quota > period) refuse();
    umask(0077);
}
#ifdef GUARD_PROBE
int main(void) {
    if (!ai_guard_status()) return 1;
    pid_t pid = fork();
    if (pid < 0) return 1;
    if (pid == 0) {
        if (!ai_guard_status()) _exit(1);
        raise(SIGABRT);
        _exit(1);
    }
    int status;
    if (waitpid(pid, &status, 0) != pid || !WIFSIGNALED(status)
        || WTERMSIG(status) != SIGABRT || WCOREDUMP(status)) return 1;
    puts("{\"native_guard\":\"PASS\",\"child_nondumpable_crash\":\"PASS\"}");
    return 0;
}
#endif
