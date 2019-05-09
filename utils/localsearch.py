#!/usr/bin/env python

import os
from multiprocessing import Pool
from utils.classes import local_breach_target
from utils.colors import colors as c


def local_to_targets(targets, local_results):
    for t in targets:
        for l in local_results:
            if l.email == t.email:
                t.data.append(
                    ("LOCALSEARCH", f"[{l.filepath}] Line {l.line}: {l.content}")
                )
    return targets


from itertools import takewhile, repeat


def raw_in_count(filename):
    c.info_news(c, "Identifying total line number...")
    f = open(filename, "rb")
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
    return sum(buf.count(b"\n") for buf in bufgen)


def worker(filepath, target_list):
    with open(filepath, "r") as fp:
        found_list = []
        size = os.stat(filepath).st_size
        c.info_news(
            c,
            "Searching for targets in {filepath} ({size} bytes)".format(
                filepath=filepath, size=size
            ),
        )
        for cnt, line in enumerate(fp):
            for t in target_list:
                if t in line:
                    found_list.append(local_breach_target(t, filepath, cnt, line))
                    c.good_news(c, f"Found occurrence [{filepath}] Line {cnt}: {line}")
    return found_list


def local_search(files_to_parse, target_list):
    pool = Pool()
    found_list = []
    for f in files_to_parse:
        async_results = pool.apply_async(worker, args=(f, target_list))
        found_list.extend(async_results.get())
    pool.close()
    pool.join()
    return found_list


import sys


def progress(count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", status))
    sys.stdout.write("\033[K")

sys.stdout.flush()


def local_search_single(file_to_parse, target_list):
    with open(file_to_parse, "r") as fp:
        found_list = []
        size = os.stat(file_to_parse).st_size
        lines_no = raw_in_count(file_to_parse)
        c.info_news(
            c,
            "Searching for targets in {file_to_parse} ({size} bytes, {lines_no} lines)".format(
                file_to_parse=file_to_parse, size=size, lines_no=lines_no
            ),
        )
        for cnt, line in enumerate(fp):
            lines_left = lines_no-cnt
            progress(cnt, lines_no, f"{cnt} lines checked - {lines_left} lines left")
            for t in target_list:
                if t in line:
                    found_list.append(local_breach_target(t, file_to_parse, cnt, line))
                    c.good_news(c, f"Found occurrence [{file_to_parse}] Line {cnt}: {line}")
    return found_list

