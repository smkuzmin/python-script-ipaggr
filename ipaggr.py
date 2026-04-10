#!/usr/bin/env python3

r"""
IPAggr v1.18 - IPv4 Aggregator

Merges overlapping and adjacent IPv4 addresses and subnets into the minimum number
of networks, preserving and merging comments from the original list.

FEATURES:
  - Rounds input networks to the specified CIDR prefix before aggregation
  - Supports both CIDR prefixes and subnet masks (e.g., 192.168.1.0/24 or 192.168.1.0/255.255.255.0)
  - Skips invalid lines without errors (empty lines, comments, text)
  - Preserves and merges comments from input lines
  - Automatically treats individual IP addresses as /32 networks
  - Outputs single addresses without /32 prefix
  - Automatically sorts output in ascending order
  - Uses fixed-width formatting: "%-18s # %s"

INPUT FORMAT:
  192.168.1.1                  Single IP address
  192.168.1.0/24               Network with CIDR prefix
  192.168.1.0/255.255.255.0    Network with subnet mask

OUTPUT FORMAT:
  192.168.1.0/24     # comment1, comment2, ...
  192.168.1.1        # comment

USAGE:
  cat infile.lst | ipaggr OPTIONS
  ipaggr OPTIONS < infile.lst > outfile.lst

OPTIONS:
  -p, --prefix=CIDR_PREFIX    Aggregation with rounding to the specified CIDR prefix
"""

import sys
import ipaddress
from collections import defaultdict

def parse_line(line):
    # Разбираем строку с опциональным комментарием. Возвращаем (сеть, список_комментариев) или (None, [])
    line = line.strip()
    if not line or line.startswith('#'):
        return None, []

    # Разделяем по '#' для отделения IP/CIDR от комментария
    parts = line.split('#', 1)
    ip_part = parts[0].strip()
    comment_str = parts[1].strip() if len(parts) > 1 else ''

    if not ip_part:
        return None, []

    # Обрабатываем одиночный IP как /32
    if '/' not in ip_part:
        ip_part += '/32'

    try:
        network = ipaddress.ip_network(ip_part, strict=False)
        # Разбиваем строку комментариев по запятым, убираем пробелы и пустые элементы
        comments = [c.strip() for c in comment_str.split(',') if c.strip()]
        return network, comments
    except ValueError:
        return None, []

def main():
    # Парсинг опции -p / --prefix
    target_prefix = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-p':
            if i + 1 < len(args):
                i += 1
                val = args[i]
                try:
                    target_prefix = int(val)
                    if not (0 <= target_prefix <= 32): raise ValueError
                except ValueError:
                    print(f"Error: Invalid prefix: {val}. Must be 0-32.", file=sys.stderr)
                    sys.exit(1)
            else:
                print("Error: Option -p requires a value.", file=sys.stderr)
                sys.exit(1)
        elif arg.startswith('--prefix='):
            val = arg.split('=', 1)[1]
            if val:
                try:
                    target_prefix = int(val)
                    if not (0 <= target_prefix <= 32): raise ValueError
                except ValueError:
                    print(f"Error: Invalid prefix: {val}. Must be 0-32.", file=sys.stderr)
                    sys.exit(1)
            else:
                print("Error: Option --prefix requires a value.", file=sys.stderr)
                sys.exit(1)
        elif arg in ('-h', '--help'):
            print(__doc__, file=sys.stderr)
            sys.exit(0)
        else:
            print(f"Error: Invalid option: {arg}", file=sys.stderr)
            sys.exit(1)
        i += 1

    # Храним сети с их комментариями: {сеть: [список комментариев]}
    net_comments = defaultdict(list)

    for line in sys.stdin:
        network, comments = parse_line(line)
        if network:
            # Округляем входящую сеть до заданного префикса, если он строже
            if target_prefix is not None and network.prefixlen > target_prefix:
                network = network.supernet(new_prefix=target_prefix)
            net_comments[network].extend(comments)

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

        # Удаляем повторяющиеся комментарии после сортировки
        comments = list(dict.fromkeys(comments))

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
