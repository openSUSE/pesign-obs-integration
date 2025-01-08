 # Signing kernel modules and EFI binaries in the Open Build Service

RPM packages that need to sign files during build should add the following lines
to the specfile

```
# needssslcertforbuild
export BRP_PESIGN_FILES='pattern...'
BuildRequires: pesign-obs-integration
```

BRP_PESIGN_PACKAGES can optionally be defined to restrict repacking to a subset
of packages of choice.

Debian packages need to add the following line to the Source stanza in the
debian/control file, which will add "Obs: needssslcertforbuild" to the generated
.dsc file:

```XS-Obs: needssslcertforbuild```

The "# needssslcertforbuild" comment tells the buildservice to store the
signing certificate in %_sourcedir/_projectcert.crt. At the end of the
install phase, the brp-99-pesign script computes hashes of all
files matching the patterns in $BRP_PESIGN_FILES. The sha256 hashes are stored
in %_topdir/OTHER/%name.cpio.rsasign, plus the script places a
pesign-repackage.spec file there. When the first rpmbuild finishes, the
buildservice sends the cpio archive to the signing server, which returns
a rsasigned.cpio archive with RSA signatures of the sha256 hashes.

The pesign-repackage.spec takes the original RPMs, unpacks them and
appends the signatures to the files. It then uses the
pesign-gen-repackage-spec script to generate another specfile, which
builds new RPMs with signed files. The supported file types are:

- *.ko
  - Signature appended to the module
- efi binaries
  - Signature embedded in a header. If a HMAC checksum named
    .$file.hmac exists, it is regenerated

Debian packages can use the dh-signobs debhelper to automate signing and
repacking. Build-depend on dh-signobs and add --with signobs to the dh line
in debian/rules to use the fully automated helper.
Consult the dh_signobs manpage for more information.

## Options

### Kernel Module Compression
When BRP_PESIGN_COMPRESS_MODULE is passed, the script tries to compress the
kernel modules at the repackaging phase. Currently xz, gzip and zstd format is supported.
For enable the compression feature, put the following along with
BRP_PESIGN_FILES setup:

```export BRP_PESIGN_COMPRESS_MODULE="xz"```

### Dependency Generation
If you need macros within the pesign-repackage specfile to adjust [dependency generation](https://rpm-software-management.github.io/rpm/manual/dependency_generators.html)
, then place these in a source file called pesign-spec-macros, this will subseqently be loaded.

Example of pesign-spec-macros:

```%__kmp_supplements %_sourcedir/my-find-supplements %_sourcedir/pci_ids-%{version}```

To save creating duplicate copies of macros, load this file from your existing spec file by using the following:

```%{load:%{_sourcedir}/pesign-spec-macros}```

If you need some source files such as dependency generation scripts then place the names of these source files in a source file called pesign-copy-sources.

Example of pesign-copy-sources:
```
my-find-supplements
pci_ids-%{version}
```
