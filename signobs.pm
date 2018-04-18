#!/usr/bin/perl
# SPDX-License-Identifier: GPL-2.0+
# Copyright: 2018 Luca Boccassi <bluca@debian.org>

use warnings;
use strict;
use Debian::Debhelper::Dh_Lib;

insert_before('dh_auto_install', 'dh_signobs_unpack');
insert_after('dh_install', 'dh_signobs_pack');

1
