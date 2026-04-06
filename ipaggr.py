#!/usr/bin/env python3

r"""
IPAggr v1.15 - IPv4 Aggregator

Merges overlapping and adjacent IPv4 addresses and subnets into the minimum number
of networks, preserving and merging comments from the original list.

FEATURES:
  - Skips invalid lines without errors (empty lines, comments, text)
  - Automatically processes single IP addresses as /32
  - Outputs single addresses without /32 prefix
  - Automatic ascending sorting
  - Supports both CIDR prefixes and subnet masks (e.g., 192.168.1.0/24 or 192.168.1.0/255.255.255.0)
  - Preserves and merges comments from input lines
  - Fixed-width output format: "%-18s # %s"

INPUT FORMAT:
  192.168.1.1                  Single IP address
  192.168.1.0/24               Network with CIDR prefix
  192.168.1.0/255.255.255.0    Network with subnet mask

OUTPUT FORMAT:
  192.168.1.0/24     # comment1, comment2, ...
  192.168.1.1        # comment

USAGE:
  cat infile.lst | ipaggr
  ipaggr < infile.lst > outfile.lst
"""

import sys
import ipaddress
from collections import defaultdict

def parse_line(line):
    # Разбираем строку с опциональным комментарием. Возвращаем (сеть, комментарий) или (None, None)
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None

    # Разделяем по '#' для отделения IP/CIDR от комментария
    parts = line.split('#', 1)
    ip_part = parts[0].strip()
    comment = parts[1].strip() if len(parts) > 1 else ''

    if not ip_part:
        return None, None

    # Обрабатываем одиночный IP как /32
    if '/' not in ip_part:
        ip_part += '/32'

    try:
        network = ipaddress.ip_network(ip_part, strict=False)
        return network, comment
    except ValueError:
        return None, None

def main():
    # Храним сети с их комментариями: {сеть: [список комментариев]}
    net_comments = defaultdict(list)

    for line in sys.stdin:
        network, comment = parse_line(line)
        if network:
            net_comments[network].append(comment)

    if not net_comments:
        return

    # Агрегируем сети в минимальный набор
    collapsed = list(ipaddress.collapse_addresses(sorted(net_comments.keys())))

    # Для каждой агрегированной сети собираем комментарии от всех исходных сетей, которые в неё входят
    for agg_net in collapsed:
        comments = set()
        for orig_net, orig_comments in net_comments.items():
            # Проверяем, является ли исходная сеть подсетью агрегированной (или равна ей)
            if orig_net.subnet_of(agg_net):
                comments.update(orig_comments)

        # Фильтруем пустые комментарии и сортируем для консистентного вывода
        comments = sorted(c for c in comments if c)

        # Формируем строку IP/сети
        if agg_net.prefixlen == 32:
            ip_str = str(agg_net.network_address)
        else:
            ip_str = str(agg_net)

        # Вывод в фиксированном формате: "%-18s # %s"
        # Обрезаем завершающие пробелы после # если нет комментариев
        comment_str = ', '.join(comments)
        if comment_str:
            print(f"{ip_str:<18} # {comment_str}")
        else:
            print(f"{ip_str:<18} #")

# Точка входа
if __name__ == '__main__':
    # Показываем справку при вызове с -h или --help, или если запущен без перенаправления ввода
    if sys.stdin.isatty() or '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__, file=sys.stderr)
        sys.exit(0)

    # Обрабатываем прерывание без вывода ошибки
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
