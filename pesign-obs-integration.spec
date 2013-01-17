#
# spec file for package pesign-obs-integration (Version 1.0)
#
# Copyright (c) 2012 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild
Name:           pesign-obs-integration
Summary:        Macros and scripts to sign the kernel and bootloader
Version:        1.0
Release:        1
BuildArch:      noarch
License:        GPL v2 only
Group:          Development/Tools/Other
URL:            http://en.opensuse.org/openSUSE:UEFI_Image_File_Sign_Tools
Source1:        macros.pesign-obs
Source2:        pesign-repackage.spec.in
Source3:        pesign-gen-repackage-spec
Source4:        pesign-install-post
Source5:        COPYING
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%description
This package provides scripts and rpm macros to automate signing of the
boot loader, kernel and kernel modules in the openSUSE Buildservice.

%prep
%setup -cT
cp %_sourcedir/COPYING .

%build

%install

mkdir -p %buildroot/usr/lib/rpm %buildroot/etc/rpm
install -m644 %_sourcedir/macros.pesign-obs %buildroot/etc/rpm
install  %_sourcedir/{pesign-gen-repackage-spec,pesign-install-post} %buildroot/usr/lib/rpm
install -m644 %_sourcedir/pesign-repackage.spec.in %buildroot/usr/lib/rpm

%files
%defattr(-,root,root)
%doc COPYING
/usr/lib/rpm/*
/etc/rpm/*

%changelog

